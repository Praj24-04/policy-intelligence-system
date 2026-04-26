from fastapi import APIRouter
from typing import Optional
from app.services.nlp_service import load_policies, get_policy_by_id

router = APIRouter()

@router.get("/")
def get_policies(
    sector: Optional[str] = None,
    region: Optional[str] = None,
    search: Optional[str] = None,
    status: Optional[str] = None,
):
    return load_policies(sector=sector, region=region, search=search, status=status)

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