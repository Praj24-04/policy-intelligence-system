from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.routes import policies, analytics, compare, recommend, upload, auth, fetch, feedback, generate, ml
app = FastAPI(
    title="Global Policy Intelligence API",
    description="AI-powered policy analysis — Live data from OECD, CISA, EUR-Lex, ENISA",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    init_db()

    # Pre-warm NER cache
    from app.services.nlp_service import prewarm_ner_cache
    prewarm_ner_cache()

    # Train ML model in background so it doesn't block server startup
    import threading
    from app.services.recommender import _load_and_train
    threading.Thread(target=_load_and_train, daemon=True).start()

    # Start new ML scheduler
    from app.ml.scheduler import start_scheduler, embed_new_policies
    scheduler = start_scheduler()
    app.state.scheduler = scheduler

    # Run check for unembedded policies immediately
    try:
        await embed_new_policies()
    except Exception as e:
        print(f"[WARN] Failed running immediate policy embedding check on startup: {e}")

    print("[READY] PolicyIQ API running - Multi-source data pipeline active")


@app.on_event("shutdown")
def shutdown():
    # Stop new ML scheduler
    if hasattr(app.state, "scheduler"):
        from app.ml.scheduler import stop_scheduler
        stop_scheduler(app.state.scheduler)

app.include_router(auth.router,      prefix="/api/auth",      tags=["Auth"])
app.include_router(policies.router,  prefix="/api/policies",  tags=["Policies"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(compare.router,   prefix="/api/compare",   tags=["Compare"])
app.include_router(recommend.router, prefix="/api/recommend", tags=["Recommendations"])
app.include_router(upload.router,    prefix="/api/upload",    tags=["Upload"])
app.include_router(fetch.router,     prefix="/api/fetch",     tags=["Live Fetch"])
app.include_router(feedback.router, prefix="/api/feedback", tags=["Feedback"])
app.include_router(generate.router, prefix="/api/generate", tags=["Generate"])
app.include_router(ml.router,        prefix="/api/ml",        tags=["ML System"])

@app.get("/")
def root():
    return {
        "service": "Global Policy Intelligence API",
        "version": "2.0.0",
        "status": "running",
        "data_sources": ["OECD", "CISA", "EUR-Lex", "ENISA"],
        "docs": "/docs"
    }

# trigger reload