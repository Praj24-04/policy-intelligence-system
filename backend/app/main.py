from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.routes import policies, analytics, compare, recommend, upload, auth, fetch, feedback, generate, ml
from contextlib import asynccontextmanager
from app.config import CORS_ORIGINS

# Setup globally structured logging format immediately
from app.logging_config import setup_logging
setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup validation check for LLM provider configuration
    import os
    llm_provider = os.getenv("LLM_PROVIDER", "auto").lower()
    google_key = os.getenv("GOOGLE_API_KEY", "")
    
    if llm_provider == "gemini":
        if not google_key:
            print("\n" + "="*80)
            print(" WARNING:")
            print(" GOOGLE_API_KEY not configured.")
            print(" PolicyIQ will operate in DEMO MODE using sector templates.")
            print("="*80 + "\n")
    elif llm_provider == "auto":
        if not google_key:
            print("\n" + "="*80)
            print(" WARNING:")
            print(" GOOGLE_API_KEY is not configured.")
            print(" PolicyIQ will operate in DEMO MODE using sector templates.")
            print("="*80 + "\n")

    init_db()

    # Pre-warm NER cache
    from app.services.nlp_service import prewarm_ner_cache
    prewarm_ner_cache()

    # V2 recommender pre-computes country need embeddings on import
    # No explicit startup training needed
    import threading

    # Start live fetch scheduler (EUR-Lex + CISA refresh every 24 hours)
    from app.services.scheduler import start_scheduler as start_fetch_scheduler
    start_fetch_scheduler()

    # Start new ML scheduler
    from app.ml.scheduler import start_scheduler as start_ml_scheduler, embed_new_policies
    ml_scheduler = start_ml_scheduler()
    app.state.scheduler = ml_scheduler

    # Pre-warm/fit ML clusterer in memory on startup in a background thread
    from app.ml.clusterer import load_and_fit
    threading.Thread(target=load_and_fit, daemon=True).start()

    # Run check for unembedded policies immediately
    try:
        await embed_new_policies()
    except Exception as e:
        print(f"[WARN] Failed running immediate policy embedding check on startup: {e}")

    print("[READY] PolicyIQ API running - Multi-source data pipeline active")
    
    yield
    
    # Stop live fetch scheduler
    from app.services.scheduler import stop_scheduler as stop_fetch_scheduler
    stop_fetch_scheduler()

    # Stop new ML scheduler
    if hasattr(app.state, "scheduler"):
        from app.ml.scheduler import stop_scheduler as stop_ml_scheduler
        stop_ml_scheduler(app.state.scheduler)

from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from app.limiter import limiter

app = FastAPI(
    title="Global Policy Intelligence API",
    description="AI-powered policy analysis — Live data from OECD, CISA, EUR-Lex, ENISA",
    version="2.0.0",
    lifespan=lifespan
)

@app.middleware("http")
async def force_ssl_redirect_scheme(request: Request, call_next):
    if request.headers.get("x-forwarded-proto") == "https":
        request.scope["scheme"] = "https"
    response = await call_next(request)
    return response

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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

@app.get("/health", tags=["System Uptime"])
def health_check():
    health_status = {
        "status": "healthy",
        "database": "unreachable",
        "ml_prewarmed": False
    }
    
    # Check PostgreSQL connection
    try:
        from app.database import get_connection
        conn = get_connection()
        conn.execute("SELECT 1")
        conn.close()
        health_status["database"] = "connected"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["database"] = f"error: {str(e)}"
        
    # Check Recommender Fit status
    try:
        from app.ml.recommender_v2 import recommender
        if recommender.fitted:
            health_status["ml_prewarmed"] = True
    except Exception:
        pass
        
    return health_status

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