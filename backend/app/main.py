from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import policies, analytics, compare, recommend, upload, auth, fetch
from app.database import init_db
from app.routes import policies, analytics, compare, recommend, upload, auth, fetch, feedback
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
def startup():
    init_db()

    # Pre-warm NER cache
    from app.services.nlp_service import prewarm_ner_cache
    prewarm_ner_cache()

    # Train ML model
    from app.services.recommender import _load_and_train
    _load_and_train()

    # Start live fetcher
    from app.services.scheduler import start_scheduler
    start_scheduler()

    print("🚀 PolicyIQ API running — Live data pipeline active")

@app.on_event("shutdown")
def shutdown():
    from app.services.scheduler import stop_scheduler
    stop_scheduler()

app.include_router(auth.router,      prefix="/api/auth",      tags=["Auth"])
app.include_router(policies.router,  prefix="/api/policies",  tags=["Policies"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(compare.router,   prefix="/api/compare",   tags=["Compare"])
app.include_router(recommend.router, prefix="/api/recommend", tags=["Recommendations"])
app.include_router(upload.router,    prefix="/api/upload",    tags=["Upload"])
app.include_router(fetch.router,     prefix="/api/fetch",     tags=["Live Fetch"])
app.include_router(feedback.router, prefix="/api/feedback", tags=["Feedback"])

@app.get("/")
def root():
    return {
        "service": "Global Policy Intelligence API",
        "version": "2.0.0",
        "status": "running",
        "data_sources": ["OECD", "CISA", "EUR-Lex", "ENISA"],
        "docs": "/docs"
    }