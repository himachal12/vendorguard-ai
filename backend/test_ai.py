from data_collector import collect_vendor_data
from ai_engine import analyze_vendor_risk

# Collect data
data = collect_vendor_data("Stripe", "https://stripe.com")

# Analyze with AI
result = analyze_vendor_risk(data)

print("\n\n🎯 FULL RISK REPORT:")
print(f"Risk Score: {result['risk_score']}/100")
print(f"Risk Level: {result['risk_level']}")
print(f"Summary: {result['summary']}")
print(f"\nKey Findings:")
for f in result['key_findings']:
    print(f"  • {f}")
print(f"\nRisk Categories:")
for k, v in result['risk_categories'].items():
    print(f"  • {k}: {v}/100")
print(f"\nRecommended Actions:")
for a in result['recommended_actions']:
    print(f"  • {a}")