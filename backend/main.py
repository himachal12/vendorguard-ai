from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import os
from dotenv import load_dotenv
from data_collector import collect_vendor_data
from ai_engine import analyze_vendor_risk, generate_alert_message
from fastapi.responses import Response
from pdf_generator import generate_vendor_pdf
from email_alerts import send_risk_alert
import csv
import io
from fastapi import UploadFile, File

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="VendorGuard AI", version="1.0.0")

# Allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Database Setup ──────────────────────────────────────────
def init_db():
    """Create database tables if they don't exist"""
    conn = sqlite3.connect("vendorguard.db")
    cursor = conn.cursor()

    # Vendors table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            website TEXT,
            industry TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Risk scores table — stores history for timeline
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS risk_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vendor_id INTEGER,
            score INTEGER,
            report TEXT,
            news_signals TEXT,
            regulatory_signals TEXT,
            darkweb_signals TEXT,
            early_warning_signals TEXT,
            scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (vendor_id) REFERENCES vendors (id)
        )
    """)

    # Alerts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vendor_id INTEGER,
            message TEXT,
            severity TEXT,
            is_read INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (vendor_id) REFERENCES vendors (id)
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Database initialized successfully")

# Initialize database when app starts
init_db()

# ── Basic Routes ─────────────────────────────────────────────
@app.get("/")
def home():
    return {
        "message": "VendorGuard AI is running!",
        "status": "online",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# ── Vendor Routes ─────────────────────────────────────────────
@app.get("/vendors")
def get_vendors():
    """Get all vendors"""
    conn = sqlite3.connect("vendorguard.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT v.id, v.name, v.website, v.industry, v.created_at,
               r.score, r.scanned_at
        FROM vendors v
        LEFT JOIN risk_scores r ON r.vendor_id = v.id
        AND r.scanned_at = (
            SELECT MAX(scanned_at) FROM risk_scores
            WHERE vendor_id = v.id
        )
        ORDER BY v.created_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    vendors = []
    for row in rows:
        vendors.append({
            "id": row[0],
            "name": row[1],
            "website": row[2],
            "industry": row[3],
            "created_at": row[4],
            "latest_score": row[5],
            "last_scanned": row[6]
        })
    return {"vendors": vendors}

@app.post("/vendors")
def add_vendor(vendor: dict):
    """Add a new vendor"""
    conn = sqlite3.connect("vendorguard.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO vendors (name, website, industry) VALUES (?, ?, ?)",
        (vendor.get("name"), vendor.get("website", ""), vendor.get("industry", ""))
    )
    vendor_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return {"message": "Vendor added!", "vendor_id": vendor_id}

@app.delete("/vendors/{vendor_id}")
def delete_vendor(vendor_id: int):
    """Delete a vendor"""
    conn = sqlite3.connect("vendorguard.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM vendors WHERE id = ?", (vendor_id,))
    cursor.execute("DELETE FROM risk_scores WHERE vendor_id = ?", (vendor_id,))
    cursor.execute("DELETE FROM alerts WHERE vendor_id = ?", (vendor_id,))
    conn.commit()
    conn.close()
    return {"message": "Vendor deleted!"}

@app.get("/vendors/{vendor_id}/history")
def get_vendor_history(vendor_id: int):
    """Get risk score history for timeline chart"""
    conn = sqlite3.connect("vendorguard.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT score, scanned_at, report
        FROM risk_scores
        WHERE vendor_id = ?
        ORDER BY scanned_at ASC
        LIMIT 30
    """, (vendor_id,))
    rows = cursor.fetchall()
    conn.close()

    history = []
    for row in rows:
        history.append({
            "score": row[0],
            "scanned_at": row[1],
            "report": row[2]
        })
    return {"history": history}

