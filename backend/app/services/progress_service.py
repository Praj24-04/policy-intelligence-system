from datetime import datetime
from threading import Lock

# Global dictionary holding pipeline progress metrics
pipeline_progress = {
    "status": "idle",                # "idle", "fetching", "embedding", "clustering"
    "task_name": "",                 # e.g., "Multi-source policy fetch"
    "total_policies": 0,
    "processed_policies": 0,
    "current_policy_title": "",
    "last_run": None,
    "last_error": None,
    "last_updated": None
}

_progress_lock = Lock()

def update_progress(status=None, task_name=None, total=None, processed=None, current_title=None, error=None):
    """Thread-safely update pipeline progress statistics."""
    with _progress_lock:
        if status is not None:
            pipeline_progress["status"] = status
        if task_name is not None:
            pipeline_progress["task_name"] = task_name
        if total is not None:
            pipeline_progress["total_policies"] = total
        if processed is not None:
            pipeline_progress["processed_policies"] = processed
        if current_title is not None:
            pipeline_progress["current_policy_title"] = current_title
        if error is not None:
            pipeline_progress["last_error"] = error
        pipeline_progress["last_updated"] = datetime.now().isoformat()
