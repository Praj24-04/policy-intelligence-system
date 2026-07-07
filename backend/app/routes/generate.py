from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
from datetime import datetime
import re
from app.database import get_connection
from app.services.policy_generator import generate_policy_document
from app.services.pdf_generator import generate_policy_pdf
from data.country_profiles import COUNTRY_PROFILES

router = APIRouter()

# In-memory database cache to store generated policies temporarily
_generated_policies = {}

class GeneratePolicyRequest(BaseModel):
    country: str
    sector: str
    policy_scope: str = None
    focus_areas: list = None

@router.post("/policy")
def generate_policy(req: GeneratePolicyRequest):
    """
    POST /api/generate/policy
    Generates a structured policy document from Gemini using aggregated intelligence.
    """
    if not req.country or not req.sector:
        raise HTTPException(status_code=400, detail="Country and sector are required fields.")
        
    try:
        result = generate_policy_document(
            country=req.country,
            sector=req.sector,
            scope=req.policy_scope,
            focus_areas=req.focus_areas
        )
        
        # Save output in cache using policy_id
        policy_id = result["policy_id"]
        _generated_policies[policy_id] = result
        return result
    except ValueError as ve:
        # Google key not set or invalid
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

@router.get("/download/{policy_id}")
def download_policy_pdf(policy_id: str):
    """
    GET /api/generate/download/{policy_id}
    Retrieves the policy draft from the cache and returns a ReportLab government-style A4 PDF.
    """
    policy_data = _generated_policies.get(policy_id)
    if not policy_data:
        raise HTTPException(status_code=404, detail="Requested policy framework was not found or has expired.")
        
    try:
        pdf_bytes = generate_policy_pdf(policy_data)
        
        # Create safe slug-like filename
        clean_country = re.sub(r'[^a-zA-Z0-9-]', '', policy_data['country'].replace(' ', '-'))
        clean_sector = re.sub(r'[^a-zA-Z0-9-]', '', policy_data['sector'].replace(' ', '-'))
        date_str = datetime.now().strftime('%Y%m%d')
        filename = f"PolicyIQ-{clean_country}-{clean_sector}-Framework-{date_str}.pdf"
        
        headers = {
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Type": "application/pdf"
        }
        return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF document: {str(e)}")

@router.get("/countries")
def get_countries():
    """
    GET /api/generate/countries
    Returns all unique countries in the DB + static profiles.
    """
    countries_set = set(COUNTRY_PROFILES.keys())
    
    # Query database for additional unique countries
    conn = get_connection()
    try:
        rows = conn.execute("SELECT DISTINCT country FROM policies WHERE country IS NOT NULL").fetchall()
        for r in rows:
            if r["country"]:
                countries_set.add(r["country"].strip())
    except Exception as e:
        print(f"[WARN] Failed to query countries from policies table: {e}")
    finally:
        conn.close()
        
    return sorted(list(countries_set))

@router.get("/sectors")
def get_sectors():
    """
    GET /api/generate/sectors
    Returns all unique sectors in DB + standard preset sectors.
    """
    default_sectors = {
        "AI Governance", "Cybersecurity", "Data Privacy",
        "Healthcare AI", "Financial Regulation",
        "POSH Policies", "ESG Policies", "IoT and Robotics"
    }
    
    # Query database for additional unique sectors
    conn = get_connection()
    try:
        rows = conn.execute("SELECT DISTINCT sector FROM policies WHERE sector IS NOT NULL").fetchall()
        for r in rows:
            if r["sector"]:
                default_sectors.add(r["sector"].strip())
    except Exception as e:
        print(f"[WARN] Failed to query sectors from policies table: {e}")
    finally:
        conn.close()
        
    return sorted(list(default_sectors))

@router.get("/context-preview")
def get_context_preview(country: str, sector: str):
    """
    GET /api/generate/context-preview
    Retrieves the intelligence context (maturity, existing count, gaps) for frontend preview.
    """
    if not country or not sector:
        raise HTTPException(status_code=400, detail="Country and sector parameters are required.")
    from app.services.policy_generator import build_generation_context
    try:
        context = build_generation_context(country, sector)
        return {
            "maturity": context["maturity"],
            "priority_needs": context["priority_needs"],
            "existing_sectors": context["existing_sectors"],
            "existing_count": context["existing_count"],
            "gaps": context["gaps"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load preview: {str(e)}")