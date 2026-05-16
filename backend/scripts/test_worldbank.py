"""Test World Bank API for global regulatory data."""
import requests
import json

# Test: Fetch regulatory quality indicator for all countries
print("Testing World Bank Indicators API...")

# IT.NET.SECR.P6 = Secure Internet servers per 1 million people (cybersecurity proxy)
# RQ.EST = Regulatory Quality estimate
# IC.BUS.EASE.DFRN.DB.XQ = Ease of doing business  
# SG.GEN.LHRD.IFRS = Laws on sexual harassment in employment

indicators = [
    ("IT.NET.SECR.P6", "Secure Internet Servers (per million)"),
    ("RQ.EST", "Regulatory Quality"),
    ("SG.GEN.LHRD.IFRS", "Sexual harassment laws in employment"),
]

for code, label in indicators:
    try:
        r = requests.get(
            f"https://api.worldbank.org/v2/country/all/indicator/{code}",
            params={"format": "json", "date": "2023", "per_page": 5},
            timeout=15
        )
        r.raise_for_status()
        data = r.json()
        if len(data) > 1:
            entries = data[1]
            print(f"\n  {label} ({code}): {len(entries)} results")
            for e in entries[:3]:
                print(f"    {e.get('country', {}).get('value', '?')}: {e.get('value', 'N/A')}")
        else:
            print(f"\n  {label}: No data")
    except Exception as e:
        print(f"\n  {label}: FAILED - {e}")

# Test: Search for countries
print("\n\nTesting country list...")
try:
    r = requests.get(
        "https://api.worldbank.org/v2/country",
        params={"format": "json", "per_page": 300},
        timeout=15
    )
    data = r.json()
    if len(data) > 1:
        countries = [c for c in data[1] if c.get("region", {}).get("value") != "Aggregates"]
        print(f"  Total non-aggregate countries: {len(countries)}")
        regions = {}
        for c in countries:
            reg = c.get("region", {}).get("value", "Unknown")
            regions[reg] = regions.get(reg, 0) + 1
        for reg, count in sorted(regions.items()):
            print(f"    {reg}: {count} countries")
except Exception as e:
    print(f"  FAILED: {e}")
