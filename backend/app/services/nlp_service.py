import spacy
import json
from app.database import get_connection
from app.services.fine_extractor import extract_fines

try:
    nlp = spacy.load("en_core_web_md")
    print("spaCy: en_core_web_md loaded")
except OSError:
    nlp = spacy.load("en_core_web_sm")
    print("spaCy: falling back to en_core_web_sm")

CORRECTIONS = {
    "EU": "European Union", "U.S.": "United States",
    "U.K.": "United Kingdom", "UAE": "United Arab Emirates",
    "UK": "United Kingdom", "US": "United States",
    "E.U.": "European Union", "USA": "United States",
}

EXCLUDE = {
    "AI", "ICT", "PDPC", "FCA", "CMA", "ICO", "NIST", "CISA",
    "BSI", "CERT", "PPC", "ANPD", "OAIC", "LGPD", "PIPL", "APPI",
    "GDPR", "CCPA", "NIS", "ISO", "IEEE", "OECD", "NATO", "UN",
    "WHO", "WTO", "IMF", "G20", "G7", "ENISA", "NITI", "MAS"
}

KNOWN_COUNTRIES = {
    "United States", "European Union", "United Kingdom", "China",
    "India", "Japan", "Germany", "France", "Canada", "Australia",
    "Singapore", "Brazil", "South Korea", "United Arab Emirates",
    "South Africa", "Indonesia", "Nigeria", "Kenya", "Mexico",
    "Argentina", "Saudi Arabia", "Russia", "Israel", "Netherlands",
    "Sweden", "Switzerland", "Italy", "Spain", "Poland", "Turkey",
    "International", "New Zealand", "Thailand", "Vietnam", "Malaysia",
}


import re

# Regex patterns for country abbreviations that spaCy often misses
# (they appear inside org names like "U.S. Department of Commerce")
_COUNTRY_PATTERNS = [
    (re.compile(r'\bU\.S\b\.?|\bUSA\b|\bUnited States\b', re.IGNORECASE), "United States"),
    (re.compile(r'\bU\.K\b\.?|\bUnited Kingdom\b', re.IGNORECASE), "United Kingdom"),
    (re.compile(r'\bE\.U\b\.?|\bEuropean Union\b', re.IGNORECASE), "European Union"),
    (re.compile(r'\bUnited Arab Emirates\b|\bUAE\b', re.IGNORECASE), "United Arab Emirates"),
    (re.compile(r'\bSouth Korea\b|\bRepublic of Korea\b', re.IGNORECASE), "South Korea"),
    (re.compile(r'\bNew Zealand\b', re.IGNORECASE), "New Zealand"),
    (re.compile(r'\bSouth Africa\b', re.IGNORECASE), "South Africa"),
    (re.compile(r'\bSaudi Arabia\b', re.IGNORECASE), "Saudi Arabia"),
    (re.compile(r'\b(?<!\w)China\b', re.IGNORECASE), "China"),
    (re.compile(r'\b(?<!\w)India\b', re.IGNORECASE), "India"),
    (re.compile(r'\b(?<!\w)Japan\b', re.IGNORECASE), "Japan"),
    (re.compile(r'\b(?<!\w)Germany\b', re.IGNORECASE), "Germany"),
    (re.compile(r'\b(?<!\w)France\b', re.IGNORECASE), "France"),
    (re.compile(r'\b(?<!\w)Canada\b', re.IGNORECASE), "Canada"),
    (re.compile(r'\b(?<!\w)Australia\b', re.IGNORECASE), "Australia"),
    (re.compile(r'\b(?<!\w)Singapore\b', re.IGNORECASE), "Singapore"),
    (re.compile(r'\b(?<!\w)Brazil\b', re.IGNORECASE), "Brazil"),
    (re.compile(r'\b(?<!\w)Nigeria\b', re.IGNORECASE), "Nigeria"),
    (re.compile(r'\b(?<!\w)Indonesia\b', re.IGNORECASE), "Indonesia"),
    (re.compile(r'\b(?<!\w)Kenya\b', re.IGNORECASE), "Kenya"),
    (re.compile(r'\b(?<!\w)Mexico\b', re.IGNORECASE), "Mexico"),
    (re.compile(r'\b(?<!\w)Argentina\b', re.IGNORECASE), "Argentina"),
    (re.compile(r'\b(?<!\w)Russia\b|\bRussian Federation\b', re.IGNORECASE), "Russia"),
    (re.compile(r'\b(?<!\w)Israel\b', re.IGNORECASE), "Israel"),
    (re.compile(r'\b(?<!\w)Netherlands\b', re.IGNORECASE), "Netherlands"),
    (re.compile(r'\b(?<!\w)Sweden\b', re.IGNORECASE), "Sweden"),
    (re.compile(r'\b(?<!\w)Switzerland\b', re.IGNORECASE), "Switzerland"),
    (re.compile(r'\b(?<!\w)Italy\b', re.IGNORECASE), "Italy"),
    (re.compile(r'\b(?<!\w)Spain\b', re.IGNORECASE), "Spain"),
    (re.compile(r'\b(?<!\w)Poland\b', re.IGNORECASE), "Poland"),
    (re.compile(r'\b(?<!\w)Turkey\b', re.IGNORECASE), "Turkey"),
    (re.compile(r'\b(?<!\w)Thailand\b', re.IGNORECASE), "Thailand"),
    (re.compile(r'\b(?<!\w)Vietnam\b', re.IGNORECASE), "Vietnam"),
    (re.compile(r'\b(?<!\w)Malaysia\b', re.IGNORECASE), "Malaysia"),
]


