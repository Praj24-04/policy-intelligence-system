import json
import hashlib
import requests
from datetime import datetime
from pathlib import Path
from app.database import get_connection

# ── Last fetch results (in-memory cache for status endpoint) ─────────
_last_fetch_result = {
    "timestamp": None,
    "sources": {},
    "total_inserted": 0,
    "total_duplicates": 0,
}

EURLEX_SPARQL_ENDPOINT = "https://publications.europa.eu/webapi/rdf/sparql"
CISA_KEV_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
FEDERAL_REGISTER_URL = "https://www.federalregister.gov/api/v1/documents.json"


# ── Helpers ──────────────────────────────────────────────────────────

def generate_id(prefix: str, title: str, country: str) -> str:
    """Generate deterministic policy ID from source prefix + title + country."""
    raw = f"{title.lower().strip()}{country.lower().strip()}"
    return f"{prefix}_" + hashlib.md5(raw.encode()).hexdigest()[:10]


def policy_exists(policy_id: str) -> bool:
    conn = get_connection()
    row = conn.execute("SELECT id FROM policies WHERE id = %s", (policy_id,)).fetchone()
    conn.close()
    return row is not None


def save_policy(policy: dict) -> bool:
    """Insert policy if it doesn't already exist. Returns True if inserted."""
    if policy_exists(policy["id"]):
        return False
    conn = get_connection()
    try:
        conn.execute("""
            INSERT INTO policies 
            (id, title, sector, region, country, content, tags, status, year, version, source_url)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            policy["id"], policy["title"], policy["sector"], policy["region"],
            policy["country"], policy["content"], json.dumps(policy.get("tags", [])),
            policy.get("status", "Active"), policy.get("year"),
            policy.get("version", "1.0"), policy.get("source_url", "")
        ))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving policy {policy.get('id', '?')}: {e}")
        conn.close()
        return False


# ── Sector classifier ───────────────────────────────────────────────

# Keywords that indicate a document is NOT relevant policy content
IRRELEVANT_KEYWORDS = [
    "tire", "tires", "lumber", "sugar", "steel", "aluminum", "aluminium",
    "shrimp", "honey", "fish", "seafood", "poultry", "beef", "pork",
    "cotton", "wheat", "corn", "rice", "petroleum", "gasoline",
    "textile", "garment", "footwear", "furniture", "ceramic",
    "antidumping", "anti-dumping", "countervailing duty", "tariff",
    "import quota", "customs duty", "trade remedy", "dumping margin",
    "suspension agreement", "injury determination",
    "pesticide", "herbicide", "fertilizer",
    "motor vehicle safety standard", "seat belt",
    "food labeling", "nutrition labeling", "dietary supplement",
    "animal feed", "veterinary", "hunting", "fishing quota",
    "spectrum auction", "broadcast license",
    "marine mammal", "marine mammals", "endangered species",
    "recoupment of awards", "recoupment of bonuses",
    "visa", "immigration", "passport", "naturalization",
    "crop insurance", "grain inspection", "livestock",
    "tobacco", "alcohol", "firearms dealer",
    "bankruptcy", "mortgage servicing",
    "airworthiness", "aircraft certification",
    "nuclear reactor", "radioactive waste",
    "waterway", "dredging", "navigation channel",
]


def _is_policy_relevant(title: str, abstract: str = "") -> bool:
    """Check if a document is actually relevant to our policy sectors."""
    t = (title + " " + (abstract or "")).lower()

    # Reject if it matches irrelevant trade/commodity/unrelated keywords
    for kw in IRRELEVANT_KEYWORDS:
        if kw in t:
            return False

    return True  # Let the strict sector classifier handle the rest


def _classify_sector(title: str, abstract: str = "") -> str:
    """Heuristic sector classification from title + abstract text.
    Returns None if document doesn't match any known sector."""
    t = ((title or "") + " " + (abstract or "")).lower()
    
    # Privacy Act / System of Records is always Data Privacy
    if "privacy act" in t or "system of records" in t:
        return "Data Privacy"
        
    # Check POSH Policies first (high specificity)
    if any(kw in t for kw in ["harassment", "sexual harassment", "posh", "pawahara", "power harassment", "workplace harassment"]):
        return "POSH Policies"
        
    # Check Healthcare / Clinical Trials first (high specificity)
    if any(kw in t for kw in ["healthcare", "medical device", "clinical", "health data", "hipaa",
                               "electronic health", "telehealth", "patient data", "medical ai",
                               "medicare", "medicaid", "hospital", "physician fee",
                               "clinical trial", "clinical trials", "patient population"]):
        return "Healthcare AI"

    if any(kw in t for kw in ["digital markets act", "dma", "digital services act", "dsa", "gatekeeper", "online intermediation", "antitrust", "competition"]):
        return "Data Privacy"
        
    if any(kw in t for kw in ["artificial intelligence", "ai act", "ai governance", "algorithmic",
                               "machine learning", "deep learning", "autonomous system", "generative ai"]):
        return "AI Governance"
        
    if any(kw in t for kw in ["cybersecurity", "cyber security", "cyber resilience", "network security",
                               "vulnerability", "exploit", "malware", "ransomware", "incident response",
                               "critical infrastructure protection", "information security"]):
        return "Cybersecurity"
        
    if any(kw in t for kw in ["data protection", "data privacy", "privacy", "personal data", "gdpr",
                               "consumer data", "surveillance", "biometric", "facial recognition",
                               "data breach", "consent", "data subject"]):
        return "Data Privacy"
        
    if any(kw in t for kw in ["financial", "banking", "crypto", "digital asset", "payment systems",
                               "payment services", "electronic payment", "securities", "fintech",
                               "anti-money", "aml", "kyc", "capital markets", "lending", "credit"]):
        return "Financial Regulation"
        
    if any(kw in t for kw in ["iot", "internet of things", "robot", "drone", "autonomous vehicle",
                               "connected device", "smart device", "embedded system"]):
        return "IoT and Robotics"
        
    if any(kw in t for kw in ["esg", "sustainability", "climate", "environmental", "carbon",
                               "green", "renewable", "emission", "biodiversity", "taxonomy"]):
        return "ESG Policies"
    
    # ── Check admin-added custom sectors from database ──
    try:
        conn = get_connection()
        custom_rows = conn.execute(
            "SELECT name, keywords FROM custom_sectors WHERE status = 'Active' AND keywords != ''"
        ).fetchall()
        conn.close()
        for row in custom_rows:
            sector_keywords = [kw.strip().lower() for kw in row["keywords"].split(",") if kw.strip()]
            if any(kw in t for kw in sector_keywords):
                return row["name"]
    except Exception:
        pass  # Graceful fallback if DB not available

    return None  # Not relevant to any known sector


def _detect_country(title: str, abstract: str, hint: str = None) -> str:
    """Detect which country a policy is most relevant to."""
    title_lower = (title or "").lower()
    abstract_lower = (abstract or "").lower()
    
    country_variants = {
        "India": ["india", "indian"],
        "Japan": ["japan", "japanese"],
        "Australia": ["australia", "australian"],
        "Canada": ["canada", "canadian"],
        "South Korea": ["south korea", "korea", "korean"],
        "South Africa": ["south africa", "south african"],
        "Saudi Arabia": ["saudi arabia", "saudi"],
        "United Arab Emirates": ["united arab emirates", "uae"],
        "United Kingdom": ["united kingdom", "uk", "british"],
        "Germany": ["germany", "german"],
        "France": ["france", "french"],
        "Nigeria": ["nigeria", "nigerian"],
        "Kenya": ["kenya", "kenyan"],
        "Indonesia": ["indonesia", "indonesian"],
        "Mexico": ["mexico", "mexican"],
        "Argentina": ["argentina", "argentine"],
        "Brazil": ["brazil", "brazilian"],
        "China": ["china", "chinese"],
        "Singapore": ["singapore", "singaporean"],
        "European Union": ["european union", "eu", "eur-lex", "celex"],
    }

    if hint and hint in country_variants:
        if any(v in title_lower for v in country_variants[hint]):
            return hint

    # Scan title for other countries
    for country, variants in country_variants.items():
        if any(v in title_lower for v in variants):
            return country

    # Conservative check in abstract (must appear at least twice to avoid casual comparisons)
    if hint and hint in country_variants:
        if any(abstract_lower.count(v) >= 2 for v in country_variants[hint]):
            return hint

    for country, variants in country_variants.items():
        if any(abstract_lower.count(v) >= 2 for v in variants):
            return country

    return "United States"  # Default for Federal Register




# ═══════════════════════════════════════════════════════════════════
# SOURCE 1: EUR-Lex SPARQL API (European Union Legislation)
# ═══════════════════════════════════════════════════════════════════

EURLEX_SEARCH_TERMS = [
    ("artificial intelligence", "AI Governance"),
    ("cybersecurity", "Cybersecurity"),
    ("cyber resilience", "Cybersecurity"),
    ("data protection", "Data Privacy"),
    ("privacy", "Data Privacy"),
    ("digital services", "Data Privacy"),
    ("digital markets", "Data Privacy"),
    ("electronic communications", "Data Privacy"),
    ("financial technology", "Financial Regulation"),
    ("crypto-assets", "Financial Regulation"),
    ("sustainability reporting", "ESG Policies"),
    ("environmental taxonomy", "ESG Policies"),
    ("medical devices", "Healthcare AI"),
    ("health data", "Healthcare AI"),
    ("robotics", "IoT and Robotics"),
    ("internet of things", "IoT and Robotics"),
    ("machinery safety", "IoT and Robotics"),
    ("product safety", "IoT and Robotics"),
    ("workplace safety", "POSH Policies"),
    ("equal treatment", "POSH Policies"),
]


def _sparql_search(keyword: str, limit: int = 15) -> list:
    """Search EUR-Lex CELLAR for legislation matching a keyword."""
    query = f"""
    PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    SELECT DISTINCT ?celex ?title ?date WHERE {{
      ?work cdm:resource_legal_id_celex ?celex ;
            cdm:work_title ?title ;
            cdm:work_date_document ?date .
      FILTER(LANG(?title) = "en")
      FILTER(CONTAINS(LCASE(?title), "{keyword.lower()}"))
    }}
    ORDER BY DESC(?date)
    LIMIT {limit}
    """
    try:
        resp = requests.get(
            EURLEX_SPARQL_ENDPOINT,
            params={"query": query},
            headers={"Accept": "application/sparql-results+json"},
            timeout=20,
        )
        resp.raise_for_status()
        bindings = resp.json().get("results", {}).get("bindings", [])
        results = []
        for b in bindings:
            results.append({
                "celex": b["celex"]["value"],
                "title": b["title"]["value"],
                "date": b.get("date", {}).get("value", ""),
            })
        return results
    except Exception as e:
        print(f"    SPARQL search failed for '{keyword}': {e}")
        return []


def fetch_from_eurlex() -> list:
    """
    LIVE: Fetch EU legislation from EUR-Lex via SPARQL API.
    Searches across all relevant sectors using keyword queries.
    """
    print("\n[EURLEX] Fetching EU legislation via SPARQL API...")
    policies = []
    seen_celex = set()

    for keyword, default_sector in EURLEX_SEARCH_TERMS:
        results = _sparql_search(keyword, limit=15)
        
        for doc in results:
            celex = doc["celex"]
            if celex in seen_celex:
                continue
            seen_celex.add(celex)
            
            title = (doc.get("title") or "Untitled EU Legislation")[:250]
            year = None
            if doc.get("date"):
                try:
                    year = int(doc["date"][:4])
                except (ValueError, IndexError):
                    pass

            # Re-classify from title for accuracy
            sector = _classify_sector(title) 
            if sector is None:
                sector = default_sector  # Use search-term hint if classifier can't match
            
            source_url = f"https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:{celex}"
            
            # Build substantive content from title + metadata
            content = (
                f"{title}. "
                f"European Union {sector} legislation (CELEX: {celex}). "
                f"This regulation addresses key aspects of {sector.lower()} within the EU regulatory framework. "
                f"Full official text available at EUR-Lex: {source_url}"
            )
            
            # Extract meaningful tags from title
            tags = _extract_tags_from_title(title, sector)
            
            policy = {
                "id": generate_id("eurlex", celex, "European Union"),
                "title": title,
                "sector": sector,
                "region": "Europe",
                "country": "European Union",
                "content": content,
                "tags": tags,
                "status": "Active",
                "year": year,
                "version": "1.0",
                "source_url": source_url,
            }
            policies.append(policy)

    print(f"  [OK] EUR-Lex: {len(policies)} unique policies fetched across {len(EURLEX_SEARCH_TERMS)} keyword searches")
    return policies


def _extract_tags_from_title(title: str, sector: str) -> list:
    """Extract meaningful tags from a policy title."""
    tags = [sector.lower()] if sector else []
    t = title.lower()
    
    tag_keywords = {
        "regulation": "regulation", "directive": "directive", "decision": "decision",
        "recommendation": "recommendation", "proposal": "proposal",
        "artificial intelligence": "artificial intelligence", "cybersecurity": "cybersecurity",
        "data protection": "data protection", "privacy": "privacy",
        "digital": "digital", "electronic": "electronic communications",
        "financial": "financial regulation", "crypto": "cryptocurrency",
        "sustainability": "sustainability", "environmental": "environmental",
        "safety": "safety", "consumer": "consumer protection",
        "transparency": "transparency", "accountability": "accountability",
        "risk": "risk management", "security": "security",
        "health": "health", "medical": "medical devices",
        "robot": "robotics", "iot": "IoT",
    }
    
    for keyword, tag in tag_keywords.items():
        if keyword in t and tag not in tags:
            tags.append(tag)
    
    return tags[:8]  # Cap at 8 tags


# ═══════════════════════════════════════════════════════════════════
# SOURCE 2: CISA Known Exploited Vulnerabilities (US Cybersecurity)
# ═══════════════════════════════════════════════════════════════════

def fetch_from_cisa() -> list:
    """
    LIVE: Fetch CISA Known Exploited Vulnerabilities catalog.
    Groups recent advisories by vendor for meaningful policy-level entries.
    """
    print("\n[CISA] Fetching cybersecurity vulnerability catalog...")
    policies = []

    try:
        resp = requests.get(CISA_KEV_URL, timeout=20)
        resp.raise_for_status()
        data = resp.json()

        catalog_version = data.get("catalogVersion", "unknown")
        vulnerabilities = data.get("vulnerabilities", [])

        # Take the most recent 50 vulnerabilities and group by vendor
        recent = sorted(
            vulnerabilities,
            key=lambda v: v.get("dateAdded", ""),
            reverse=True
        )[:50]

        vendor_groups = {}
        for v in recent:
            vendor = v.get("vendorProject", "Unknown")
            if vendor not in vendor_groups:
                vendor_groups[vendor] = []
            vendor_groups[vendor].append(v)

        for vendor, vulns in vendor_groups.items():
            vuln_details = []
            for v in vulns[:5]:
                vuln_details.append(
                    f"- {v.get('cveID', 'N/A')}: {v.get('vulnerabilityName', 'Unknown')} "
                    f"({v.get('product', 'Unknown')} - {v.get('shortDescription', '')[:150]})"
                )

            latest_date = max(v.get("dateAdded", "") for v in vulns)
            year = None
            if latest_date:
                try:
                    year = int(latest_date[:4])
                except (ValueError, IndexError):
                    pass

            title = f"CISA KEV: {vendor} - {len(vulns)} Known Exploited Vulnerabilities"
            content = (
                f"CISA Known Exploited Vulnerabilities (KEV) catalog entries for {vendor}. "
                f"The Cybersecurity and Infrastructure Security Agency (CISA) maintains this catalog of "
                f"vulnerabilities known to be actively exploited. Federal agencies must remediate these "
                f"within mandated timelines under Binding Operational Directive 22-01. "
                f"Catalog version: {catalog_version}. "
                f"Vulnerabilities:\n" + "\n".join(vuln_details) + "\n"
                f"Remediation is mandatory for US federal agencies and recommended for all organizations."
            )

            policy = {
                "id": generate_id("cisa", title, "United States"),
                "title": title,
                "sector": "Cybersecurity",
                "region": "North America",
                "country": "United States",
                "content": content,
                "tags": ["vulnerability management", "incident reporting", "critical infrastructure",
                         "mandatory remediation", "BOD 22-01", vendor.lower()],
                "status": "Active",
                "year": year,
                "version": catalog_version,
                "source_url": "https://www.cisa.gov/known-exploited-vulnerabilities-catalog",
            }
            policies.append(policy)

        print(f"  [OK] CISA KEV: {len(policies)} vendor advisory groups from {len(vulnerabilities)} total vulnerabilities")

    except requests.exceptions.Timeout:
        print("  [WARN] CISA KEV: Request timed out")
    except requests.exceptions.ConnectionError:
        print("  [WARN] CISA KEV: Connection failed (no internet?)")
    except Exception as e:
        print(f"  [WARN] CISA KEV: Fetch failed - {e}")

    return policies


# ═══════════════════════════════════════════════════════════════════
# SOURCE 3: US Federal Register API (US Regulations & Executive Orders)
# ═══════════════════════════════════════════════════════════════════

FEDERAL_REGISTER_SEARCHES = [
    # (search_term, sector, pages_to_fetch, country_hint)
    # ── US Generic (domestic policies) ──
    ("artificial intelligence policy", "AI Governance", 2, None),
    ("artificial intelligence executive order", "AI Governance", 1, None),
    ("cybersecurity framework", "Cybersecurity", 2, None),
    ("cybersecurity executive order", "Cybersecurity", 1, None),
    ("data privacy regulation", "Data Privacy", 2, None),
    ("consumer data protection", "Data Privacy", 1, None),
    ("biometric privacy", "Data Privacy", 1, None),
    ("healthcare AI regulation", "Healthcare AI", 1, None),
    ("medical device software", "Healthcare AI", 1, None),
    ("financial technology regulation", "Financial Regulation", 1, None),
    ("cryptocurrency regulation", "Financial Regulation", 1, None),
    ("anti-money laundering", "Financial Regulation", 1, None),
    ("IoT security", "IoT and Robotics", 1, None),
    ("autonomous vehicle regulation", "IoT and Robotics", 1, None),
    ("drone regulation", "IoT and Robotics", 1, None),
    ("ESG disclosure", "ESG Policies", 1, None),
    ("climate risk financial", "ESG Policies", 1, None),
    ("sustainability reporting", "ESG Policies", 1, None),
    ("workplace harassment", "POSH Policies", 1, None),
    ("equal employment opportunity", "POSH Policies", 1, None),
    ("whistleblower protection", "POSH Policies", 1, None),
    # ── India ──
    ("India data protection regulation", "Data Privacy", 1, "India"),
    ("India cybersecurity policy", "Cybersecurity", 1, "India"),
    ("India artificial intelligence", "AI Governance", 1, "India"),
    ("India digital regulation trade", "AI Governance", 1, "India"),
    # ── China ──
    ("China cybersecurity law regulation", "Cybersecurity", 1, "China"),
    ("China data privacy regulation", "Data Privacy", 1, "China"),
    ("China artificial intelligence regulation", "AI Governance", 1, "China"),
    ("China financial technology regulation", "Financial Regulation", 1, "China"),
    # ── Brazil ──
    ("Brazil data protection LGPD", "Data Privacy", 1, "Brazil"),
    ("Brazil cybersecurity regulation", "Cybersecurity", 1, "Brazil"),
    ("Brazil ESG sustainability", "ESG Policies", 1, "Brazil"),
    # ── Japan ──
    ("Japan data privacy protection act", "Data Privacy", 1, "Japan"),
    ("Japan cybersecurity strategy", "Cybersecurity", 1, "Japan"),
    ("Japan artificial intelligence", "AI Governance", 1, "Japan"),
    ("Japan robotics regulation", "IoT and Robotics", 1, "Japan"),
    # ── United Kingdom ──
    ("United Kingdom data protection GDPR", "Data Privacy", 1, "United Kingdom"),
    ("United Kingdom cybersecurity strategy", "Cybersecurity", 1, "United Kingdom"),
    ("United Kingdom AI regulation", "AI Governance", 1, "United Kingdom"),
    ("United Kingdom financial conduct", "Financial Regulation", 1, "United Kingdom"),
    # ── Australia ──
    ("Australia privacy act regulation", "Data Privacy", 1, "Australia"),
    ("Australia cybersecurity strategy", "Cybersecurity", 1, "Australia"),
    ("Australia critical infrastructure", "Cybersecurity", 1, "Australia"),
    # ── Canada ──
    ("Canada privacy regulation PIPEDA", "Data Privacy", 1, "Canada"),
    ("Canada cybersecurity strategy", "Cybersecurity", 1, "Canada"),
    ("Canada artificial intelligence", "AI Governance", 1, "Canada"),
    # ── South Korea ──
    ("South Korea data protection regulation", "Data Privacy", 1, "South Korea"),
    ("South Korea cybersecurity", "Cybersecurity", 1, "South Korea"),
    ("South Korea artificial intelligence", "AI Governance", 1, "South Korea"),
    # ── Singapore ──
    ("Singapore data protection PDPA", "Data Privacy", 1, "Singapore"),
    ("Singapore cybersecurity act", "Cybersecurity", 1, "Singapore"),
    ("Singapore fintech regulation", "Financial Regulation", 1, "Singapore"),
    # ── Germany / France (EU leaders) ──
    ("Germany data protection regulation", "Data Privacy", 1, "Germany"),
    ("France artificial intelligence strategy", "AI Governance", 1, "France"),
    # ── Middle East ──
    ("Saudi Arabia data regulation", "Data Privacy", 1, "Saudi Arabia"),
    ("UAE artificial intelligence strategy", "AI Governance", 1, "United Arab Emirates"),
    ("UAE financial regulation", "Financial Regulation", 1, "United Arab Emirates"),
    # ── Africa ──
    ("Nigeria data protection regulation", "Data Privacy", 1, "Nigeria"),
    ("Kenya data protection act", "Data Privacy", 1, "Kenya"),
    ("South Africa protection personal information", "Data Privacy", 1, "South Africa"),
    # ── Latin America ──
    ("Mexico data protection regulation", "Data Privacy", 1, "Mexico"),
    ("Argentina data protection", "Data Privacy", 1, "Argentina"),
    # ── Southeast Asia ──
    ("Indonesia data protection regulation", "Data Privacy", 1, "Indonesia"),
]

# Country-to-region mapping
COUNTRY_REGIONS = {
    "United States": "North America",
    "Canada": "North America",
    "Mexico": "North America",
    "European Union": "Europe",
    "Germany": "Europe",
    "France": "Europe",
    "United Kingdom": "Europe",
    "India": "Asia",
    "China": "Asia",
    "Japan": "Asia",
    "South Korea": "Asia",
    "Singapore": "Asia",
    "Indonesia": "Asia",
    "Australia": "Oceania",
    "Brazil": "South America",
    "Argentina": "South America",
    "Nigeria": "Africa",
    "Kenya": "Africa",
    "South Africa": "Africa",
    "Saudi Arabia": "Middle East",
    "United Arab Emirates": "Middle East",
}


def _fetch_federal_register_page(term: str, page: int = 1, per_page: int = 20) -> list:
    """Fetch one page of Federal Register results."""
    try:
        resp = requests.get(
            FEDERAL_REGISTER_URL,
            params={
                "conditions[term]": term,
                "per_page": per_page,
                "page": page,
                "order": "relevance",
                "fields[]": ["title", "abstract", "publication_date", "type",
                             "document_number", "html_url", "agencies"]
            },
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json().get("results", [])
    except Exception as e:
        print(f"    Federal Register fetch failed for '{term}' page {page}: {e}")
        return []


def fetch_from_federal_register() -> list:
    """
    LIVE: Fetch regulatory documents from the Federal Register API.
    Covers US domestic policy + international/bilateral policy mentioning 20+ countries.
    """
    print("\n[FEDREG] Fetching Federal Register documents (US + global)...")
    policies = []
    seen_doc_numbers = set()

    for term, default_sector, pages, country_hint in FEDERAL_REGISTER_SEARCHES:
        for page in range(1, pages + 1):
            results = _fetch_federal_register_page(term, page=page)
            
            for doc in results:
                doc_number = doc.get("document_number", "")
                if not doc_number or doc_number in seen_doc_numbers:
                    continue
                seen_doc_numbers.add(doc_number)

                title = doc.get("title", "Untitled")[:250]
                abstract = doc.get("abstract") or ""
                pub_date = doc.get("publication_date", "")
                doc_type = doc.get("type", "Document")
                html_url = doc.get("html_url", "")

                # RELEVANCE FILTER: Skip documents not related to our sectors
                # (e.g., tire tariffs, food import quotas, commodity trade)
                if not _is_policy_relevant(title, abstract):
                    continue

                year = None
                if pub_date:
                    try:
                        year = int(pub_date[:4])
                    except (ValueError, IndexError):
                        pass

                # Get agency names
                agencies = doc.get("agencies", [])
                agency_names = ", ".join(
                    a.get("name", "") for a in agencies if a.get("name")
                )[:200] if agencies else "US Federal Government"

                # Classify sector from actual content — MUST match a known sector
                sector = _classify_sector(title, abstract)
                if sector is None:
                    continue  # Skip: document doesn't match any of our 8 policy sectors

                # Determine country: use hint if provided, else detect from title/abstract
                country = _detect_country(title, abstract, country_hint)
                region = COUNTRY_REGIONS.get(country, "North America")

                content = (
                    f"{title}. "
                    f"{doc_type} published in the US Federal Register on {pub_date}. "
                    f"Issuing agency: {agency_names}. "
                    f"{abstract[:500] if abstract else ''} "
                    f"Document number: {doc_number}. "
                    f"Full text: {html_url}"
                )

                tags = _extract_tags_from_title(title, sector)
                if doc_type.lower() in ["executive order", "presidential document"]:
                    tags.append("executive order")
                if country_hint and country_hint.lower() not in [t.lower() for t in tags]:
                    tags.append(country_hint.lower())

                policy = {
                    "id": generate_id("fedreg", doc_number, country),
                    "title": title,
                    "sector": sector,
                    "region": region,
                    "country": country,
                    "content": content,
                    "tags": tags,
                    "status": "Active",
                    "year": year,
                    "version": "1.0",
                    "source_url": html_url,
                }
                policies.append(policy)

    print(f"  [OK] Federal Register: {len(policies)} unique documents across {len(FEDERAL_REGISTER_SEARCHES)} search terms")
    return policies


# ═══════════════════════════════════════════════════════════════════
# DYNAMIC CUSTOM SOURCE CRAWLER
# ═══════════════════════════════════════════════════════════════════

def fetch_from_custom_source(source: dict) -> list:
    """
    Fetch and parse policies from a dynamically added admin source (JSON API, RSS Feed, or Web Scraper).
    """
    source_id = source.get("id")
    name = source.get("name", "Custom Source")
    url = source.get("url", "")
    source_type = source.get("source_type", "web_scraper")
    default_country = source.get("country") or "Global"
    default_sector = source.get("sector") or "All"
    
    print(f"\n[DYNAMIC SOURCE] Crawling '{name}' ({url})...")
    policies = []

    try:
        headers = {
            "User-Agent": "PolicyIQ-Crawler/2.0 (Legal-Policy-Intelligence-Bot; +http://policyiq.ai)"
        }
        resp = requests.get(url, headers=headers, timeout=20)
        resp.raise_for_status()

        # 1. RSS / Atom Feed Parsing
        if source_type == "rss_feed" or "xml" in resp.headers.get("content-type", "") or "<rss" in resp.text.lower() or "<feed" in resp.text.lower():
            try:
                import xml.etree.ElementTree as ET
                import re
                root = ET.fromstring(resp.text)
                items = root.findall(".//item") or root.findall(".//{http://www.w3.org/2005/Atom}entry")
                for item in items[:25]:
                    title_elem = item.find("title") or item.find("{http://www.w3.org/2005/Atom}title")
                    link_elem = item.find("link") or item.find("{http://www.w3.org/2005/Atom}link")
                    desc_elem = item.find("description") or item.find("summary") or item.find("{http://www.w3.org/2005/Atom}summary")
                    
                    title = (title_elem.text if title_elem is not None and title_elem.text else "Untitled Policy")[:250]
                    link = link_elem.text if link_elem is not None and link_elem.text else url
                    if link_elem is not None and "href" in link_elem.attrib:
                        link = link_elem.attrib["href"]
                    
                    content_text = desc_elem.text if desc_elem is not None and desc_elem.text else title
                    clean_content = re.sub(r'<[^>]+>', ' ', content_text).strip()
                    
                    sector = _classify_sector(title, clean_content) or (default_sector if default_sector != "All" else "Data Privacy")
                    country = _detect_country(title, clean_content, hint=default_country if default_country != "Global" else None) or default_country
                    region = COUNTRY_REGIONS.get(country, "Global")

                    policy = {
                        "id": generate_id(f"custom_{source_id}", title, country),
                        "title": title,
                        "sector": sector,
                        "region": region,
                        "country": country,
                        "content": f"{title}. Source: {name}. {clean_content[:800]} Full text: {link}",
                        "tags": _extract_tags_from_title(title, sector),
                        "status": "Active",
                        "year": datetime.now().year,
                        "version": "1.0",
                        "source_url": link
                    }
                    policies.append(policy)
            except Exception as e:
                print(f"    RSS parsing error for '{name}': {e}")

        # 2. JSON API Parsing
        elif source_type == "json_api" or "json" in resp.headers.get("content-type", ""):
            try:
                data = resp.json()
                docs = []
                if isinstance(data, list):
                    docs = data
                elif isinstance(data, dict):
                    for k, v in data.items():
                        if isinstance(v, list):
                            docs = v
                            break
                
                for item in docs[:30]:
                    if not isinstance(item, dict):
                        continue
                    title = str(item.get("title") or item.get("name") or item.get("headline") or "Untitled Document")[:250]
                    link = str(item.get("url") or item.get("link") or item.get("html_url") or url)
                    content_text = str(item.get("abstract") or item.get("description") or item.get("content") or title)
                    
                    sector = _classify_sector(title, content_text) or (default_sector if default_sector != "All" else "Data Privacy")
                    country = _detect_country(title, content_text, hint=default_country if default_country != "Global" else None) or default_country
                    region = COUNTRY_REGIONS.get(country, "Global")

                    policy = {
                        "id": generate_id(f"custom_{source_id}", title, country),
                        "title": title,
                        "sector": sector,
                        "region": region,
                        "country": country,
                        "content": f"{title}. Published by {name}. {content_text[:800]} Link: {link}",
                        "tags": _extract_tags_from_title(title, sector),
                        "status": "Active",
                        "year": datetime.now().year,
                        "version": "1.0",
                        "source_url": link
                    }
                    policies.append(policy)
            except Exception as e:
                print(f"    JSON parsing error for '{name}': {e}")

        # 3. Web Page HTML Scraper
        else:
            try:
                from urllib.parse import urljoin
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(resp.text, 'html.parser')
                
                page_title = soup.title.string.strip() if soup.title and soup.title.string else name
                anchors = soup.find_all('a', href=True)
                policy_links = []
                for a in anchors:
                    txt = a.get_text(strip=True)
                    href = a['href']
                    if len(txt) > 12 and any(kw in txt.lower() for kw in ['policy', 'act', 'regulation', 'law', 'guideline', 'directive', 'order', 'standard', 'framework', 'data', 'ai', 'security', 'privacy']):
                        full_href = urljoin(url, href)
                        policy_links.append((txt[:250], full_href))

                if policy_links:
                    for txt, href in policy_links[:20]:
                        sector = _classify_sector(txt) or (default_sector if default_sector != "All" else "Data Privacy")
                        country = _detect_country(txt, "", hint=default_country if default_country != "Global" else None) or default_country
                        region = COUNTRY_REGIONS.get(country, "Global")

                        policy = {
                            "id": generate_id(f"custom_{source_id}", txt, country),
                            "title": txt,
                            "sector": sector,
                            "region": region,
                            "country": country,
                            "content": f"{txt}. Official policy resource crawled from {name} ({url}). Full documentation link: {href}",
                            "tags": _extract_tags_from_title(txt, sector),
                            "status": "Active",
                            "year": datetime.now().year,
                            "version": "1.0",
                            "source_url": href
                        }
                        policies.append(policy)
                else:
                    paragraphs = [p.get_text(strip=True) for p in soup.find_all('p') if len(p.get_text(strip=True)) > 40]
                    body_text = " ".join(paragraphs[:10])
                    
                    sector = _classify_sector(page_title, body_text) or (default_sector if default_sector != "All" else "Data Privacy")
                    country = _detect_country(page_title, body_text, hint=default_country if default_country != "Global" else None) or default_country
                    region = COUNTRY_REGIONS.get(country, "Global")

                    policy = {
                        "id": generate_id(f"custom_{source_id}", page_title, country),
                        "title": page_title[:250],
                        "sector": sector,
                        "region": region,
                        "country": country,
                        "content": f"{page_title}. Official regulatory domain: {name}. {body_text[:1000]} Source URL: {url}",
                        "tags": _extract_tags_from_title(page_title, sector),
                        "status": "Active",
                        "year": datetime.now().year,
                        "version": "1.0",
                        "source_url": url
                    }
                    policies.append(policy)

            except Exception as e:
                print(f"    Web scraping error for '{name}': {e}")

        print(f"  [OK] Custom Source '{name}': {len(policies)} policies extracted")
    except Exception as e:
        print(f"  [WARN] Failed to fetch custom source '{name}': {e}")

    return policies


def test_crawl_source(source: dict) -> list:
    """Helper used by admin test endpoint."""
    return fetch_from_custom_source(source)


# ═══════════════════════════════════════════════════════════════════
# ORCHESTRATOR
# ═══════════════════════════════════════════════════════════════════

def run_full_fetch() -> dict:
    """
    Master fetch orchestrator.
    Executes live government endpoints + all admin-provisioned trusted sources in DB.
    """
    global _last_fetch_result
    from app.services.progress_service import update_progress

    update_progress(status="fetching", task_name="Multi-source policy fetch", total=4, processed=0, current_title="Connecting to EUR-Lex...")

    print("\n" + "=" * 60)
    print("POLICY INTELLIGENCE PIPELINE - Multi-source live fetch")
    print("=" * 60)

    source_results = {
        "eurlex":   {"status": "pending", "count": 0, "inserted": 0},
        "cisa":     {"status": "pending", "count": 0, "inserted": 0},
        "fedreg":   {"status": "pending", "count": 0, "inserted": 0},
    }

    total_inserted = 0
    total_duplicates = 0

    # 1. EUR-Lex SPARQL (EU Legislation)
    try:
        eurlex_policies = fetch_from_eurlex()
        source_results["eurlex"]["count"] = len(eurlex_policies)
        source_results["eurlex"]["status"] = "success"
        for p in eurlex_policies:
            if save_policy(p):
                total_inserted += 1
                source_results["eurlex"]["inserted"] += 1
            else:
                total_duplicates += 1
    except Exception as e:
        source_results["eurlex"]["status"] = f"failed: {str(e)[:100]}"
        print(f"  [ERROR] EUR-Lex pipeline failed: {e}")

    # 2. CISA KEV (US Cybersecurity)
    try:
        update_progress(processed=1, current_title="Fetching from CISA KEV...")
        cisa_policies = fetch_from_cisa()
        source_results["cisa"]["count"] = len(cisa_policies)
        source_results["cisa"]["status"] = "success"
        for p in cisa_policies:
            if save_policy(p):
                total_inserted += 1
                source_results["cisa"]["inserted"] += 1
            else:
                total_duplicates += 1
    except Exception as e:
        source_results["cisa"]["status"] = f"failed: {str(e)[:100]}"
        print(f"  [ERROR] CISA pipeline failed: {e}")

    # 3. Federal Register (US Regulations)
    try:
        update_progress(processed=2, current_title="Fetching from Federal Register...")
        fedreg_policies = fetch_from_federal_register()
        source_results["fedreg"]["count"] = len(fedreg_policies)
        source_results["fedreg"]["status"] = "success"
        for p in fedreg_policies:
            if save_policy(p):
                total_inserted += 1
                source_results["fedreg"]["inserted"] += 1
            else:
                total_duplicates += 1
    except Exception as e:
        source_results["fedreg"]["status"] = f"failed: {str(e)[:100]}"
        print(f"  [ERROR] Federal Register pipeline failed: {e}")

    # 4. Admin-configured Trusted Sources from DB
    try:
        update_progress(processed=3, current_title="Crawling admin trusted sources...")
        conn = get_connection()
        db_sources = conn.execute(
            "SELECT id, name, url, source_type, description, country, sector FROM trusted_sources WHERE status = 'Active'"
        ).fetchall()
        conn.close()

        for src in db_sources:
            src_dict = dict(src)
            # Skip built-in sources as they were fetched above
            if src_dict["url"] in [EURLEX_SPARQL_ENDPOINT, CISA_KEV_URL, FEDERAL_REGISTER_URL]:
                continue

            src_policies = fetch_from_custom_source(src_dict)
            inserted_count = 0
            for p in src_policies:
                if save_policy(p):
                    total_inserted += 1
                    inserted_count += 1
                else:
                    total_duplicates += 1
            
            source_results[f"source_{src_dict['id']}"] = {
                "name": src_dict["name"],
                "status": "success",
                "count": len(src_policies),
                "inserted": inserted_count
            }

            try:
                conn_u = get_connection()
                conn_u.execute(
                    "UPDATE trusted_sources SET last_crawled_at = NOW(), policies_fetched = policies_fetched + %s WHERE id = %s",
                    (inserted_count, src_dict["id"])
                )
                conn_u.commit()
                conn_u.close()
            except Exception as e:
                print(f"[WARN] Failed to update source stats: {e}")

    except Exception as e:
        print(f"  [ERROR] Dynamic trusted sources pipeline failed: {e}")

    # Summary
    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_fetched": sum(s.get("count", 0) for s in source_results.values()),
        "total_inserted": total_inserted,
        "total_duplicates": total_duplicates,
        "sources": source_results,
    }

    _last_fetch_result = summary

    print(f"\n{'=' * 60}")
    print(f"FETCH COMPLETE")
    print(f"   TOTAL: {total_inserted:>4} inserted, {total_duplicates:>4} duplicates skipped")
    print(f"{'=' * 60}\n")

    if total_inserted > 0:
        try:
            from app.services.cache_service import backend_cache
            backend_cache.clear()
            print("[OK] Backend cache cleared due to new database insertions")
        except Exception as ce:
            print(f"[WARN] Failed to clear backend cache: {ce}")

    update_progress(status="idle", task_name="", total=0, processed=0, current_title="")

    return summary


def get_fetch_status() -> dict:
    """Get current database stats and per-source breakdown."""
    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) FROM policies").fetchone()[0]

    eurlex_count = conn.execute(
        "SELECT COUNT(*) FROM policies WHERE id LIKE 'eurlex_%'"
    ).fetchone()[0]

    cisa_count = conn.execute(
        "SELECT COUNT(*) FROM policies WHERE id LIKE 'cisa_%'"
    ).fetchone()[0]

    fedreg_count = conn.execute(
        "SELECT COUNT(*) FROM policies WHERE id LIKE 'fedreg_%'"
    ).fetchone()[0]

    other_count = total - eurlex_count - cisa_count - fedreg_count

    sectors = conn.execute(
        "SELECT sector, COUNT(*) as count FROM policies GROUP BY sector"
    ).fetchall()
    conn.close()

    return {
        "total_policies": total,
        "live_fetched": eurlex_count + cisa_count + fedreg_count,
        "other": other_count,
        "sources": {
            "eurlex": {"count": eurlex_count, "type": "live", "label": "EUR-Lex SPARQL API"},
            "cisa": {"count": cisa_count, "type": "live", "label": "CISA KEV JSON Feed"},
            "fedreg": {"count": fedreg_count, "type": "live", "label": "US Federal Register API"},
        },
        "sectors": {r["sector"]: r["count"] for r in sectors},
        "last_fetch": _last_fetch_result.get("timestamp"),
        "last_fetch_sources": _last_fetch_result.get("sources", {}),
        "last_updated": datetime.now().isoformat(),
    }