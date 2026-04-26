from fastapi import APIRouter, BackgroundTasks
from app.services.policy_fetcher import run_full_fetch, get_fetch_status

router = APIRouter()

@router.get("/status")
def fetch_status():
    """Get current database stats and live fetch info."""
    return get_fetch_status()

@router.post("/trigger")
def trigger_fetch(background_tasks: BackgroundTasks):
    """Manually trigger a policy fetch."""
    background_tasks.add_task(run_full_fetch)
    return {
        "message": "Policy fetch started in background",
        "status": "running"
    }