from fastapi import APIRouter
from app.services.comparator import compare_policies

router = APIRouter(redirect_slashes=False)

@router.get("/")
def compare(id1: str, id2: str):
    return compare_policies(id1, id2)