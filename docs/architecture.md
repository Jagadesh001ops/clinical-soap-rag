# Architecture

## System Components

### 1. Haystack RAG Pipeline

The pipeline is built on **Haystack 2.x** with four connected components:

| Component | Role |
|---|---|
| `PgVectorRetriever` | Cosine similarity search over pgvector index |
| `PromptBuilder` | Formats retrieved docs + input note into Gemini prompt |
| `GeminiGenerator` | Calls Gemini 1.5 Pro API (1M token context) |
| `SoapValidator` | Multi-step completeness + coherence checks |

### 2. PostgreSQL + pgvector

A single PostgreSQL instance serves dual purpose:
- **Structured data**: Patient metadata, note types, timestamps
- **Vector search**: `embedding vector(768)` column with `ivfflat` cosine index

This eliminates a separate Pinecone/Weaviate/Qdrant service, simplifying the deployment topology and enabling SQL JOINs between semantic search results and structured patient records.

### 3. Flask REST API

Blueprint-organized REST endpoints:

```
POST /api/ingest     → embed & store clinical notes
POST /api/generate   → run RAG pipeline → SOAP draft
POST /api/validate   → standalone validation endpoint
POST /api/export     → render SOAP → PDF (WeasyPrint)
GET  /api/notes      → list indexed documents
```

### 4. Vue.js Frontend

Split-screen workspace:
- **Left**: Read-only original note with retrieved context highlights
- **Right**: Editable SOAP form with live validation indicators
- **Toolbar**: Generate · Validate · Export PDF · Save Draft

State management via **Pinia**. HTTP calls via **axios**.

### 5. Docker Compose

Three services: `api`, `frontend`, `db` — all networked on a single bridge. Health checks ensure API waits for PostgreSQL readiness before starting.

## Data Flow

```
User uploads note
      │
      ▼
Deidentifier (regex + NER)
      │
      ▼
PgVectorRetriever ──── ivfflat cosine search ──── PostgreSQL/pgvector
      │
      ▼
PromptBuilder (Jinja2 template)
      │
      ▼
GeminiGenerator (Gemini 1.5 Pro, 1M token ctx)
      │
      ▼
SoapValidator (4 gates: completeness, coherence, ICD codes, length)
      │
      ▼
Flask JSON response → Vue.js SOAP editor
      │
      ▼
PDF export (WeasyPrint)
```
