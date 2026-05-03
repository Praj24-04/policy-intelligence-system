from collections import Counter
from app.services.nlp_service import load_policies
from app.database import get_connection

def get_country_distribution():
    policies = load_policies()  # Load more for distribution
    counts = Counter()
    for p in policies:
        for c in p["extracted_countries"]:
            counts[c] += 1
    return dict(counts)

def get_sector_distribution():
    conn = get_connection()
    rows = conn.execute("SELECT sector, COUNT(*) as count FROM policies GROUP BY sector").fetchall()
    conn.close()
    return {r["sector"]: r["count"] for r in rows}

def get_region_distribution():
    conn = get_connection()
    rows = conn.execute("SELECT region, COUNT(*) as count FROM policies GROUP BY region").fetchall()
    conn.close()
    return {r["region"]: r["count"] for r in rows}

def get_year_trend():
    conn = get_connection()
    rows = conn.execute("SELECT year, COUNT(*) as count FROM policies WHERE year IS NOT NULL GROUP BY year ORDER BY year").fetchall()
    conn.close()
    return {r["year"]: r["count"] for r in rows}

def get_status_distribution():
    conn = get_connection()
    rows = conn.execute("SELECT status, COUNT(*) as count FROM policies GROUP BY status").fetchall()
    conn.close()
    return {r["status"]: r["count"] for r in rows}

def get_overview():
    conn = get_connection()
    
    total = conn.execute("SELECT COUNT(*) FROM policies").fetchone()[0]
    countries = conn.execute("SELECT COUNT(DISTINCT country) FROM policies").fetchone()[0]
    sectors = conn.execute("SELECT COUNT(DISTINCT sector) FROM policies").fetchone()[0]
    regions = conn.execute("SELECT COUNT(DISTINCT region) FROM policies").fetchone()[0]
    
    conn.close()
    return {
        "total_policies": total,
        "total_countries": countries,
        "total_sectors": sectors,
        "total_regions": regions
    }