from data_collector import collect_vendor_data

# Test with a real company
data = collect_vendor_data("Stripe", "https://stripe.com")

print("\n\n📦 RAW DATA COLLECTED:")
print(f"News signals: {len(data['news_signals'])}")
print(f"Regulatory signals: {len(data['regulatory_signals'])}")
print(f"Website signals: {len(data['website_signals'])}")
print(f"Early warning signals: {len(data['early_warning_signals'])}")
print(f"\nFirst news item: {data['news_signals'][0] if data['news_signals'] else 'None'}")