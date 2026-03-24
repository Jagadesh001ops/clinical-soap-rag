# Setup Guide

## Prerequisites

| Tool | Version | Notes |
|---|---|---|
| Docker | 24+ | Required for containerised deployment |
| Docker Compose | v2 | Included with Docker Desktop |
| Python | 3.11+ | For local backend development |
| Node.js | 20+ | For local frontend development |
| Google API Key | — | Gemini 1.5 Pro access required |
| MIMIC-IV access | — | PhysioNet credentialed account |

---

## 1. Clone & Configure

```bash
git clone https://github.com/YOUR_USERNAME/clinical-soap-rag.git
cd clinical-soap-rag

cp .env.example .env
```

Edit `.env`:

```env
GOOGLE_API_KEY=AIza...your_key_here
DATABASE_URL=postgresql://postgres:postgres@db:5432/clinicalsoap
```

---

## 2. Docker Compose (recommended)

```bash
docker compose -f docker/docker-compose.yml up --build
```

Services started:

| Service | URL |
|---|---|
| Frontend (Vue.js) | http://localhost:5173 |
| Backend (Flask API) | http://localhost:5000 |
| PostgreSQL + pgvector | localhost:5432 |

---

## 3. Local Development

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Start a local pgvector instance
docker run -d -p 5432:5432 \
  -e POSTGRES_DB=clinicalsoap \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  pgvector/pgvector:pg16

flask --app app run --debug
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## 4. Ingest MIMIC-IV Notes

After obtaining MIMIC-IV access via PhysioNet:

```bash
python backend/scripts/ingest_mimic.py \
  --notes_csv /path/to/mimic-iv/note/discharge.csv \
  --limit 10000
```

This will:
1. Load the discharge notes CSV
2. De-identify each note (regex + NER)
3. Embed with `sentence-transformers/all-MiniLM-L6-v2`
4. Insert into the `clinical_notes` pgvector table in batches of 64

---

## 5. Run Tests

```bash
cd backend
pytest tests/ -v
```
