import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger("app.scheduler")
scheduler = BackgroundScheduler()
_scheduler_started = False

def start_scheduler():
    global _scheduler_started
    if _scheduler_started:
        return

    from app.services.policy_fetcher import run_full_fetch
    import threading

    def initial_fetch():
        logger.info("Running initial multi-source policy fetch in background...")
        try:
            result = run_full_fetch()
            live = result.get("sources", {})
            eurlex_status = live.get("eurlex", {}).get("status", "unknown")
            cisa_status = live.get("cisa", {}).get("status", "unknown")
            logger.info(f"Initial fetch result: EUR-Lex={eurlex_status}, CISA={cisa_status}")
        except Exception as e:
            logger.warning(f"Initial fetch failed: {e}")

    threading.Thread(target=initial_fetch, daemon=True).start()

    scheduler.add_job(
        func=run_full_fetch,
        trigger=IntervalTrigger(hours=24),
        id="policy_fetch",
        name="Multi-source policy fetch (EUR-Lex + CISA + Curated)",
        replace_existing=True
    )

    scheduler.start()
    _scheduler_started = True
    logger.info("Background Live Ingestion Scheduler started (refresh interval: 24h)")

def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Background Live Ingestion Scheduler shut down successfully.")