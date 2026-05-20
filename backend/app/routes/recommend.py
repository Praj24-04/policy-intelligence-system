from fastapi import APIRouter
from app.services.recommender import get_recommendations, get_cluster_summary
from app.ml.recommender_v2 import get_recommendations_v2

router = APIRouter()

# Important: /clusters/summary must be BEFORE /{policy_id}
@router.get("/clusters/summary")
def clusters():
    return get_cluster_summary()

@router.get("/v2/{policy_id}")
def recommend_v2(policy_id: str, top_n: int = 5):
    return get_recommendations_v2(policy_id, top_n)

@router.get("/{policy_id}")
def recommend(policy_id: str, top_n: int = 5, use_v2: bool = True):
    if use_v2:
        return get_recommendations_v2(policy_id, top_n)
    else:
        return get_recommendations(policy_id, top_n)