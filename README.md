# PolicyIQ — Global Policy Intelligence System

PolicyIQ is a full-stack, AI-powered platform designed for aggregating, analyzing, and generating global policy intelligence. It provides deep regulatory insights across critical sectors like AI Governance, Cybersecurity, Data Privacy, and ESG.

---

## 🌟 Key Features

### 1. Premium SaaS Dashboard & UI overhaul
* **Modern Aesthetic:** A sleek "black-and-lime" visual identity matching enterprise-grade design standards (neutral borders `#e8e8e8`, clean card backgrounds `var(--bg-card)`, and signature lime green `#5c9e2e` highlights).
* **Deep Theme Synchronization (Full Dark Mode):** Zero hardcoded styles. The entire dashboard dynamically shifts colors based on a persistent global dark mode toggle, transforming components (stat cards, interactive map elements, Recharts tooltip overlays, and bar charts) into high-contrast Zinc-950/Zinc-50 deep space tones.
* **Proportional Grid Alignment:** Visually balanced dashboard grid containing proportionally centered data containers (`220px` responsive height) including dynamic pie charts, chronological area charts, global maps, and spaCy NER country lists.
* **Nowrap Pipeline Banner:** A single-line horizontal scrollable Hybrid Intelligence Pipeline banner detailing live-fetched sources, live indicators, and asynchronous fetch trigger status with dynamic visual spinner states.

### 2. Live Aggregation & Synchronization Pipeline
* **Auto-Ingestion Pipeline:** Uses `apscheduler` on the backend to dynamically ingest live policies from API endpoints (EUR-Lex, CISA, US Federal Register) and merge them with curated foundational structures.
* **Robust Database Seeder:** Automatic startup script ensures full synchronization between the UI, API statistics, and the PostgreSQL database tables.
* **Sector Segmentation:** Advanced categorical indexing for high-specificity sectors (AI Governance, Cyber, Privacy, POSH, Healthcare, ESG).

### 3. ML-Powered Policy Recommender
* **Strategic Adoption Matches:** Employs TF-IDF and KMeans clustering to match policy frameworks with countries based on their regulatory maturity and GDP tier.
* **Semantic Similarity (BERT):** Uses SentenceTransformers to find thematically identical policies across borders.
* **Human-in-the-Loop Feedback:** Users can vote on the relevance of ML recommendations, continuously refining system accuracy.

### 4. Advanced Policy Comparator
* **Side-by-Side Analysis:** Instantly compare any two policies in the database.
* **Gap Detection:** Automatically identifies verbatim orphaned clauses, unique focus areas, and shared ML-extracted themes.
* **Export to PDF:** Generates formatted `jsPDF` reports of the comparison directly from the browser.

### 5. Custom Document Ingestion
* **PDF Uploads:** Upload proprietary policy documents (`.pdf`) for instant NLP analysis.
* **Auto-Tagging:** Extracts word counts, countries (via spaCy NER), sectors, and summarizes key constraints.

### 6. AI Policy Template Generator
* **Drafting Assistant:** Automatically drafts comprehensive regulatory frameworks tailored to specific countries and sectors.
* **Gap Analysis Context:** Adjusts the generated language based on whether it is supplementing an existing framework or filling a total regulatory void.
* **Text Export:** One-click download of the generated template as a `.txt` file.

### 7. Interactive Analytics
* **Live Visualizations:** Powered by `Recharts` for geographic distribution (radar charts), chronological adoption (bar charts), and ML-feedback accuracy.

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
* **ML & Data:** spaCy (NER), SentenceTransformers (Embeddings/Similarity), Scikit-Learn (TF-IDF/KMeans)
* **Background Tasks:** APScheduler

---

## 🚀 Setup & Installation

### Prerequisites
* Node.js (v16+)
* Python (v3.9+)
* PostgreSQL installed and running on default port `5432`

### 1. Database Configuration
Ensure PostgreSQL is running and create a database named `policy_db` with credentials matching your local environment (default: `postgres` / `admin123`).

### 2. Backend Setup
Navigate to the `backend` directory, create a virtual environment, and install dependencies:
```bash
cd backend
python -m venv venv
# On Windows: venv\Scripts\activate
# On Mac/Linux: source venv/bin/activate

pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

Initialize the database schema:
```bash
python check_tables.py
```

Run the backend server:
```bash
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup
Navigate to the `frontend` directory:
```bash
cd frontend
npm install
npm start
```

Navigate to `http://localhost:3000` in your browser. Create an account via the Sign Up page to access the PolicyIQ dashboard!

---

## 🔒 Security Note
This project utilizes `.env` files for managing secrets (e.g., JWT signing keys, PostgreSQL credentials). Ensure you copy `backend/.env.example` to `backend/.env` and update the values before deploying to production.