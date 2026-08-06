import json
from collections import Counter
from app.database import get_connection

def canonicalize_country(name):
    if not name:
        return None
    n = name.strip()
    nl = n.lower()
    if nl == "united states of america" or nl == "usa" or nl == "us" or nl == "united states":
        return "United States"
    if nl == "united kingdom" or nl == "uk":
        return "United Kingdom"
    if nl == "south korea" or nl == "korea" or nl == "republic of korea":
        return "South Korea"
    return n

def get_country_distribution():
    conn = get_connection()
    rows = conn.execute("SELECT country, extracted_countries_cache FROM policies").fetchall()
    conn.close()
    counts = Counter()
    for r in rows:
        policy_countries = set()
        
        primary_country = canonicalize_country(r["country"])
        if primary_country:
            policy_countries.add(primary_country)
            
        cached_str = r["extracted_countries_cache"]
        if cached_str:
            try:
                extracted = json.loads(cached_str)
                for c in extracted:
                    c_canon = canonicalize_country(c)
                    if c_canon:
                        policy_countries.add(c_canon)
            except Exception:
                pass
                
        for c in policy_countries:
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