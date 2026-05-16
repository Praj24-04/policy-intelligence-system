"""Test EUR-Lex SPARQL with different query approaches."""
import requests

ENDPOINT = "https://publications.europa.eu/webapi/rdf/sparql"

# Approach 1: Search by title keywords instead of CELEX
print("Approach 1: Search by title keyword 'artificial intelligence'...")
query1 = """
PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
SELECT DISTINCT ?celex ?title WHERE {
  ?work cdm:resource_legal_id_celex ?celex ;
        cdm:work_title ?title .
  FILTER(LANG(?title) = "en")
  FILTER(CONTAINS(LCASE(?title), "artificial intelligence"))
}
LIMIT 10
"""
try:
    r = requests.get(ENDPOINT, params={"query": query1},
                     headers={"Accept": "application/sparql-results+json"}, timeout=20)
    r.raise_for_status()
    bindings = r.json().get("results", {}).get("bindings", [])
    print(f"  Results: {len(bindings)}")
    for b in bindings[:5]:
        print(f"  - CELEX: {b['celex']['value']}")
        print(f"    Title: {b['title']['value'][:100]}")
except Exception as e:
    print(f"  Failed: {e}")

# Approach 2: Search by date (recent legislation)
print("\nApproach 2: Recent legislation mentioning 'data protection'...")
query2 = """
PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
SELECT DISTINCT ?celex ?title ?date WHERE {
  ?work cdm:resource_legal_id_celex ?celex ;
        cdm:work_title ?title ;
        cdm:work_date_document ?date .
  FILTER(LANG(?title) = "en")
  FILTER(CONTAINS(LCASE(?title), "data protection"))
}
ORDER BY DESC(?date)
LIMIT 10
"""
try:
    r = requests.get(ENDPOINT, params={"query": query2},
                     headers={"Accept": "application/sparql-results+json"}, timeout=20)
    r.raise_for_status()
    bindings = r.json().get("results", {}).get("bindings", [])
    print(f"  Results: {len(bindings)}")
    for b in bindings[:5]:
        print(f"  - CELEX: {b['celex']['value']}, Date: {b.get('date', {}).get('value', '?')}")
        print(f"    Title: {b['title']['value'][:100]}")
except Exception as e:
    print(f"  Failed: {e}")

# Approach 3: Search for cybersecurity
print("\nApproach 3: Cybersecurity legislation...")
query3 = """
PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
SELECT DISTINCT ?celex ?title WHERE {
  ?work cdm:resource_legal_id_celex ?celex ;
        cdm:work_title ?title .
  FILTER(LANG(?title) = "en")
  FILTER(CONTAINS(LCASE(?title), "cybersecurity") || CONTAINS(LCASE(?title), "cyber"))
}
LIMIT 10
"""
try:
    r = requests.get(ENDPOINT, params={"query": query3},
                     headers={"Accept": "application/sparql-results+json"}, timeout=20)
    r.raise_for_status()
    bindings = r.json().get("results", {}).get("bindings", [])
    print(f"  Results: {len(bindings)}")
    for b in bindings[:5]:
        print(f"  - CELEX: {b['celex']['value']}")
        print(f"    Title: {b['title']['value'][:100]}")
except Exception as e:
    print(f"  Failed: {e}")

# Approach 4: Simple broad query - just get any recent regulation
print("\nApproach 4: Any recent EU regulation (broad test)...")
query4 = """
PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
SELECT DISTINCT ?celex ?title ?date WHERE {
  ?work cdm:resource_legal_id_celex ?celex ;
        cdm:work_title ?title ;
        cdm:work_date_document ?date .
  FILTER(LANG(?title) = "en")
  FILTER(?date > "2024-01-01"^^xsd:date)
  FILTER(CONTAINS(LCASE(?title), "digital") || CONTAINS(LCASE(?title), "regulation"))
}
ORDER BY DESC(?date)
LIMIT 5
"""
try:
    r = requests.get(ENDPOINT, params={"query": query4},
                     headers={"Accept": "application/sparql-results+json"}, timeout=20)
    r.raise_for_status()
    bindings = r.json().get("results", {}).get("bindings", [])
    print(f"  Results: {len(bindings)}")
    for b in bindings[:5]:
        print(f"  - CELEX: {b['celex']['value']}, Date: {b.get('date', {}).get('value', '?')}")
        print(f"    Title: {b['title']['value'][:100]}")
except Exception as e:
    print(f"  Failed: {e}")
