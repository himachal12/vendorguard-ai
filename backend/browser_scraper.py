import asyncio
import os
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv()

BROWSER_USER = os.getenv("BRIGHTDATA_BROWSER_USER")
BROWSER_PASS = os.getenv("BRIGHTDATA_BROWSER_PASS")

# Official Bright Data connection string
AUTH = f"{BROWSER_USER}:{BROWSER_PASS}"
WS_ENDPOINT = f"wss://{AUTH}@brd.superproxy.io:9222"


async def browser_scan_vendor(vendor_name: str, vendor_website: str = "") -> dict:
    """
    One browser connection — multiple pages.
    This is the correct pattern per Bright Data docs.
    """
    print(f"\n{'='*50}")
    print(f"🚀 Browser API scanning: {vendor_name}")
    print(f"{'='*50}")

    results = {
        "wikipedia_findings": [],
        "news_findings": [],
        "website_findings": [],
        "total_browser_findings": 0,
        "all_findings": []
    }

    try:
        async with async_playwright() as p:
            # ONE connection — keep it open for all scraping
            print("🔌 Connecting to Bright Data Browser API...")
            browser = await p.chromium.connect_over_cdp(WS_ENDPOINT)
            print("✅ Connected!")

            # ── PAGE 1: Wikipedia ─────────────────────────────
            try:
                print(f"📖 Opening Wikipedia for: {vendor_name}")
                page1 = await browser.new_page()
                page1.set_default_navigation_timeout(60000)

                wiki_url = f"https://en.wikipedia.org/wiki/{vendor_name.replace(' ', '_')}"
                await page1.goto(wiki_url, wait_until="domcontentloaded")

                text = await page1.inner_text("body")
                text_lower = text.lower()

                risk_keywords = [
                    "controversy", "fraud", "lawsuit", "fine",
                    "bankruptcy", "collapse", "investigation",
                    "scandal", "breach", "hack", "charged",
                    "penalty", "indicted", "settlement"
                ]

                found = [kw for kw in risk_keywords if kw in text_lower]

                if found:
                    # Extract relevant paragraphs
                    paragraphs = [
                        p.strip() for p in text.split('\n')
                        if len(p.strip()) > 80 and
                        any(kw in p.lower() for kw in risk_keywords)
                    ][:3]

                    finding = {
                        "source": "Wikipedia (Direct Browser)",
                        "finding": f"Risk keywords found: {', '.join(found[:5])}",
                        "details": paragraphs,
                        "data_type": "ENCYCLOPEDIA_PRIMARY_SOURCE"
                    }
                    results["wikipedia_findings"].append(finding)
                    results["all_findings"].append(finding)
                    print(f"✅ Wikipedia: found {len(found)} risk keywords")
                else:
                    print(f"✅ Wikipedia: no controversies found")

                await page1.close()

            except Exception as e:
                print(f"⚠ Wikipedia failed: {e}")

            # ── PAGE 2: DuckDuckGo News Search ───────────────
            try:
                print(f"📰 Searching DuckDuckGo news for: {vendor_name}")
                page2 = await browser.new_page()
                page2.set_default_navigation_timeout(60000)

                ddg_url = f"https://duckduckgo.com/?q={vendor_name.replace(' ', '+')}+fraud+OR+lawsuit+OR+breach+OR+scandal&ia=news"
                await page2.goto(ddg_url, wait_until="domcontentloaded")

                text = await page2.inner_text("body")
                text_lower = text.lower()

                risk_keywords = [
                    "fraud", "lawsuit", "fine", "hack", "breach",
                    "bankrupt", "collapse", "investigation", "charges",
                    "penalty", "layoff", "scandal", "leak", "indicted"
                ]

                found_articles = []
                lines = text.split('\n')
                for line in lines:
                    line = line.strip()
                    if len(line) > 40:
                        for kw in risk_keywords:
                            if kw in line.lower():
                                found_articles.append({
                                    "headline": line[:200],
                                    "trigger": kw
                                })
                                break

                if found_articles:
                    finding = {
                        "source": "DuckDuckGo News (Direct Browser)",
                        "finding": f"Found {len(found_articles)} risk news items",
                        "articles": found_articles[:4],
                        "data_type": "DIRECT_NEWS_SEARCH"
                    }
                    results["news_findings"].append(finding)
                    results["all_findings"].append(finding)
                    print(f"✅ DuckDuckGo: {len(found_articles)} risk items found")
                else:
                    print(f"ℹ DuckDuckGo: no risk news found")

                await page2.close()

            except Exception as e:
                print(f"⚠ DuckDuckGo search failed: {e}")

            # ── PAGE 3: Vendor Website ────────────────────────
            if vendor_website:
                try:
                    print(f"🌐 Opening vendor website: {vendor_website}")
                    page3 = await browser.new_page()
                    page3.set_default_navigation_timeout(60000)

                    await page3.goto(
                        vendor_website,
                        wait_until="domcontentloaded"
                    )

                    text = await page3.inner_text("body")
                    text_lower = text.lower()

                    red_flags = [
                        "incident", "breach", "outage",
                        "security alert", "data leak",
                        "unauthorized access", "we are investigating",
                        "service disruption", "vulnerability"
                    ]

                    found = [f for f in red_flags if f in text_lower]

                    if found:
                        finding = {
                            "source": "Vendor Website (Direct Browser)",
                            "finding": f"Red flags on website: {', '.join(found)}",
                            "data_type": "DIRECT_WEBSITE_SCAN"
                        }
                        results["website_findings"].append(finding)
                        results["all_findings"].append(finding)
                        print(f"🚨 Website red flags: {found}")
                    else:
                        print(f"✅ Vendor website looks clean")

                    await page3.close()

                except Exception as e:
                    print(f"⚠ Website check failed: {e}")

            # Close browser
            await browser.close()
            print("🔌 Browser closed cleanly")

    except Exception as e:
        print(f"❌ Browser connection failed: {e}")

    results["total_browser_findings"] = len(results["all_findings"])
    print(f"\n✅ Browser scan complete: {results['total_browser_findings']} findings")
    return results


def run_browser_scan(vendor_name: str, vendor_website: str = "") -> dict:
    """Synchronous wrapper for FastAPI"""
    try:
        return asyncio.run(browser_scan_vendor(vendor_name, vendor_website))
    except Exception as e:
        print(f"❌ Browser scan failed: {e}")
        return {
            "wikipedia_findings": [],
            "news_findings": [],
            "website_findings": [],
            "total_browser_findings": 0,
            "all_findings": []
        }