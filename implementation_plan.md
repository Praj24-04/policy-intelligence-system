# PolicyIQ — Production Deployment Remediation Plan

Make the PolicyIQ system fully safe, secure, and deployment-ready by systematically resolving all 25 audit findings across 4 phases.

## User Review Required

> [!IMPORTANT]
> **Deployment Target:** Before I start, I need to know:
> 1. **Where are you deploying?** (e.g., a VPS like DigitalOcean/AWS EC2, Render, Railway, or just making it production-ready locally for now?)
> 2. **Do you have a domain name?** (needed for SSL/CORS configuration)
> 3. **Should I skip Docker/CI-CD infrastructure and focus only on code-level security + cleanup first?**
>
> The plan below assumes we focus on **code-level fixes first** (Phases 1–3) which are universal regardless of deployment target, and optionally add Docker infrastructure (Phase 4) based on your answer.

## Open Questions

> [!IMPORTANT]
> - **Google OAuth Client ID:** The current one (`779080463690-...`) is committed to git history. Do you want me to keep using this same ID (just move it to env vars), or do you plan to create a new one?
> - **Existing user passwords:** Changing bcrypt rounds from 4→12 won't break existing hashed passwords (bcrypt stores rounds in the hash itself), but new passwords will be slower to hash (~300ms vs ~1ms). Is this acceptable?

---

## Phase 1: Security Hardening (Critical — Do First)

All hardcoded secrets, debug logging, and credential exposure fixed.

---

### Backend Configuration Module

#### [NEW] [config.py](file:///d:/VIT/PROJECTS/POLICY_PROJECT/backend/app/config.py)
Create a centralized configuration module that reads ALL settings from environment variables with sensible defaults. This replaces hardcoded values scattered across `auth.py`, `database.py`, `main.py`, and `email_service.py`.

```python
# Reads from env vars: JWT_SECRET_KEY, DATABASE_URL, CORS_ORIGINS,
# BCRYPT_ROUNDS, SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, 
# FRONTEND_URL, GOOGLE_CLIENT_ID, ANTHROPIC_API_KEY, LOG_LEVEL
```

#### [MODIFY] [auth.py](file:///d:/VIT/PROJECTS/POLICY_PROJECT/backend/app/auth.py)
- **Line 8:** Replace hardcoded `SECRET_KEY` → read from `config.JWT_SECRET_KEY`
- **Line 17:** Change `BCRYPT_ROUNDS = 4` → read from `config.BCRYPT_ROUNDS` (default 12)
- **Lines 74–109:** Remove ALL debug file-writing from `get_current_user`. Strip the function down to just JWT decode + user lookup — no file I/O.

#### [MODIFY] [database.py](file:///d:/VIT/PROJECTS/POLICY_PROJECT/backend/app/database.py)
- **Line 7:** Replace hardcoded `DB_URL` → read from `config.DATABASE_URL`
- **Lines 28–30:** Add connection pooling using `psycopg2.pool.ThreadedConnectionPool` (min=2, max=10)
- **Line 15–16:** Remove the hacky `?` → `%s` auto-replacement from `PostgresConnectionWrapper`

#### [MODIFY] [main.py](file:///d:/VIT/PROJECTS/POLICY_PROJECT/backend/app/main.py)
- **Line 13:** Replace hardcoded CORS origins → read from `config.CORS_ORIGINS` (comma-separated env var)
- **Lines 19, 56:** Migrate from deprecated `@app.on_event("startup"/"shutdown")` to FastAPI `lifespan` context manager
- Add rate limiting middleware using `slowapi` for auth endpoints

#### [MODIFY] [email_service.py](file:///d:/VIT/PROJECTS/POLICY_PROJECT/backend/app/email_service.py)
- Import settings from `config.py` instead of reading `os.getenv` directly

#### [MODIFY] [policy_generator.py](file:///d:/VIT/PROJECTS/POLICY_PROJECT/backend/app/services/policy_generator.py)
- **Line 11:** Import `ANTHROPIC_API_KEY` from config module instead of `os.getenv`

---

### Backend .env Cleanup

#### [MODIFY] [backend/.env](file:///d:/VIT/PROJECTS/POLICY_PROJECT/backend/.env)
Rewrite with ALL required env vars including new ones:
```env
JWT_SECRET_KEY=<generate-64-char-random-hex>
DATABASE_URL=postgresql://postgres:admin123@localhost:5432/policy_db
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
BCRYPT_ROUNDS=12
LOG_LEVEL=INFO
# ... existing SMTP, GOOGLE, ANTHROPIC keys
```

