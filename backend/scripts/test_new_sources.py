"""Test Federal Register API + UK Legislation API connectivity."""
import requests
import json

print("=" * 60)
print("Testing new live data sources")
print("=" * 60)

# 1. Federal Register API (US)
print("\n1. US Federal Register API...")
SECTORS = ["artificial intelligence", "cybersecurity", "data privacy", "ESG", "robotics"]
for term in SECTORS:
    try:
        r = requests.get(
            "https://www.federalregister.gov/api/v1/documents.json",
            params={
                "conditions[term]": term,
                "per_page": 5,
                "order": "relevance",
                "fields[]": ["title", "abstract", "publication_date", "type", "document_number", "html_url"]
            },
            timeout=15
        )
        r.raise_for_status()
        data = r.json()
        count = data.get("count", 0)
        results = data.get("results", [])
        print(f"   '{term}': {count} total results")
        if results:
            print(f"     Top: {results[0].get('title', '?')[:80]}")
    except Exception as e:
        print(f"   FAILED for '{term}': {e}")

# 2. UK Legislation API
print("\n2. UK Legislation API...")
UK_SEARCHES = [
    ("data protection", "ukpga"),
    ("online safety", "ukpga"),
    ("computer misuse", "ukpga"),
]
for title, leg_type in UK_SEARCHES:
    try:
        r = requests.get(
            f"https://www.legislation.gov.uk/{leg_type}/data.feed",
            params={"title": title},
            headers={"Accept": "application/atom+xml"},
            timeout=15
        )
        print(f"   '{title}' ({leg_type}): HTTP {r.status_code}, {len(r.text)} bytes")
    except Exception as e:
        print(f"   FAILED for '{title}': {e}")

print("\n" + "=" * 60)
