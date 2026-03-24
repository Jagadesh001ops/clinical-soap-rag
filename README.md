# 🏥 ClinicalSOAP — RAG-Powered SOAP Note Generator

[![Status](https://img.shields.io/badge/status-in%20progress-yellow?style=flat-square)](https://github.com)
[![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)](https://python.org)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.x-42b883?style=flat-square&logo=vue.js)](https://vuejs.org)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?style=flat-square&logo=docker)](https://docker.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-pgvector-336791?style=flat-square&logo=postgresql)](https://postgresql.org)

> A Haystack RAG pipeline leveraging Gemini 1.5 Pro's 1M-token context window to process lengthy clinical notes and generate structured SOAP summaries — with multi-step validation and a full-stack web interface.

---

## 📸 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      Vue.js Frontend                        │
│         Split-screen editor · SOAP form · PDF export        │
└──────────────────────────┬──────────────────────────────────┘
                           │ REST
┌──────────────────────────▼──────────────────────────────────┐
│                    Flask REST API                           │
│        /ingest  ·  /generate  ·  /validate  ·  /export     │
└──────────┬────────────────────────┬────────────────────────┘
           │                        │
┌──────────▼──────────┐  ┌──────────▼──────────────────────┐
│   Haystack Pipeline │  │   PostgreSQL + pgvector          │
│  DocumentStore      │  │   De-identified MIMIC-IV index   │
│  Retriever          │  │   Vector search co-located       │
│  PromptNode         │  │   with structured patient data   │
│  Validator          │  └──────────────────────────────────┘
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│  Gemini 1.5 Pro API │
│  1M-token context   │
│  SOAP generation    │
└─────────────────────┘
```

---

## ✨ Features

| Feature | Status |
|---|---|
| Haystack RAG pipeline with Gemini 1.5 Pro | 🔄 In Progress |
| pgvector document store on PostgreSQL | 🔄 In Progress |
| MIMIC-IV de-identification & ingestion | 🔄 In Progress |
| Multi-step SOAP validation layer | 🔄 In Progress |
| Flask REST API (`/ingest`, `/generate`, `/validate`, `/export`) | 🔄 In Progress |
| Vue.js split-screen SOAP editor UI | 🔄 In Progress |
| PDF export of finalized SOAP notes | 🔄 In Progress |
| Docker Compose deployment | 🔄 In Progress |

---

## 🗂️ Project Structure

```
clinical-soap-rag/
├── backend/
│   ├── app/
│   │   ├── api/            # Flask route blueprints
│   │   │   ├── ingest.py
│   │   │   ├── generate.py
│   │   │   ├── validate.py
│   │   │   └── export.py
│   │   ├── pipeline/       # Haystack pipeline components
│   │   │   ├── rag_pipeline.py
│   │   │   ├── retriever.py
│   │   │   ├── validator.py
│   │   │   └── gemini_node.py
│   │   ├── models/         # SQLAlchemy models
│   │   │   ├── patient.py
│   │   │   └── note.py
│   │   └── services/
│   │       ├── deidentifier.py
│   │       └── pdf_exporter.py
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/     # Vue components
│   │   │   ├── SoapEditor.vue
│   │   │   ├── NoteViewer.vue
│   │   │   └── ValidationPanel.vue
│   │   ├── views/
│   │   │   ├── HomeView.vue
│   │   │   └── WorkspaceView.vue
│   │   └── stores/         # Pinia state management
│   │       └── soap.js
│   └── Dockerfile
├── docker/
│   └── docker-compose.yml
├── docs/
│   ├── architecture.md
│   └── api-reference.md
└── .github/
    └── workflows/
        └── ci.yml
```

---

## 🚀 Getting Started

### Prerequisites

- Docker & Docker Compose
- Google AI API key (Gemini 1.5 Pro)
- PostgreSQL 15+ with `pgvector` extension

### Quickstart

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/clinical-soap-rag.git
cd clinical-soap-rag

# Copy environment config
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY

# Start all services
docker compose up --build
```

The app will be available at:
- **Frontend**: http://localhost:5173
- **API**: http://localhost:5000
- **API Docs**: http://localhost:5000/docs

---

## 🧠 RAG Pipeline

The pipeline is built with [Haystack 2.x](https://haystack.deepset.ai/) and processes clinical notes in multiple stages:

```python
# pipeline/rag_pipeline.py (simplified)
pipeline = Pipeline()
pipeline.add_component("retriever", PgVectorRetriever(document_store=store))
pipeline.add_component("prompt_builder", SoapPromptBuilder())
pipeline.add_component("llm", GeminiGenerator(model="gemini-1.5-pro"))
pipeline.add_component("validator", SoapValidator())

pipeline.connect("retriever", "prompt_builder.documents")
pipeline.connect("prompt_builder", "llm")
pipeline.connect("llm", "validator")
```

### Multi-step Validation

Generated SOAP notes pass through a structured validation layer that checks:
1. **Completeness** — all four SOAP sections present (Subjective, Objective, Assessment, Plan)
2. **Clinical coherence** — Assessment aligns with documented Objective findings
3. **ICD code presence** — Plan section includes actionable diagnosis codes
4. **Hallucination guard** — Generated content grounded against retrieved source documents

---

## 🗄️ pgvector Schema

```sql
-- Vector index co-located with structured patient data
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE clinical_notes (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id  TEXT NOT NULL,
    note_type   TEXT,
    content     TEXT,
    embedding   vector(768),
    created_at  TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX ON clinical_notes
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);
```

---

## 🖥️ Frontend — Split-Screen Workspace

The Vue.js UI provides a clinical workflow-optimized split-screen layout:

- **Left pane**: Original clinical note (read-only, with retrieved context highlights)
- **Right pane**: Editable SOAP form with inline validation indicators
- **Toolbar**: Generate, validate, export to PDF, and save actions

---

## 📦 Docker Compose Services

| Service | Image | Port |
|---|---|---|
| `api` | `./backend` | 5000 |
| `frontend` | `./frontend` | 5173 |
| `db` | `pgvector/pgvector:pg16` | 5432 |

---

## 📋 API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/api/ingest` | `POST` | Ingest & embed clinical notes |
| `/api/generate` | `POST` | Run RAG pipeline → SOAP draft |
| `/api/validate` | `POST` | Run multi-step SOAP validator |
| `/api/export` | `POST` | Export SOAP note to PDF |
| `/api/notes` | `GET` | List all indexed notes |

Full reference: [`docs/api-reference.md`](docs/api-reference.md)

---

## 🔒 Data & Privacy

This project uses the [MIMIC-IV](https://physionet.org/content/mimiciv/2.2/) dataset, which requires credentialed access via PhysioNet. All data is de-identified prior to ingestion per HIPAA Safe Harbor guidelines. No real patient data is stored in this repository.

---

## 🛣️ Roadmap

- [ ] Complete Haystack pipeline wiring with Gemini 1.5 Pro
- [ ] Finish pgvector ingestion pipeline for MIMIC-IV notes
- [ ] Complete Vue.js split-screen workspace UI
- [ ] Implement multi-step SOAP validator
- [ ] PDF export via WeasyPrint
- [ ] Docker Compose full-stack deployment
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Unit & integration test suite

---

## 🤝 Contributing

This project is under active development. Issues and PRs welcome once the initial implementation is complete.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

*Built with [Haystack](https://haystack.deepset.ai/) · [Gemini 1.5 Pro](https://deepmind.google/technologies/gemini/) · [pgvector](https://github.com/pgvector/pgvector) · [Vue.js](https://vuejs.org/) · [Flask](https://flask.palletsprojects.com/)*
