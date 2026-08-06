"""Test if Federal Register has country-specific policy documents."""
import requests

# Countries we have profiles for
COUNTRIES = [
    "India", "China", "Brazil", "Japan", "Singapore",  
    "Australia", "Canada", "South Korea", "Germany",
    "United Kingdom", "Nigeria", "Kenya", "Saudi Arabia",
    "Indonesia", "South Africa", "United Arab Emirates",
    "Mexico", "Argentina", "France"
]

for country in COUNTRIES:
    terms = [
        f"{country} data privacy",
        f"{country} cybersecurity",
        f"{country} regulation",
    ]
    total = 0
    for term in terms:
        try:
            r = requests.get(
                "https://www.federalregister.gov/api/v1/documents.json",
                params={"conditions[term]": term, "per_page": 1},
                timeout=10
            )
            count = r.json().get("count", 0)
            total += count
        except:
            pass
    print(f"  {country:25s}: ~{total:>6} relevant US Federal Register documents")
