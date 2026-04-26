from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

scheduler = BackgroundScheduler()
_scheduler_started = False

def start_scheduler():
    global _scheduler_started
    if _scheduler_started:
        return

    from app.services.policy_fetcher import run_full_fetch

    print("🔄 Running initial policy fetch...")
    try:
        run_full_fetch()
    except Exception as e:
        print(f"⚠️ Initial fetch failed: {e}")

    scheduler.add_job(
        func=run_full_fetch,
        trigger=IntervalTrigger(hours=24),
        id="policy_fetch",
        name="Fetch live policies every 24 hours",
        replace_existing=True
    )

    scheduler.start()
    _scheduler_started = True
    print("⏰ Scheduler started — policies will auto-update every 24 hours")

def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()