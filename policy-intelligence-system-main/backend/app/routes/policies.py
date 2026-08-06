from fastapi import APIRouter, HTTPException
from typing import Optional
from app.services.nlp_service import load_policies, get_policy_by_id
from app.services.cache_service import backend_cache

router = APIRouter()

@router.get("/")
def get_policies(
    sector: Optional[str] = None,
    region: Optional[str] = None,
    search: Optional[str] = None,
    status: Optional[str] = None,
    country: Optional[str] = None,
):
    cache_key = f"policies:{sector}:{region}:{search}:{status}:{country}"
    cached = backend_cache.get(cache_key)
    if cached is not None:
        return cached

    res = load_policies(sector=sector, region=region, search=search, status=status, country=country)
    backend_cache.set(cache_key, res)
    return res

@router.get("/sectors")
def get_sectors():
    cache_key = "policies:sectors"
    cached = backend_cache.get(cache_key)
    if cached is not None:
        return cached

    default_sectors = {
        "AI Governance", "Cybersecurity", "Data Privacy",
        "Healthcare AI", "Financial Regulation",
        "POSH Policies", "ESG Policies", "IoT and Robotics"
    }

    from app.database import get_connection
    conn = get_connection()
    try:
        rows = conn.execute("SELECT DISTINCT sector FROM policies WHERE sector IS NOT NULL").fetchall()
        for r in rows:
            if r["sector"]:
                default_sectors.add(r["sector"].strip())
        
        custom_rows = conn.execute("SELECT name FROM custom_sectors WHERE status = 'Active'").fetchall()
        for r in custom_rows:
            if r["name"]:
                default_sectors.add(r["name"].strip())
    except Exception as e:
        print(f"[WARN] Failed to query sectors from policies: {e}")
    finally:
        conn.close()

    res = sorted(list(default_sectors))
    backend_cache.set(cache_key, res)
    return res

@router.get("/regions")
def get_regions():
    cache_key = "policies:regions"
    cached = backend_cache.get(cache_key)
    if cached is not None:
        return cached

    from app.database import get_connection
    conn = get_connection()
    rows = conn.execute("SELECT DISTINCT region FROM policies").fetchall()
    conn.close()
    res = [r["region"] for r in rows]
    backend_cache.set(cache_key, res)
    return res

@router.get("/{policy_id}")
def get_policy(policy_id: str):
    p = get_policy_by_id(policy_id)
    if not p:
        raise HTTPException(status_code=404, detail="Policy not found")
    return p 