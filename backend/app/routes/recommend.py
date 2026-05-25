from fastapi import APIRouter, Query
from app.services.recommender import get_recommendations, get_cluster_summary
from app.ml.recommender_v2 import get_recommendations_v2

router = APIRouter()

def _parse_weights(
    w_sector: float = None,
    w_maturity: float = None,
    w_semantic: float = None,
    w_regional: float = None,
    w_economic: float = None
):
    if any(w is not None for w in [w_sector, w_maturity, w_semantic, w_regional, w_economic]):
        return {
            "sector_gap": w_sector if w_sector is not None else 0.35,
            "regulatory_maturity": w_maturity if w_maturity is not None else 0.25,
            "semantic_need": w_semantic if w_semantic is not None else 0.20,
            "regional_pressure": w_regional if w_regional is not None else 0.12,
            "economic_tier": w_economic if w_economic is not None else 0.08,
        }
    return None

# Important: /clusters/summary must be BEFORE /{policy_id}
@router.get("/clusters/summary")
def clusters():
    return get_cluster_summary()

@router.get("/download/{policy_id}")
def download_recommendations_pdf(
    policy_id: str, 
    top_n: int = 5,
    w_sector: float = Query(None),
    w_maturity: float = Query(None),
    w_semantic: float = Query(None),
    w_regional: float = Query(None),
    w_economic: float = Query(None)
):
    weights = _parse_weights(w_sector, w_maturity, w_semantic, w_regional, w_economic)
    res = get_recommendations_v2(policy_id, top_n, weights)
    
    from app.ml.recommender_v2 import DEFAULT_WEIGHTS
    res["weights"] = weights if weights else DEFAULT_WEIGHTS
    
    from app.services.pdf_generator import generate_recommendations_pdf
    from fastapi.responses import Response
    
    pdf_bytes = generate_recommendations_pdf(res)
    
    filename = f"PolicyIQ_Recommendations_{policy_id[:8]}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

@router.get("/v2/{policy_id}")
def recommend_v2(
    policy_id: str, 
    top_n: int = 5,
    w_sector: float = Query(None),
    w_maturity: float = Query(None),
    w_semantic: float = Query(None),
    w_regional: float = Query(None),
    w_economic: float = Query(None)
):
    weights = _parse_weights(w_sector, w_maturity, w_semantic, w_regional, w_economic)
    return get_recommendations_v2(policy_id, top_n, weights)

@router.get("/{policy_id}")
def recommend(
    policy_id: str, 
    top_n: int = 5, 
    use_v2: bool = True,
    w_sector: float = Query(None),
    w_maturity: float = Query(None),
    w_semantic: float = Query(None),
    w_regional: float = Query(None),
    w_economic: float = Query(None)
):
    weights = _parse_weights(w_sector, w_maturity, w_semantic, w_regional, w_economic)
    if use_v2:
        return get_recommendations_v2(policy_id, top_n, weights)
    else:
        return get_recommendations(policy_id, top_n)