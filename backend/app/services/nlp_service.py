import spacy
import json
from app.database import get_connection

try:
    nlp = spacy.load("en_core_web_md")
    print("✅ spaCy: en_core_web_md loaded")
except OSError:
    nlp = spacy.load("en_core_web_sm")
    print("⚠️ spaCy: falling back to en_core_web_sm")

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


def extract_countries(text: str) -> list:
    if not text:
        return []
    doc = nlp(text)
    found = set()
    for ent in doc.ents:
        if ent.label_ in ("GPE", "LOC", "NORP"):
            name = ent.text.strip()
            if len(name) < 3 or name in EXCLUDE:
                continue
            name = CORRECTIONS.get(name, name)
            if name in KNOWN_COUNTRIES:
                found.add(name)
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
            "SELECT extracted_countries_cache FROM policies WHERE id = ?",
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
            "UPDATE policies SET extracted_countries_cache = ? WHERE id = ?",
            (json.dumps(countries), policy_id)
        )
        conn.commit()
    except Exception:
        pass


def load_policies(sector=None, region=None, search=None, status=None):
    conn = get_connection()
    query = "SELECT * FROM policies WHERE 1=1"
    params = []

    if sector:
        query += " AND sector = ?"
        params.append(sector)
    if region:
        query += " AND region = ?"
        params.append(region)
    if status:
        query += " AND status = ?"
        params.append(status)
    if search:
        query += " AND (title LIKE ? OR content LIKE ? OR country LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])

    rows = conn.execute(query, params).fetchall()

    result = []
    for row in rows:
        p = dict(row)
        p["tags"] = json.loads(p["tags"] or "[]")

        # Use cache — never run spaCy on list view
        cached = _get_cached_countries(p["id"], conn)
        if cached is not None:
            p["extracted_countries"] = cached
        else:
            # Use country field directly for speed
            p["extracted_countries"] = [p["country"]] if p.get("country") else []
            # Save to cache so next time is instant
            _save_cache(p["id"], p["extracted_countries"], conn)

        result.append(p)

    conn.close()
    return result


def get_policy_by_id(policy_id: str):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM policies WHERE id = ?", (policy_id,)
    ).fetchone()

    if not row:
        conn.close()
        return None

    p = dict(row)
    p["tags"] = json.loads(p["tags"] or "[]")

    # Check cache first — return immediately if cached
    cached = _get_cached_countries(p["id"], conn)
    if cached is not None:
        p["extracted_countries"] = cached
        conn.close()
        return p

    # Only run spaCy if no cache exists
    try:
        countries = extract_countries_smart(p)
        p["extracted_countries"] = countries
        _save_cache(p["id"], countries, conn)
    except Exception:
        p["extracted_countries"] = [p.get("country", "")]

    conn.close()
    return p


def prewarm_ner_cache():
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT id, country FROM policies WHERE extracted_countries_cache IS NULL"
        ).fetchall()
        conn.close()

        if not rows:
            print("✅ NER cache already warm")
            return

        print(f"🔄 Pre-warming NER cache for {len(rows)} policies...")
        conn2 = get_connection()
        for row in rows:
            countries = [row["country"]] if row["country"] else []
            _save_cache(row["id"], countries, conn2)
        conn2.close()
        print(f"✅ NER cache warmed for {len(rows)} policies")
    except Exception as e:
        print(f"⚠️ Cache warm failed: {e}")
        try:
            conn.close()
        except Exception:
            pass