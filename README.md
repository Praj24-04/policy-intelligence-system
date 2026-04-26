# Global Policy Intelligence System

A full-stack AI-powered platform for aggregating, analyzing, and recommending global policies across AI Governance, Cybersecurity, and Data Privacy sectors.

## Tech Stack
- **Frontend:** React, Tailwind CSS, Recharts, Framer Motion
- **Backend:** FastAPI, SQLite, Python
- **ML/NLP:** spaCy (NER), TF-IDF, KMeans Clustering

## Features
- 30 real-world policies across 3 sectors
- NLP-based country extraction (spaCy NER)
- Policy comparison with AI insights
- ML recommendation engine (TF-IDF + KMeans + Need-Gap Scoring)
- Interactive analytics dashboard

## Setup

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python scripts/seed_db.py
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm start
```

## API Endpoints
| Endpoint | Description |
|---|---|
| `GET /api/policies/` | All policies with filters |
| `GET /api/analytics/overview` | Dashboard stats |
| `GET /api/compare?id1=x&id2=y` | Compare two policies |
| `GET /api/recommend/{id}` | ML recommendations |