#### [MODIFY] [backend/.env.example](file:///d:/VIT/PROJECTS/POLICY_PROJECT/backend/.env.example)
Update template with all new variables, placeholder values only (no real secrets).

#### [DELETE] [auth_debug.log](file:///d:/VIT/PROJECTS/POLICY_PROJECT/backend/auth_debug.log)
Delete the file containing real JWT tokens.

---

### Frontend Environment

#### [MODIFY] [api.js](file:///d:/VIT/PROJECTS/POLICY_PROJECT/frontend/src/services/api.js)
- **Line 1:** Replace hardcoded `http://localhost:8000/api` → `process.env.REACT_APP_API_URL || "http://localhost:8000/api"`
- **Line 96:** Same fix for the standalone `fetch` call to feedback endpoint
- **Lines 5, 10, 18, 20, 29:** Remove ALL `console.log` debug statements (6 total)

#### [MODIFY] [frontend/.env](file:///d:/VIT/PROJECTS/POLICY_PROJECT/frontend/.env)
Add `REACT_APP_API_URL=http://localhost:8000/api`

#### [NEW] [frontend/.env.example](file:///d:/VIT/PROJECTS/POLICY_PROJECT/frontend/.env.example)
Create template file.

---

### SQL Placeholder Fix (? → %s)

#### [MODIFY] [nlp_service.py](file:///d:/VIT/PROJECTS/POLICY_PROJECT/backend/app/services/nlp_service.py)
- **Lines 145, 147, 158–159, 207–217, 243:** Replace all `?` with `%s` in SQL queries (7 occurrences)

#### [MODIFY] [feedback.py](file:///d:/VIT/PROJECTS/POLICY_PROJECT/backend/app/routes/feedback.py)
- **Lines 19–33, 62–67:** Replace all `?` with `%s` in SQL queries (9 occurrences)

#### [MODIFY] [database.py](file:///d:/VIT/PROJECTS/POLICY_PROJECT/backend/app/database.py)
- **Lines 14–16:** Remove the `?` → `%s` auto-replacement hack from `PostgresConnectionWrapper.execute()`

---

### HTTP Status Code Fixes

#### [MODIFY] [policies.py](file:///d:/VIT/PROJECTS/POLICY_PROJECT/backend/app/routes/policies.py)
- **Lines 35–37:** Replace `return {"error": ...}` with `raise HTTPException(status_code=404, ...)`

---

### Dependencies

#### [MODIFY] [requirements.txt](file:///d:/VIT/PROJECTS/POLICY_PROJECT/backend/requirements.txt)
- Add `python-dotenv` (for loading `.env` file)
- Add `slowapi` (for rate limiting)
- Pin all versions using current installed versions from pip freeze

---

## Phase 2: Code Cleanup & Hygiene

Dead files, debug noise, and repository clutter removed.

---

### Python Logging System

#### [NEW] [logging_config.py](file:///d:/VIT/PROJECTS/POLICY_PROJECT/backend/app/logging_config.py)
Create a logging configuration module that sets up Python `logging` with configurable level (from `LOG_LEVEL` env var). This replaces all `print()` calls across the codebase.

#### All Backend .py Files
Replace `print(...)` with `logger.info(...)` / `logger.warning(...)` / `logger.error(...)` across all 48 files that currently use print statements. Key files:
- `main.py`, `database.py`, `auth.py`, `email_service.py`
- `services/nlp_service.py`, `services/policy_fetcher.py`, `services/recommender.py`, `services/policy_generator.py`
- `ml/embedder.py`, `ml/vector_store.py`, `ml/clusterer.py`, `ml/scheduler.py`, `ml/recommender_v2.py`
- All route files

---

### File & Directory Cleanup

#### [DELETE] Files to remove:
| File | Reason |
|---|---|
| `frontend/src/components/Navbar.jsx` | Empty file (0 bytes) |
| `backend/auth_debug.log` | Contains real JWT tokens |
| `backend/import_times.txt` | 900KB debug timing data |
| `backend/check_db.py` | Dev-only debug script |
| `backend/check_tables.py` | Dev-only debug script |
| `backend/clean.py` | Dev-only utility |
| `backend/generate_policies.py` | Dev-only seed script |
| `backend/scripts/requirements.txt` | Duplicate/conflicting requirements |

