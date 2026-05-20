from fastapi import APIRouter
from app.services.comparator import compare_policies
from app.ml.comparator_v2 import compare_policies_v2

router = APIRouter(redirect_slashes=False)

@router.get("/v2")
def compare_v2(id1: str, id2: str):
    return compare_policies_v2(id1, id2)

@router.get("/")
def compare(id1: str, id2: str, use_v2: bool = True):
    if use_v2:
        return compare_policies_v2(id1, id2)
    else:
        return compare_policies(id1, id2)