from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import policies, analytics, compare
from app.database import init_db

app = FastAPI(
    title="Global Policy Intelligence API",
    description="AI-powered policy analysis across AI Governance, Cybersecurity, and Data Privacy",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()
    print(" Global Policy Intelligence API is running")

app.include_router(policies.router,  prefix="/api/policies",  tags=["Policies"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(compare.router,   prefix="/api/compare",   tags=["Compare"])

@app.get("/")
def root():
    return {
        "service": "Global Policy Intelligence API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }