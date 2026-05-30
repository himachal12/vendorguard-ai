import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("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"))

def analyze_vendor_risk(collected_data: dict) -> dict:
    vendor_name = collected_data.get("vendor_name", "Unknown")
    print(f"\n🧠 AI analyzing risk for: {vendor_name}")

    news = collected_data.get("news_signals", [])
    regulatory = collected_data.get("regulatory_signals", [])
    website = collected_data.get("website_signals", [])
    early_warning = collected_data.get("early_warning_signals", [])

    news_text = "\n".join([
        f"- {n.get('title','')}: {n.get('snippet','')[:150]}"
        for n in news
    ]) or "No news signals found."

    regulatory_text = "\n".join([
        f"- {r.get('title','')}: {r.get('snippet','')[:150]}"
        for r in regulatory
    ]) or "No regulatory signals found."

    website_text = "\n".join([
        f"- {w.get('finding','')}"
        for w in website
    ]) or "Website appears clean."

    early_text = "\n".join([
        f"- {e.get('finding','')}: {e.get('snippet','')[:150]}"
        for e in early_warning
    ]) or "No early warning signals found."

    prompt = f"""You are VendorGuard AI — an expert enterprise risk analyst.

Analyze this intelligence data about vendor "{vendor_name}" and return a risk assessment.

NEWS SIGNALS:
{news_text}

REGULATORY SIGNALS:
{regulatory_text}

WEBSITE SIGNALS:
{website_text}

EARLY WARNING SIGNALS:
{early_text}

Return ONLY this JSON, no extra text, no markdown:

{{
    "risk_score": <integer 0-100>,
    "risk_level": "<GREEN / YELLOW / RED>",
    "summary": "<2-3 sentence plain English summary>",
    "key_findings": ["<finding 1>", "<finding 2>", "<finding 3>"],
    "risk_categories": {{
        "cybersecurity_risk": <0-100>,
        "regulatory_risk": <0-100>,
        "financial_risk": <0-100>,
        "reputational_risk": <0-100>
    }},
    "recommended_actions": ["<action 1>", "<action 2>"],
    "confidence_level": "<LOW / MEDIUM / HIGH>"
}}

SCORING: 0-30=GREEN, 31-60=YELLOW, 61-100=RED"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert enterprise risk analyst. Always respond with valid JSON only. No markdown, no explanation, just the JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,
            max_tokens=1000
        )

        raw = response.choices[0].message.content.strip()

        # Clean markdown if Groq adds it
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        result = json.loads(raw)

        print(f"✅ Analysis complete!")
        print(f"📊 Risk Score: {result.get('risk_score')}/100")
        print(f"🚦 Risk Level: {result.get('risk_level')}")
        print(f"📝 {result.get('summary','')[:120]}...")

        return result

    except Exception as e:
        print(f"❌ AI failed: {e}")
        return _default_response(str(e))


def generate_alert_message(
    vendor_name: str,
    old_score: int,
    new_score: int,
    findings: list
) -> str:
    jump = new_score - old_score
    top = findings[0] if findings else "Multiple risk signals detected"

    if new_score >= 61:
        severity = "🔴 CRITICAL"
    elif new_score >= 31:
        severity = "🟡 WARNING"
    else:
        severity = "🟢 RESOLVED"

    return (
        f"{severity}: {vendor_name} risk jumped "
        f"from {old_score} to {new_score} (+{jump} points). {top}"
    )


def _default_response(reason: str) -> dict:
    return {
        "risk_score": 50,
        "risk_level": "YELLOW",
        "summary": f"Analysis incomplete: {reason}",
        "key_findings": ["Re-scan recommended"],
        "risk_categories": {
            "cybersecurity_risk": 50,
            "regulatory_risk": 50,
            "financial_risk": 50,
            "reputational_risk": 50
        },
        "recommended_actions": ["Re-run scan", "Manual review"],
        "confidence_level": "LOW"
    }