def extract_countries(text: str) -> list:
    if not text:
        return []

    found = set()

    # 1. spaCy NER pass — catches explicit GPE/LOC/NORP entities
    doc = nlp(text[:5000])  # limit to first 5000 chars for performance
    for ent in doc.ents:
        if ent.label_ in ("GPE", "LOC", "NORP"):
            name = ent.text.strip()
            if len(name) < 3 or name in EXCLUDE:
                continue
            name = CORRECTIONS.get(name, name)
            if name in KNOWN_COUNTRIES:
                found.add(name)

    # 2. Regex pass — catches abbreviations inside org names (e.g. "U.S. Department of Commerce")
    #    Uses a smaller sample of the document for speed
    sample = text[:3000]
    for pattern, canonical in _COUNTRY_PATTERNS:
        if pattern.search(sample):
            found.add(canonical)

    return list(found)


def extract_countries_smart(policy: dict) -> list:
    policy_id = policy.get("id", "")
    country_field = policy.get("country", "")
    content = policy.get("content", "")

    if not policy_id.startswith("live_"):
        countries = set()
        if country_field and country_field != "Unknown":
            countries.add(country_field)
        if content:
            try:
                doc = nlp(content[:300])
                for ent in doc.ents:
                    if ent.label_ in ("GPE", "LOC"):
                        name = ent.text.strip()
                        if len(name) >= 3 and name not in EXCLUDE:
                            name = CORRECTIONS.get(name, name)
                            if name in KNOWN_COUNTRIES:
                                countries.add(name)
            except Exception:
                pass
        return list(countries)
    else:
        countries = set()
        if country_field and country_field != "Unknown":
            countries.add(country_field)
        if content:
            try:
                ner_countries = extract_countries(content[:800])
                countries.update(ner_countries)
            except Exception:
                pass
        return list(countries) if countries else [country_field]


def _get_cached_countries(policy_id: str, conn) -> list:
    try:
        row = conn.execute(
            "SELECT extracted_countries_cache FROM policies WHERE id = %s",
            (policy_id,)
        ).fetchone()
        if row and row["extracted_countries_cache"]:
            return json.loads(row["extracted_countries_cache"])
    except Exception:
        pass
    return None


def _save_cache(policy_id: str, countries: list, conn):
    try:
        conn.execute(
            "UPDATE policies SET extracted_countries_cache = %s WHERE id = %s",
            (json.dumps(countries), policy_id)
        )
        conn.commit()
    except Exception:
        pass