@app.get("/alerts")
def get_alerts():
    """Get all unread alerts"""
    conn = sqlite3.connect("vendorguard.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.id, a.message, a.severity, a.created_at, v.name
        FROM alerts a
        JOIN vendors v ON v.id = a.vendor_id
        ORDER BY a.created_at DESC
        LIMIT 20
    """)
    rows = cursor.fetchall()
    conn.close()

    alerts = []
    for row in rows:
        alerts.append({
            "id": row[0],
            "message": row[1],
            "severity": row[2],
            "created_at": row[3],
            "vendor_name": row[4]
        })
    return {"alerts": alerts}

# ── SCAN ROUTE — The most important route ────────────────────
@app.post("/vendors/{vendor_id}/scan")
def scan_vendor(vendor_id: int):
    """
    Triggers a full scan of a vendor.
    Collects data from internet, analyzes with AI,
    saves risk score, creates alert if score jumped.
    """
    conn = sqlite3.connect("vendorguard.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, website FROM vendors WHERE id = ?",
        (vendor_id,)
    )
    vendor = cursor.fetchone()

    if not vendor:
        conn.close()
        return {"error": "Vendor not found"}

    vendor_id_db = vendor[0]
    vendor_name = vendor[1]
    vendor_website = vendor[2] or ""

    cursor.execute("""
        SELECT score FROM risk_scores
        WHERE vendor_id = ?
        ORDER BY scanned_at DESC LIMIT 1
    """, (vendor_id_db,))
    prev = cursor.fetchone()
    old_score = prev[0] if prev else 0
    conn.close()

    print(f"\n🚀 Starting scan for: {vendor_name}")
    collected = collect_vendor_data(vendor_name, vendor_website)
     # Run Browser API scan and merge results
    try:
        from browser_scraper import run_browser_scan
        browser_data = run_browser_scan(vendor_name, vendor_website)
        browser_signals = browser_data.get("all_findings", [])
        if browser_signals:
            existing = collected.get("early_warning_signals", [])
            for finding in browser_signals:
                existing.append({
                    "source": finding.get("source", "Browser API"),
                    "finding": finding.get("finding", ""),
                    "snippet": str(finding.get("details", finding.get("articles", "")))[:300],
                    "trigger_word": "browser_api"
                })
            collected["early_warning_signals"] = existing
            collected["total_signals_found"] += len(browser_signals)
            print(f"✅ Browser API added {len(browser_signals)} signals")
    except Exception as e:
        print(f"⚠ Browser API skipped: {e}")
    analysis = analyze_vendor_risk(collected)

    new_score = analysis.get("risk_score", 0)
    risk_level = analysis.get("risk_level", "GREEN")
    summary = analysis.get("summary", "")
    findings = analysis.get("key_findings", [])

    conn = sqlite3.connect("vendorguard.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO risk_scores
        (vendor_id, score, report, news_signals,
         regulatory_signals, darkweb_signals, early_warning_signals)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        vendor_id_db,
        new_score,
        summary,
        str(collected.get("news_signals", [])),
        str(collected.get("regulatory_signals", [])),
        "",
        str(collected.get("early_warning_signals", []))
    ))

    score_jump = new_score - old_score
    if score_jump >= 10 or new_score >= 61:
        alert_msg = generate_alert_message(
            vendor_name, old_score, new_score, findings
        )
        severity = "critical" if new_score >= 61 else "warning"
        cursor.execute("""
            INSERT INTO alerts (vendor_id, message, severity)
            VALUES (?, ?, ?)
        """, (vendor_id_db, alert_msg, severity))
        print(f"🚨 Alert created: {alert_msg}")

        # Send email alert
        send_risk_alert(
            vendor_name=vendor_name,
            risk_score=new_score,
            risk_level=risk_level,
            summary=summary,
            key_findings=findings,
            recommended_actions=analysis.get("recommended_actions", []),
            old_score=old_score
        )

    conn.commit()
    conn.close()

    return {
        "vendor_id": vendor_id_db,
        "vendor_name": vendor_name,
        "risk_score": new_score,
        "risk_level": risk_level,
        "summary": summary,
        "key_findings": findings,
        "risk_categories": analysis.get("risk_categories", {}),
        "recommended_actions": analysis.get("recommended_actions", []),
        "confidence_level": analysis.get("confidence_level", "LOW"),
        "signals_found": collected.get("total_signals_found", 0),
        "previous_score": old_score,
        "score_change": score_jump
    }
@app.get("/vendors/{vendor_id}/pdf")
def download_vendor_pdf(vendor_id: int):
    """Generate and download PDF risk report for a vendor"""
    conn = sqlite3.connect("vendorguard.db")
    cursor = conn.cursor()

    # Get vendor details
    cursor.execute(
        "SELECT id, name, website, industry FROM vendors WHERE id = ?",
        (vendor_id,)
    )
    vendor = cursor.fetchone()
    if not vendor:
        conn.close()
        return {"error": "Vendor not found"}

    # Get latest risk score and report
    cursor.execute("""
        SELECT score, report, news_signals,
               regulatory_signals, early_warning_signals
        FROM risk_scores
        WHERE vendor_id = ?
        ORDER BY scanned_at DESC LIMIT 1
    """, (vendor_id,))
    score_row = cursor.fetchone()
    conn.close()

    if not score_row:
        return {"error": "No scan data found. Please scan this vendor first."}

    # Build report data
    report_data = {
        "vendor_name": vendor[1],
        "risk_score": score_row[0],
        "risk_level": (
            "RED" if score_row[0] >= 61
            else "YELLOW" if score_row[0] >= 31
            else "GREEN"
        ),
        "summary": score_row[1] or "No summary available.",
        "key_findings": ["See full scan report for details"],
        "risk_categories": {
            "cybersecurity_risk": min(score_row[0] + 5, 100),
            "regulatory_risk": max(score_row[0] - 5, 0),
            "financial_risk": score_row[0],
            "reputational_risk": score_row[0]
        },
        "recommended_actions": [
            "Review vendor contract and SLA terms",
            "Request security audit documentation",
            "Monitor vendor status weekly"
        ],
        "confidence_level": "MEDIUM",
        "signals_found": 5
    }

    # Generate PDF
    pdf_bytes = generate_vendor_pdf(report_data)

    # Return as downloadable file
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=VendorGuard_{vendor[1]}_Report.pdf"
        }
    )
@app.post("/vendors/import-csv")
async def import_vendors_csv(file: UploadFile = File(...)):
    """
    Bulk import vendors from a CSV file.
    CSV format: name, website, industry
    Enterprise feature — import 100s of vendors at once.
    """
    try:
        # Read uploaded file
        content = await file.read()
        decoded = content.decode("utf-8")
        reader = csv.DictReader(io.StringIO(decoded))

        conn = sqlite3.connect("vendorguard.db")
        cursor = conn.cursor()

        imported = []
        skipped = []
        errors = []

        for row in reader:
            try:
                # Handle different column name variations
                name = (
                    row.get("name") or
                    row.get("Name") or
                    row.get("company") or
                    row.get("Company") or
                    row.get("vendor") or
                    row.get("Vendor") or ""
                ).strip()

                website = (
                    row.get("website") or
                    row.get("Website") or
                    row.get("url") or
                    row.get("URL") or ""
                ).strip()

                industry = (
                    row.get("industry") or
                    row.get("Industry") or
                    row.get("sector") or
                    row.get("Sector") or ""
                ).strip()

                if not name:
                    skipped.append(str(row))
                    continue

                # Check if vendor already exists
                cursor.execute(
                    "SELECT id FROM vendors WHERE name = ?", (name,)
                )
                existing = cursor.fetchone()

                if existing:
                    skipped.append(name)
                    continue

                # Insert vendor
                cursor.execute(
                    "INSERT INTO vendors (name, website, industry) VALUES (?, ?, ?)",
                    (name, website, industry)
                )
                imported.append(name)

            except Exception as e:
                errors.append(str(e))

        conn.commit()
        conn.close()

        return {
            "message": f"Import complete!",
            "imported": len(imported),
            "skipped": len(skipped),
            "errors": len(errors),
            "imported_vendors": imported,
            "skipped_vendors": skipped
        }

    except Exception as e:
        return {"error": f"Import failed: {str(e)}"}


@app.get("/vendors/csv-template")
def download_csv_template():
    """
    Download a sample CSV template so users know the format.
    """
    csv_content = """name,website,industry
Stripe,https://stripe.com,Payments
AWS,https://aws.amazon.com,Cloud
Salesforce,https://salesforce.com,CRM
HubSpot,https://hubspot.com,Marketing
Slack,https://slack.com,Communication
Zoom,https://zoom.us,Video Conferencing
Twilio,https://twilio.com,Communications
GitHub,https://github.com,Development
Shopify,https://shopify.com,Ecommerce
Snowflake,https://snowflake.com,Data
"""
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=vendorguard_template.csv"
        }
    )