import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the backend folder
BASE_DIR = Path(__file__).parent.parent

# Load environment variables from .env file if it exists
env_path = BASE_DIR / ".env"
if env_path.exists():
    load_dotenv(env_path)

# ── JWT Security Settings ──────────────────────────────────────────────────
# Default key is for local development only. Production must use a high-entropy key via env.
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-this-in-production-policysystem2024-jwt-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
BCRYPT_ROUNDS = int(os.getenv("BCRYPT_ROUNDS", "12"))

# ── Database Configuration ─────────────────────────────────────────────────
# Loaded dynamically from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:admin123@localhost:5432/policy_db")

# ── CORS Origins ───────────────────────────────────────────────────────────
# Whitelisted clients. Comma-separated list in env: "https://domain.com,http://localhost:3000"
raw_cors = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001")
CORS_ORIGINS = [origin.strip() for origin in raw_cors.split(",") if origin.strip()]

# ── Email Service Settings ─────────────────────────────────────────────────
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# ── Google Authentication ──────────────────────────────────────────────────
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")

# ── Anthropic API (Policy Generator) ───────────────────────────────────────
# Needed for actual Claude model generation
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# ── Logging Settings ──────────────────────────────────────────────────────
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
