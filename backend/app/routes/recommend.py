from fastapi import APIRouter
from app.services.recommender import get_recommendations, get_cluster_summary

router = APIRouter()

# Important: /clusters/summary must be BEFORE /{policy_id}
@router.get("/clusters/summary")
def clusters():
    return get_cluster_summary()

@router.get("/{policy_id}")
def recommend(policy_id: str, top_n: int = 5):
    return get_recommendations(policy_id, top_n)