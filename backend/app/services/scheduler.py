from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

scheduler = BackgroundScheduler()
_scheduler_started = False

def start_scheduler():
    global _scheduler_started
    if _scheduler_started:
        return

    from app.services.policy_fetcher import run_full_fetch

    import threading

    def initial_fetch():
        print("[INIT] Running initial multi-source policy fetch in background...")
        try:
            result = run_full_fetch()
            live = result.get("sources", {})
            eurlex_status = live.get("eurlex", {}).get("status", "unknown")
            cisa_status = live.get("cisa", {}).get("status", "unknown")
            print(f"   Initial fetch: EUR-Lex={eurlex_status}, CISA={cisa_status}")
        except Exception as e:
            print(f"[WARN] Initial fetch failed: {e}")

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
    print("[SCHED] Scheduler started - live sources refresh every 24 hours")
    print("   Live: EUR-Lex SPARQL API · CISA KEV JSON Feed")
    print("   Static: Curated seed policies · Extended research dataset")

def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()