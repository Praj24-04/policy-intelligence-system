import spacy
import json
from app.database import get_connection

nlp = spacy.load("en_core_web_sm")

CORRECTIONS = {
    "EU": "European Union", "U.S.": "United States",
    "U.K.": "United Kingdom", "UAE": "United Arab Emirates",
    "UK": "United Kingdom", "US": "United States",
}
EXCLUDE = {"AI", "ICT", "PDPC", "FCA", "CMA", "ICO", "NIST", "CISA",
           "BSI", "CERT", "PPC", "ANPD", "OAIC", "LGPD", "PIPL", "APPI"}

def extract_countries(text: str) -> list:
    doc = nlp(text)
    found = set()
    for ent in doc.ents:
        if ent.label_ in ("GPE", "LOC"):
            name = ent.text.strip()
            if name in EXCLUDE or len(name) < 3:
                continue
            name = CORRECTIONS.get(name, name)
            found.add(name)
    return list(found)

def load_policies(sector=None, region=None, search=None, status=None, limit=10, offset=0):
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

    query += " LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    rows = conn.execute(query, params).fetchall()
    conn.close()

    result = []
    for row in rows:
        p = dict(row)
        p["tags"] = json.loads(p["tags"] or "[]")
        p["extracted_countries"] = extract_countries(p["content"])
        result.append(p)
    return result

def get_policy_by_id(policy_id: str):
    conn = get_connection()
    row = conn.execute("SELECT * FROM policies WHERE id = ?", (policy_id,)).fetchone()
    conn.close()
    if not row:
        return None
    p = dict(row)
    p["tags"] = json.loads(p["tags"] or "[]")
    p["extracted_countries"] = extract_countries(p["content"])
    return p