#### [DELETE] Directories to remove:
| Directory | Reason |
|---|---|
| `policyora_audit_flaws/` | Competitor audit — not part of this product |
| `Microsoft/` | Accidentally committed PowerShell cache |
| `.venv-1/` | Redundant second virtual environment |
| `backend/venv/` | Redundant third virtual environment inside backend |

> [!WARNING]
> I will NOT delete `.venv/` since it's the active virtual environment being used to run the project. But it should be in `.gitignore`.

---

### .gitignore Update

#### [MODIFY] [.gitignore](file:///d:/VIT/PROJECTS/POLICY_PROJECT/.gitignore)
Add missing patterns:
```gitignore
.venv/
.venv-1/
Microsoft/
policyora_audit_flaws/
images/
*.log
import_times.txt
backend/scratch/
```

---

### Requirements Pinning

#### [MODIFY] [requirements.txt](file:///d:/VIT/PROJECTS/POLICY_PROJECT/backend/requirements.txt)
Run `pip freeze` and pin all dependency versions for reproducible builds.

---

## Phase 3: Robustness & Production Hardening

Rate limiting, health checks, proper error handling.

---

### Rate Limiting

#### [MODIFY] [main.py](file:///d:/VIT/PROJECTS/POLICY_PROJECT/backend/app/main.py)
Add `slowapi` rate limiter:
- Auth endpoints (`/api/auth/login`, `/api/auth/register`, `/api/auth/forgot-password`): 5 requests/minute
- General API: 60 requests/minute
- ML/embedding triggers: 2 requests/minute

### Health Check Endpoint

#### [MODIFY] [main.py](file:///d:/VIT/PROJECTS/POLICY_PROJECT/backend/app/main.py)
Add `/health` endpoint that checks:
- Database connectivity
- ML model loaded status
- ChromaDB collection status

### Input Validation

#### [MODIFY] Routes with user input
- Add `max_length` constraints to Pydantic models (RegisterRequest, etc.)
- Validate policy_id format in route handlers

---

## Phase 4: Docker & Deployment Infrastructure (Optional — Based on Your Target)

> [!NOTE]
> This phase creates the deployment containerization. Skip if you're deploying to a PaaS like Render/Railway that handles this automatically.

#### [NEW] `backend/Dockerfile`
Multi-stage build: Python 3.12-slim base, copy requirements first for layer caching, install deps, copy code, run with Gunicorn+Uvicorn workers.

#### [NEW] `frontend/Dockerfile`
Multi-stage build: Node 20 to build, Nginx to serve static files.

#### [NEW] `docker-compose.yml`
Orchestrate: backend, frontend, postgres, nginx reverse proxy.

#### [NEW] `nginx/nginx.conf`
Reverse proxy config with SSL termination, rate limiting, security headers.

#### [NEW] `.dockerignore`
Exclude venvs, node_modules, .git, __pycache__, etc.

---

## Verification Plan

### Automated Tests
After each phase, I will:
1. Start the backend server and verify no import errors
2. Start the frontend and verify compilation succeeds
3. Test critical API endpoints via `curl`:
   - `GET /` — root health
   - `POST /api/auth/register` — user registration
   - `POST /api/auth/login` — user login
   - `GET /api/policies` — policy listing
   - `GET /api/analytics/overview` — analytics

### Manual Verification
- Verify the app loads correctly in the browser
- Verify login/register flow works
- Verify env vars are being read (not hardcoded values)

---

## Execution Order

I'll work through this **one file at a time**, showing you each change:

1. **Create `config.py`** — centralized env-based config
2. **Fix `auth.py`** — remove debug logging, use config
3. **Fix `database.py`** — use config, add connection pool
4. **Fix `main.py`** — use config CORS, add lifespan, rate limiting
5. **Fix `api.js`** — env-based API URL, remove console.logs
6. **Fix SQL placeholders** — nlp_service.py, feedback.py
7. **Fix HTTP status codes** — policies.py
8. **Update .env files** — backend + frontend
9. **Update .gitignore** — comprehensive patterns
10. **Add logging** — replace print() across all files
11. **Delete dead files/dirs** — cleanup
12. **Pin requirements** — version lock
13. **Add health check** — /health endpoint
14. **Docker infrastructure** — if requested
