from browser_scraper import run_browser_scan

result = run_browser_scan("FTX", "https://ftx.com")

print("\n🎯 BROWSER SCAN RESULTS:")
print(f"Wikipedia findings: {len(result['wikipedia_findings'])}")
print(f"News findings: {len(result['news_findings'])}")
print(f"Website findings: {len(result['website_findings'])}")
print(f"Total: {result['total_browser_findings']}")

print("\n📋 ALL FINDINGS:")
for finding in result['all_findings']:
    print(f"\n📌 Source: {finding['source']}")
    print(f"   Finding: {finding['finding']}")
    if 'details' in finding:
        for d in finding['details'][:2]:
            print(f"   Detail: {d[:150]}")
    if 'articles' in finding:
        for a in finding['articles'][:2]:
            print(f"   Article: {a['headline'][:150]}")