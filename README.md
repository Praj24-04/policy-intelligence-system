# PolicyIQ — Global Policy Intelligence System

PolicyIQ is a state-of-the-art, AI-powered regulatory intelligence platform designed for aggregating, analyzing, and comparing global policy frameworks. By combining advanced deep learning bi-encoders, cross-encoder rerankers, density-based clustering, and NLP parsing, PolicyIQ offers a robust decision-support tool for global compliance across critical sectors like AI Governance, Cybersecurity, Data Privacy, and ESG.

---

## 🔬 Core Machine Learning & NLP Architecture

### 1. Hybrid Bi-Encoder Embedding Engine
* **Primary Deep Model:** Employs **Legal-BERT** (`nlpaueb/legal-bert-base-uncased`) via SentenceTransformers to extract dense, domain-specific semantic profiles from complex legal and regulatory vocabularies.
* **Fail-Safe Fallbacks:** Dynamically degrades to `all-mpnet-base-v2` or `all-MiniLM-L6-v2` in resource-constrained environments.
* **Weighted Pool Strategy:** Instead of simple mean pooling, policy representations are constructed via a weighted mean of separate fields:
  * **Title:** Weight `4.0`
  * **Tags & Concepts:** Weight `3.0`
  * **Sector & Country Metadata:** Weight `2.0`
  * **Content Chunks:** Weight `1.0` each (split using an overlapping sliding-window chunker up to `256` words to preserve context boundary).

### 2. Dual-Engine Vector Store
* **Primary Engine:** **ChromaDB Vector Store** indexes high-dimensional vectors to perform sub-millisecond Cosine Similarity searches.
* **Fallback Engine:** **PostgreSQL pgvector** acts as a relational vector backup, allowing on-the-fly similarity calculations and seamless fallback queries if the local vector DB is warming up.

### 3. Dimensionality Reduction & HDBSCAN Clustering
* **UMAP Reduction:** Employs UMAP (Uniform Manifold Approximation and Projection) with `50` components and `cosine` metric to compress high-dimensional bi-encoder vectors while preserving global and local relationships.
* **HDBSCAN Spatial Clustering:** Runs Hierarchical Density-Based Spatial Clustering (`min_cluster_size=5`, `min_samples=3`) on UMAP coordinates. This dynamically groups policies into organic regulatory clusters and filters outlier noise documents (`-1`).
* **Real-time Prediction:** Uses UMAP's `.transform()` and HDBSCAN's `approximate_predict` to classify new or uploaded policies on-the-fly, storing the assignment along with a dynamic `cluster_confidence` float.

### 4. Five-Factor Policy Recommender Pipeline
PolicyIQ generates country-level recommendation matches using a proprietary **5-Factor Multi-Criteria Scoring System** with **Cross-Encoder Reranking**:
1. **Factor 1: Sector Gap (35% weight)** - Evaluates whether a country completely lacks a framework in the policy's sector, or flags frameworks that are vintage/outdated (>= 3 years gap).
2. **Factor 2: Regulatory Maturity (25% weight)** - Adapts proposals to national readiness levels (Nascent, Emerging, Developing, Advanced).
3. **Factor 3: Semantic Need Match (20% weight)** - Runs cosine similarity between the policy profile and the country's national priority descriptions (`country_needs`) in PostgreSQL.
4. **Factor 4: Regional Adoption Pressure (12% weight)** - Tallies the quantity of regional neighbors who have implemented identical or similar policies.
5. **Factor 5: Economic Tier GDP Alignment (8% weight)** - Facilitates leapfrogging transfers between advanced and emerging GDP tiers.

* **Cross-Encoder Reranking:** When the top recommendations have scores within `0.15` of each other, the pipeline runs **MS-Marco MiniLM Cross-Encoder** (`cross-encoder/ms-marco-MiniLM-L-6-v2`) to perform deep, bi-directional attention checks on the regulatory context.

