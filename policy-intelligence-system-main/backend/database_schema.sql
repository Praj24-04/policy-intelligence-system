-- ============================================================================
-- POSTGRESQL DATABASE SCHEMA SCRIPT FOR POLICY INTELLIGENCE SYSTEM
-- Compatible with pgAdmin 4, cPanel Postgres servers, & standard cloud DBs
-- ============================================================================

-- 1. ENABLE EXTENSIONS (Requires superuser privileges, run as postgres superuser if needed)
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. CORE POLICY STORAGE
CREATE TABLE IF NOT EXISTS policies (
    id                         TEXT PRIMARY KEY,
    title                      TEXT NOT NULL,
    sector                     TEXT NOT NULL,
    region                     TEXT NOT NULL,
    country                    TEXT NOT NULL,
    content                    TEXT NOT NULL,
    tags                       TEXT, -- JSON string array of metadata tags
    status                     TEXT DEFAULT 'Active',
    year                       INTEGER,
    version                    TEXT DEFAULT '1.0',
    source_url                 TEXT,
    key_requirements           TEXT,
    timeline_phases            TEXT,
    extracted_countries_cache  TEXT,
    embedding                  vector(768), -- ML semantic embeddings (pgvector)
    cluster_id                 INTEGER,
    cluster_confidence         DOUBLE PRECISION,
    embedding_model            VARCHAR(255),
    last_embedded_at           TIMESTAMP WITH TIME ZONE
);

-- 3. COUNTRY PROFILE METRICS (Used for Gap Analyses & Recommendations)
CREATE TABLE IF NOT EXISTS country_profiles (
    country                    TEXT PRIMARY KEY,
    region                     TEXT NOT NULL,
    gdp_tier                   TEXT NOT NULL,
    regulatory_maturity        TEXT NOT NULL,
    context                    TEXT NOT NULL,
    priority_needs             TEXT, -- JSON string array of country needs
    existing_sectors           TEXT  -- JSON string array of existing sectors
);

-- 4. COUNTRY NEEDS SUMMARIES
CREATE TABLE IF NOT EXISTS country_needs (
    country                    TEXT PRIMARY KEY,
    description                TEXT NOT NULL
);

-- 5. USER ACCOUNTS & CREDENTIALS
CREATE TABLE IF NOT EXISTS users (
    id                         SERIAL PRIMARY KEY,
    email                      TEXT UNIQUE NOT NULL,
    full_name                  TEXT NOT NULL,
    password_hash              TEXT NOT NULL,
    role                       TEXT DEFAULT 'user',
    created_at                 TIMESTAMP DEFAULT NOW()
);

-- 6. AUTHENTICATION & PASSWORD RESET VERIFICATION
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id                         SERIAL PRIMARY KEY,
    email                      TEXT NOT NULL,
    token                      TEXT NOT NULL,
    expires_at                 TIMESTAMP NOT NULL,
    used                       BOOLEAN DEFAULT FALSE,
    created_at                 TIMESTAMP DEFAULT NOW()
);

-- 7. HISTORY: USER UPLOADED ARGUMENTS
CREATE TABLE IF NOT EXISTS user_uploads (
    id                         SERIAL PRIMARY KEY,
    user_id                    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    filename                   TEXT NOT NULL,
    title                      TEXT,
    tags                       TEXT,
    word_count                 INTEGER,
    result_json                TEXT,
    created_at                 TIMESTAMP DEFAULT NOW()
);

-- 8. HISTORY: USER GENERATED CONTRACTS / POLICY DRAFTS
CREATE TABLE IF NOT EXISTS user_generates (
    id                         SERIAL PRIMARY KEY,
    user_id                    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    country                    TEXT NOT NULL,
    sector                     TEXT NOT NULL,
    result_json                TEXT,
    created_at                 TIMESTAMP DEFAULT NOW()
);

-- 9. HISTORY: USER COHERENCE COMPARISONS
CREATE TABLE IF NOT EXISTS user_compares (
    id                         SERIAL PRIMARY KEY,
    user_id                    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    policy_id_1                TEXT NOT NULL,
    policy_id_2                TEXT NOT NULL,
    result_json                TEXT,
    created_at                 TIMESTAMP DEFAULT NOW()
);

-- 10. METRICS: POLICY FEEDBACK SURVEYS
CREATE TABLE IF NOT EXISTS feedback (
    id                         SERIAL PRIMARY KEY,
    policy_id                  TEXT NOT NULL,
    country                    TEXT NOT NULL,
    helpful                    INTEGER NOT NULL,
    comment                    TEXT DEFAULT '',
    timestamp                  TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- SCHEMA SETUP COMPLETED SUCCESSFULLY
-- ============================================================================
