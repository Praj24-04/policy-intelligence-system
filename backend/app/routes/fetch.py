from fastapi import APIRouter, BackgroundTasks
from app.services.policy_fetcher import run_full_fetch, get_fetch_status

router = APIRouter()

@router.get("/status")
def fetch_status():
    """Get current database stats, per-source breakdown, and live fetch info."""
    return get_fetch_status()

@router.post("/trigger")
def trigger_fetch(background_tasks: BackgroundTasks):
    """Manually trigger a multi-source live policy fetch."""
    background_tasks.add_task(run_full_fetch)
    return {
        "message": "Multi-source live fetch started in background",
        "status": "running",
        "sources": [
            "EUR-Lex SPARQL API (EU Legislation)",
            "CISA KEV JSON (US Cybersecurity)",
            "US Federal Register API (US Regulations)"
        ]
    }