import sys
import asyncio
from pathlib import Path
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

# Setup paths to ensure we can import app modules properly
_backend_root = Path(__file__).parent.parent.parent
if str(_backend_root) not in sys.path:
    sys.path.insert(0, str(_backend_root))

from app.database import get_connection
from app.ml.embedder import embed_policy
from app.ml.embedding_store import store_embedding
from app.ml.vector_store import sync_policy_to_chroma, rebuild_chroma_index
from app.ml.clusterer import _clusterer, run_clustering_job


async def embed_new_policies():
    """
    Job 1: Runs every 1 hour.
    Query PostgreSQL for policies where embedding IS NULL.
    For each policy: embeds, stores, syncs to Chroma, predicts cluster, updates PostgreSQL.
    """
    print("[SCHEDULER] Checking for unembedded policies...")
    conn = get_connection()
    try:
        cur = conn.execute(
            """
            SELECT id, title, sector, country, region, content, year, status, tags
            FROM policies
            WHERE embedding IS NULL
            """
        )
        rows = cur.fetchall()
    finally:
        conn.close()

    if not rows:
        print("[SCHEDULER] No new policies to embed.")
        return

    total = len(rows)
    print(f"[SCHEDULER] Found {total} unembedded policies. Starting embedding process...")

    embedded_count = 0
    for row in rows:
        p = dict(row)
        pid = p["id"]
        title = p["title"]
        try:
            # 1. Call embed_policy()
            emb = embed_policy(p)

            # 2. Call store_embedding()
            store_embedding(pid, emb)

            # 3. Call sync_policy_to_chroma()
            sync_policy_to_chroma(p, emb)

            # 4. Predict cluster
            cluster_id, confidence = _clusterer.predict_single(emb)

            # 5. Update cluster_id and confidence in PostgreSQL
            conn = get_connection()
            try:
                conn.execute(
                    """
                    UPDATE policies
                    SET cluster_id = %s,
                        cluster_confidence = %s
                    WHERE id = %s
                    """,
                    (int(cluster_id), float(confidence), pid)
                )
                conn.commit()
            finally:
                conn.close()

            embedded_count += 1
            print(f"[SCHEDULER] Successfully processed '{title}' ({pid}) -> Cluster {cluster_id}")
        except Exception as e:
            print(f"[SCHEDULER] Failed to process policy '{title}' ({pid}): {e}")

    print(f"[SCHEDULER] Embedding job complete. Successfully embedded {embedded_count}/{total} policies.")


async def weekly_retrain():
    """
    Job 2: Runs every Sunday at 3:00 AM.
    Runs full clustering job and rebuilds the ChromaDB vector index.
    """
    print("[SCHEDULER] Executing weekly scheduled retrain...")
    try:
        # 1. Call run_clustering_job()
        summary = run_clustering_job()

        # 2. Call rebuild_chroma_index()
        rebuild_chroma_index()

        # 3. Log full cluster summary
        print("\n=== Weekly Cluster Summary ===")
        for cid, p_list in summary.items():
            if cid == "noise":
                print(f"Noise (Unclustered): {len(p_list)} policies")
            else:
                print(f"Cluster #{cid}: {len(p_list)} policies")
        print("==============================\n")

        print("[SCHEDULER] Weekly retrain complete.")
    except Exception as e:
        print(f"[SCHEDULER] Error during scheduled weekly retrain: {e}")


def start_scheduler():
    """
    Creates the scheduler, registers both jobs, starts execution, and returns the instance.
    """
    scheduler = AsyncIOScheduler()

    # Job 1: Every 1 hour
    scheduler.add_job(
        embed_new_policies,
        trigger=IntervalTrigger(hours=1),
        id="embed_new_policies",
        name="Hourly embedding of new policies",
        replace_existing=True
    )

    # Job 2: Every Sunday at 3:00 AM
    scheduler.add_job(
        weekly_retrain,
        trigger=CronTrigger(day_of_week="sun", hour=3, minute=0),
        id="weekly_retrain",
        name="Weekly clustering retrain and index rebuild",
        replace_existing=True
    )

    scheduler.start()
    print("[SCHEDULER] Background AsyncIOScheduler started successfully.")
    return scheduler


def stop_scheduler(scheduler):
    """
    Gracefully shuts down the background scheduler instance.
    """
    if scheduler and scheduler.running:
        scheduler.shutdown()
        print("[SCHEDULER] Background AsyncIOScheduler stopped gracefully.")
