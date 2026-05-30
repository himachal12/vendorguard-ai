import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT")


def send_risk_alert(
    vendor_name: str,
    risk_score: int,
    risk_level: str,
    summary: str,
    key_findings: list,
    recommended_actions: list,
    old_score: int = 0
):
    """
    Sends a professional HTML email alert when vendor risk changes.
    Uses Gmail SMTP — completely free.
    """
    if not EMAIL_SENDER or not EMAIL_PASSWORD:
        print("⚠ Email not configured — skipping alert")
        return False

    print(f"📧 Sending email alert for: {vendor_name}")

    # Score color
    if risk_score >= 61:
        color = "#f87171"
        level_text = "🔴 CRITICAL RISK"
        bg_color = "#450a0a"
    elif risk_score >= 31:
        color = "#fbbf24"
        level_text = "🟡 MEDIUM RISK"
        bg_color = "#451a03"
    else:
        color = "#34d399"
        level_text = "🟢 LOW RISK"
        bg_color = "#064e3b"

    score_change = risk_score - old_score
    change_text = ""
    if score_change > 0:
        change_text = f"<span style='color:#f87171'>▲ +{score_change} from last scan</span>"
    elif score_change < 0:
        change_text = f"<span style='color:#34d399'>▼ {score_change} from last scan</span>"

    # Build findings HTML
    findings_html = ""
    for finding in key_findings:
        findings_html += f"""
        <div style='background:#1a1d2e; border-left:3px solid {color};
             padding:10px 14px; margin-bottom:8px; border-radius:4px;
             color:#e2e8f0; font-size:14px;'>
            • {finding}
        </div>"""

    # Build actions HTML
    actions_html = ""
    for i, action in enumerate(recommended_actions, 1):
        actions_html += f"""
        <div style='background:#1a1d2e; border-left:3px solid #2563eb;
             padding:10px 14px; margin-bottom:8px; border-radius:4px;
             color:#e2e8f0; font-size:14px;'>
            {i}. {action}
        </div>"""

    # Full HTML email
    html = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"></head>
    <body style='margin:0; padding:0; background:#0f1117; font-family:Segoe UI, sans-serif;'>

      <div style='max-width:600px; margin:0 auto; padding:24px;'>

        <!-- HEADER -->
        <div style='background:#1a1d2e; border-radius:12px 12px 0 0;
             padding:24px; text-align:center; border-bottom:2px solid {color};'>
          <h1 style='color:#60a5fa; margin:0; font-size:24px;'>
            🛡 VendorGuard AI
          </h1>
          <p style='color:#64748b; margin:6px 0 0 0; font-size:13px;'>
            Vendor Risk Intelligence Alert
          </p>
        </div>

        <!-- VENDOR + SCORE -->
        <div style='background:#1a1d2e; padding:28px; text-align:center;'>
          <h2 style='color:#e2e8f0; margin:0 0 4px 0; font-size:20px;'>
            {vendor_name}
          </h2>
          <div style='font-size:72px; font-weight:800;
               color:{color}; line-height:1; margin:12px 0;'>
            {risk_score}
          </div>
          <div style='font-size:13px; color:#94a3b8;'>
            Risk Score out of 100
          </div>
          <div style='display:inline-block; background:{bg_color};
               color:{color}; padding:6px 20px; border-radius:20px;
               font-weight:700; font-size:14px; margin:12px 0;'>
            {level_text}
          </div>
          <div style='font-size:13px; color:#64748b; margin-top:4px;'>
            {change_text}
          </div>
        </div>

        <!-- SUMMARY -->
        <div style='background:#151823; padding:20px 28px;'>
          <h3 style='color:#60a5fa; font-size:13px; text-transform:uppercase;
               letter-spacing:1px; margin:0 0 10px 0;'>
            Executive Summary
          </h3>
          <p style='color:#cbd5e1; font-size:14px; line-height:1.6; margin:0;'>
            {summary}
          </p>
        </div>

        <!-- KEY FINDINGS -->
        <div style='background:#1a1d2e; padding:20px 28px;'>
          <h3 style='color:#60a5fa; font-size:13px; text-transform:uppercase;
               letter-spacing:1px; margin:0 0 12px 0;'>
            Key Findings ({len(key_findings)})
          </h3>
          {findings_html}
        </div>

        <!-- RECOMMENDED ACTIONS -->
        <div style='background:#151823; padding:20px 28px;'>
          <h3 style='color:#60a5fa; font-size:13px; text-transform:uppercase;
               letter-spacing:1px; margin:0 0 12px 0;'>
            Recommended Actions
          </h3>
          {actions_html}
        </div>

        <!-- FOOTER -->
        <div style='background:#1a1d2e; border-radius:0 0 12px 12px;
             padding:16px 28px; text-align:center;
             border-top:1px solid #2d3748;'>
          <p style='color:#2d3748; font-size:12px; margin:0;'>
            This alert was generated automatically by VendorGuard AI<br>
            Powered by Bright Data + Groq AI •
            Web Data UNLOCKED Hackathon 2026
          </p>
        </div>

      </div>
    </body>
    </html>
    """

    try:
        # Create email message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"⚠ VendorGuard Alert: {vendor_name} Risk Score {risk_score}/100 — {level_text}"
        msg["From"] = f"VendorGuard AI <{EMAIL_SENDER}>"
        msg["To"] = EMAIL_RECIPIENT

        # Attach HTML
        msg.attach(MIMEText(html, "html"))

        # Send via Gmail SMTP
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECIPIENT, msg.as_string())

        print(f"✅ Email alert sent to {EMAIL_RECIPIENT}!")
        return True

    except Exception as e:
        print(f"❌ Email failed: {e}")
        return False