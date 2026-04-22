from fastapi import APIRouter, Query
from typing import Optional
from app.services.nlp_service import load_policies, get_policy_by_id

router = APIRouter()

@router.get("/")
def get_policies(
    sector: Optional[str] = None,
    region: Optional[str] = None,
    search: Optional[str] = None,
    status: Optional[str] = None,
    limit: Optional[int] = Query(10, description="Number of policies to return"),
    offset: Optional[int] = Query(0, description="Number of policies to skip"),
):
    return load_policies(sector=sector, region=region, search=search, status=status, limit=limit, offset=offset)

@router.get("/sectors")
def get_sectors():
    from app.database import get_connection
    conn = get_connection()
    rows = conn.execute("SELECT DISTINCT sector FROM policies").fetchall()
    conn.close()
    return [r["sector"] for r in rows]

@router.get("/regions")
def get_regions():
    from app.database import get_connection
    conn = get_connection()
    rows = conn.execute("SELECT DISTINCT region FROM policies").fetchall()
    conn.close()
    return [r["region"] for r in rows]

@router.get("/{policy_id}")
def get_policy(policy_id: str):
    p = get_policy_by_id(policy_id)
    if not p:
        return {"error": "Policy not found"}
    return p