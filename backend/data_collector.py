import requests
import os
from dotenv import load_dotenv

load_dotenv()

BRIGHTDATA_API_KEY = os.getenv("BRIGHTDATA_API_KEY")
SERP_ZONE = os.getenv("BRIGHTDATA_SERP_ZONE")
MCP_TOKEN = os.getenv("BRIGHTDATA_MCP_TOKEN")

BRIGHTDATA_ENDPOINT = "https://api.brightdata.com/request"
MCP_ENDPOINT = "https://api.brightdata.com/request"

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {BRIGHTDATA_API_KEY}"
}

# ── SERP API — Search Google for vendor news ─────────────────
def search_vendor_news(vendor_name: str):
    """Search Google News for vendor scandals, hacks, lawsuits"""
    print(f"🔍 Searching news for: {vendor_name}")

    try:
        query = f"{vendor_name} hack OR breach OR lawsuit OR fine OR scandal OR bankrupt OR investigation"
        payload = {
            "zone": SERP_ZONE,
            "url": f"https://www.google.com/search?q={requests.utils.quote(query)}&tbm=nws&hl=en&gl=us",
            "format": "raw"
        }

        response = requests.post(
            BRIGHTDATA_ENDPOINT,
            headers=HEADERS,
            json=payload,
            timeout=30
        )

        print(f"📡 News API status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            results = []

            # Extract organic results from Light JSON format
            organic = data.get("organic", [])
            for item in organic[:5]:
                results.append({
                    "title": item.get("title", ""),
                    "snippet": item.get("description", ""),
                    "url": item.get("link", ""),
                })

            print(f"✅ Found {len(results)} news results")
            return results
        else:
            print(f"⚠ Error: {response.status_code} - {response.text[:200]}")
            return []

    except Exception as e:
        print(f"❌ News search failed: {e}")
        return []


# ── SERP API — Search for regulatory signals ─────────────────
def check_regulatory_signals(vendor_name: str):
    """
    Uses SERP API to search for regulatory actions.
    Searches SEC, FTC, government enforcement actions.
    """
    print(f"🏛 Checking regulatory signals for: {vendor_name}")

    try:
        query = f"{vendor_name} SEC OR FTC OR regulatory OR enforcement OR penalty OR compliance violation"
        payload = {
            "zone": SERP_ZONE,
            "url": f"https://www.google.com/search?q={requests.utils.quote(query)}&hl=en&gl=us",
            "format": "raw"
        }

        response = requests.post(
            BRIGHTDATA_ENDPOINT,
            headers=HEADERS,
            json=payload,
            timeout=30
        )

        print(f"📡 Regulatory API status: {response.status_code}")

        results = []
        if response.status_code == 200:
            data = response.json()
            organic = data.get("organic", [])

            for item in organic[:3]:
                title = item.get("title", "")
                snippet = item.get("description", "")

                # Only include if actually regulatory related
                reg_keywords = [
                    "sec", "ftc", "fine", "penalty", "enforcement",
                    "violation", "lawsuit", "investigation", "charged"
                ]
                combined = (title + snippet).lower()
                if any(word in combined for word in reg_keywords):
                    results.append({
                        "source": "Regulatory Search",
                        "title": title,
                        "snippet": snippet,
                        "url": item.get("link", "")
                    })

        print(f"✅ Found {len(results)} regulatory signals")
        return results

    except Exception as e:
        print(f"❌ Regulatory check failed: {e}")
        return []


# ── MCP Server — Scrape vendor website ───────────────────────
def check_vendor_website(vendor_website: str, vendor_name: str):
    """
    Uses MCP Server to scrape vendor's actual website.
    Returns clean markdown — works on JavaScript heavy sites.
    Looks for incident notices, security alerts, outage notices.
    """
    if not vendor_website:
        print(f"⚠ No website for {vendor_name}, skipping")
        return []

    print(f"🌐 Scraping vendor website: {vendor_website}")

    try:
        payload = {
            "zone": SERP_ZONE,
            "url": vendor_website,
            "format": "raw",
            "data_format": "markdown"
        }

        response = requests.post(
            MCP_ENDPOINT,
            headers=HEADERS,
            json=payload,
            timeout=40
        )

        print(f"📡 Website scrape status: {response.status_code}")

        results = []
        if response.status_code == 200:
            content = response.text[:3000].lower()

            # Red flag keywords to look for
            red_flags = [
                "incident", "breach", "outage", "security alert",
                "vulnerability", "data leak", "service disruption",
                "we are investigating", "unauthorized access"
            ]

            found = []
            for flag in red_flags:
                if flag in content:
                    found.append(flag)

            if found:
                results.append({
                    "source": "Vendor Website",
                    "finding": f"Red flag keywords found: {', '.join(found)}",
                    "severity": "high"
                })
                print(f"🚨 Red flags on website: {found}")
            else:
                print(f"✅ Website looks clean")

        else:
            print(f"⚠ Website scrape error: {response.status_code}")

        return results

    except Exception as e:
        print(f"❌ Website check failed: {e}")
        return []


# ── SERP API — Early Warning Signals ─────────────────────────
def check_early_warning_signals(vendor_name: str):
    """
    SECRET WEAPON 3 — detects risk BEFORE it makes headlines.
    Searches for layoffs, bad reviews, legal hiring, exec exits.
    These weak signals appear weeks before public news breaks.
    """
    print(f"🔎 Checking early warning signals for: {vendor_name}")

    signals = []

    warning_queries = [
        f"{vendor_name} layoffs employees fired 2025 2026",
        f"{vendor_name} CEO resign quit left company 2025 2026",
        f"{vendor_name} data breach leaked credentials 2025 2026",
    ]

    try:
        for query in warning_queries:
            payload = {
                "zone": SERP_ZONE,
                "url": f"https://www.google.com/search?q={requests.utils.quote(query)}&hl=en&gl=us",
                "format": "raw"
            }

            response = requests.post(
                BRIGHTDATA_ENDPOINT,
                headers=HEADERS,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                organic = data.get("organic", [])

                warning_words = [
                    "layoff", "fired", "laid off", "resign", "quit",
                    "breach", "leaked", "hack", "stolen", "exposed",
                    "lawsuit", "investigation", "toxic", "scandal"
                ]

                for item in organic[:2]:
                    title = item.get("title", "")
                    snippet = item.get("description", "")
                    combined = (title + snippet).lower()

                    for word in warning_words:
                        if word in combined:
                            signals.append({
                                "source": "Early Warning",
                                "finding": title,
                                "snippet": snippet[:200],
                                "url": item.get("link", ""),
                                "trigger_word": word
                            })
                            break

    except Exception as e:
        print(f"❌ Early warning check failed: {e}")

    print(f"⚠ Found {len(signals)} early warning signals")
    return signals


# ── MAIN COLLECTOR — Runs All Checks ─────────────────────────
def collect_vendor_data(vendor_name: str, vendor_website: str = ""):
    """
    Master function — runs ALL data collection for one vendor.
    Returns complete raw data package for AI to analyze.
    """
    print(f"\n{'='*50}")
    print(f"🚀 Collecting data for: {vendor_name}")
    print(f"{'='*50}")

    news = search_vendor_news(vendor_name)
    regulatory = check_regulatory_signals(vendor_name)
    website = check_vendor_website(vendor_website, vendor_name)
    early_warning = check_early_warning_signals(vendor_name)

    collected_data = {
        "vendor_name": vendor_name,
        "vendor_website": vendor_website,
        "news_signals": news,
        "regulatory_signals": regulatory,
        "website_signals": website,
        "early_warning_signals": early_warning,
        "total_signals_found": (
            len(news) + len(regulatory) +
            len(website) + len(early_warning)
        )
    }

    print(f"\n✅ Collection complete for {vendor_name}")
    print(f"📊 Total signals: {collected_data['total_signals_found']}")

    return collected_data