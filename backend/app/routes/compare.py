from fastapi import APIRouter, Depends
from app.services.comparator import compare_policies
from app.ml.comparator_v2 import compare_policies_v2
from app.auth import get_current_user
from app.database import get_connection
import json

router = APIRouter(redirect_slashes=False)

@router.get("/v2")
def compare_v2(
    id1: str, 
    id2: str,
    current_user: dict = Depends(get_current_user)
):
    res = compare_policies_v2(id1, id2)
    if "error" not in res:
        conn = get_connection()
        try:
            conn.execute(
                """
                INSERT INTO user_compares (user_id, policy_id_1, policy_id_2, result_json)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    current_user["id"],
                    id1,
                    id2,
                    json.dumps({
                        "similarity_label": res["overall_metrics"]["similarity_label"],
                        "composite_score": res["overall_metrics"]["composite_score"]
                    })
                )
            )
            conn.commit()
        except Exception as db_err:
            print(f"Error logging compare history: {db_err}")
        finally:
            conn.close()
    return res

@router.get("/")
def compare(
    id1: str, 
    id2: str, 
    use_v2: bool = True,
    current_user: dict = Depends(get_current_user)
):
    if use_v2:
        return compare_v2(id1, id2, current_user)
    else:
        res = compare_policies(id1, id2)
        if "error" not in res:
            conn = get_connection()
            try:
                conn.execute(
                    """
                    INSERT INTO user_compares (user_id, policy_id_1, policy_id_2, result_json)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        current_user["id"],
                        id1,
                        id2,
                        json.dumps({
                            "similarity_score": res.get("similarity_score", 0.0)
                        })
                    )
                )
                conn.commit()
            except Exception as db_err:
                print(f"Error logging compare history: {db_err}")
            finally:
                conn.close()
        return res