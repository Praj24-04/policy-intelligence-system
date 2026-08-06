"""Quick verification that the live data sources are reachable."""
import requests
import json

print("=" * 50)
print("Testing live data source connectivity...")
print("=" * 50)

# Test 1: CISA KEV JSON
print("\n1. CISA KEV JSON Feed...")
try:
    r = requests.get(
        "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json",
        timeout=15
    )
    r.raise_for_status()
    d = r.json()
    vulns = d.get("vulnerabilities", [])
    print(f"   OK: {len(vulns)} vulnerabilities, catalog v{d.get('catalogVersion', '?')}")
    if vulns:
        latest = sorted(vulns, key=lambda v: v.get("dateAdded", ""), reverse=True)[0]
        print(f"   Latest: {latest.get('cveID')} - {latest.get('vendorProject')} ({latest.get('dateAdded')})")
except Exception as e:
    print(f"   FAILED: {e}")

# Test 2: EUR-Lex SPARQL
print("\n2. EUR-Lex SPARQL Endpoint...")
try:
    query = """
    PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
    SELECT ?title WHERE {
      ?work cdm:resource_legal_id_celex "32024R1689" ;
            cdm:work_title ?title .
      FILTER(LANG(?title) = "en")
    }
    LIMIT 1
    """
    r = requests.get(
        "https://publications.europa.eu/webapi/rdf/sparql",
        params={"query": query},
        headers={"Accept": "application/sparql-results+json"},
        timeout=15,
    )
    r.raise_for_status()
    bindings = r.json().get("results", {}).get("bindings", [])
    if bindings:
        title = bindings[0]["title"]["value"]
        print(f"   OK: AI Act title = '{title[:80]}...'")
    else:
        print("   OK: Endpoint reachable but no results (might need different query)")
except Exception as e:
    print(f"   FAILED: {e}")

print("\n" + "=" * 50)
print("Connectivity test complete.")