def _parse_tags(raw_tags):
    """Parse tags from either JSON string or PostgreSQL array format."""
    if not raw_tags:
        return []
    if isinstance(raw_tags, list):
        return raw_tags
    raw_tags = str(raw_tags).strip()
    # Try JSON first
    try:
        parsed = json.loads(raw_tags)
        if isinstance(parsed, list):
            return parsed
    except (json.JSONDecodeError, ValueError):
        pass
    # Handle PostgreSQL array format: {tag1,"tag two",tag3}
    if raw_tags.startswith("{") and raw_tags.endswith("}"):
        inner = raw_tags[1:-1]
        tags = []
        current = ""
        in_quotes = False
        for ch in inner:
            if ch == '"':
                in_quotes = not in_quotes
            elif ch == ',' and not in_quotes:
                tags.append(current.strip().strip('"'))
                current = ""
            else:
                current += ch
        if current.strip():
            tags.append(current.strip().strip('"'))
        return tags
    # Fallback: comma-separated
    return [t.strip() for t in raw_tags.split(",") if t.strip()]


def load_policies(sector=None, region=None, search=None, status=None):
    conn = get_connection()
    query = """
        SELECT id, title, sector, region, country, 
               SUBSTRING(content FROM 1 FOR 400) AS content, 
               tags, status, year, version, source_url, 
               key_requirements, timeline_phases, extracted_countries_cache,
               cluster_id, cluster_confidence, embedding_model, last_embedded_at
        FROM policies WHERE 1=1
    """
    params = []

    if sector:
        query += " AND sector = %s"
        params.append(sector)
    if region:
        query += " AND region = %s"
        params.append(region)
    if status:
        query += " AND status = %s"
        params.append(status)
    if search:
        query += " AND (title LIKE %s OR content LIKE %s OR country LIKE %s)"
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])

    rows = conn.execute(query, params).fetchall()

    result = []
    for row in rows:
        p = dict(row)
        p["tags"] = _parse_tags(p.get("tags"))
        p["tags"] = rank_tags_by_frequency(p)

        cached_str = p.get("extracted_countries_cache")
        if cached_str:
            try:
                p["extracted_countries"] = json.loads(cached_str)
            except Exception:
                p["extracted_countries"] = [p["country"]] if p.get("country") else []
        else:
            p["extracted_countries"] = [p["country"]] if p.get("country") else []

        result.append(p)

    conn.close()
    return result


def get_policy_by_id(policy_id: str):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM policies WHERE id = %s", (policy_id,)
    ).fetchone()

    if not row:
        conn.close()
        return None

    p = dict(row)
    p["tags"] = _parse_tags(p.get("tags"))
    p["tags"] = rank_tags_by_frequency(p)

    cached_str = p.get("extracted_countries_cache")
    if cached_str:
        try:
            p["extracted_countries"] = json.loads(cached_str)
        except Exception:
            p["extracted_countries"] = [p.get("country", "")]
    else:
        try:
            countries = extract_countries_smart(p)
            p["extracted_countries"] = countries
            _save_cache(p["id"], countries, conn)
        except Exception:
            p["extracted_countries"] = [p.get("country", "")]

    p["penalty_fines"] = extract_fines(p.get("content", "")) 
    conn.close()
    return p

def rank_tags_by_frequency(policy: dict) -> list:
    """
    Ranks tags by how frequently the tag concept appears in policy content.
    Most discussed tag appears first.
    """
    content = policy.get("content", "").lower()
    tags = policy.get("tags", [])

    if not tags or not content:
        return tags

    # Count occurrences of each tag concept in content
    tag_scores = []
    for tag in tags:
        # Count direct mentions
        direct_count = content.count(tag.lower())

        # Count related word mentions
        words = tag.lower().split()
        word_count = sum(content.count(w) for w in words if len(w) > 3)

        total_score = direct_count * 2 + word_count
        tag_scores.append((tag, total_score))

    # Sort by score descending
    tag_scores.sort(key=lambda x: -x[1])
    return [tag for tag, score in tag_scores]


def prewarm_ner_cache():
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM policies WHERE extracted_countries_cache IS NULL"
        ).fetchall()
        conn.close()

        if not rows:
            print("[OK] NER cache already warm")
            return

        print(f"[NER] Pre-warming NER cache for {len(rows)} policies...")
        conn2 = get_connection()
        for row in rows:
            p = dict(row)
            try:
                countries = extract_countries_smart(p)
            except Exception:
                countries = [p.get("country")] if p.get("country") else []
            _save_cache(p["id"], countries, conn2)
        conn2.close()
        print(f"[OK] NER cache warmed for {len(rows)} policies")
    except Exception as e:
        print(f"[WARN] Cache warm failed: {e}")
        try:
            conn.close()
        except Exception:
            pass