### 5. Six-Dimensional Policy Comparator
Provides granular gap analysis between any two policy frameworks using a three-tier comparison:
* **Thematic Projection:** Maps both policies against six anchor vector spaces (Enforcement, Scope, Individual Rights, Mandatory Obligations, Innovation Sandbox, and Transparency/Audits).
* **Composite Score:** Combines Bi-Encoder Cosine similarity (40%), Cross-Encoder Sigmoid prediction (35%), and Jaccard Tag overlap (25%) into a single standardized index.
* **Philosophical Classification:** Classifies regulatory approaches into one of five baseline philosophies (*Principles-based, Risk-based, Compliance-driven, Safety-first, or Innovation-focused*).
* **Dynamic Comparative Insights:** Generates highlights detailing geopolitical divergence, structural complexity (word count density), and vintage gaps.

### 6. NLP & Entity Extraction Service
* **spaCy NER:** Employs medium English pipelines (`en_core_web_md` or fallback `en_core_web_sm`) using `GPE`, `LOC`, and `NORP` labels to parse out geographical jurisdictions.
* **Frequency Tag Ranking:** Runs frequency-analysis on policy text to prioritize and rank tag badges, ensuring the most active regulatory concepts bubble to the top.
* **Monetary Fine Extractor:** Parses statutory texts to identify and format financial penalties and regulatory liabilities.

---

## 🌟 Premium UX & Theme Standard

* **Enterprise Visual Identity:** Beautiful "black-and-lime" dashboard designed to match high-end corporate platforms (neutral borders `#e8e8e8`, card backgrounds `var(--bg-card)`, and signature lime green `#5c9e2e` accents).
* **Dynamic Light/Dark Mode:** Dynamic CSS variable mapping synchronizes every component (cards, radar charts, line graphs, map shapes, and hover overlays) automatically.
* **Proportional Grid Layout:** Centers visual components evenly across a dual-column layout containing Recharts donut sector distributions, chronological area timelines, interactive maps, and NLP lists.
* **Live Aggregator Pipeline Banner:** A single-row nowrap banner showing ingestion statistics (Curated, EUR-Lex, CISA, US Fed Register) and real-time live sync indicators.

---

## 🛠️ Technology Stack

**Frontend**
* **Framework:** React.js (Vite)
* **Styling:** Vanilla CSS (CSS Variables) + Tailwind CSS
* **Components:** Framer Motion (animations), Lucide React (iconography), Recharts (data viz)
* **Exports:** jsPDF, jsPDF-AutoTable

**Backend**
* **Framework:** FastAPI (Python)
* **Database:** PostgreSQL (psycopg2)
* **Security:** JWT Authentication, Bcrypt password hashing
* **ML & NLP:** spaCy (en_core_web_md), SentenceTransformers (Legal-BERT), UMAP, HDBSCAN, Scikit-Learn
* **Scheduling:** APScheduler

---

## 🚀 Setup & Installation

### Prerequisites
* Node.js (v16+)
* Python (v3.9+)
* PostgreSQL running on port `5432`

### 1. Database Setup
Create a PostgreSQL database named `policy_db`:
```sql
CREATE DATABASE policy_db;
```

### 2. Backend Installation
Navigate to the `backend` folder, create a virtual environment, and install dependencies:
```bash
cd backend
python -m venv venv
# On Windows: venv\Scripts\activate
# On Mac/Linux: source venv/bin/activate

pip install -r requirements.txt
python -m spacy download en_core_web_md
```

Initialize the database schema and seeder:
```bash
python check_tables.py
```

Start the FastAPI application:
```bash
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Installation
Navigate to the `frontend` folder, install packages, and start the React dev server:
```bash
cd frontend
npm install
npm start
```
Open `http://localhost:3000` to interact with the full-stack portal.

---

## 🔒 Security Note
Ensure `backend/.env` is configured with valid credentials matching your local PostgreSQL setup and a secure JWT secret before deploying.