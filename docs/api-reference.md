# API Reference

Base URL: `http://localhost:5000`

---

## POST `/api/ingest`

Embed and store a clinical note in the pgvector store.

**Request**
```json
{
  "patient_id": "P001",
  "note_type": "discharge",
  "content": "Patient is a 54-year-old male presenting with..."
}
```

**Response `201`**
```json
{ "id": "3fa85f64-...", "status": "indexed" }
```

**Errors**
- `400` — `patient_id` or `content` missing

---

## POST `/api/generate`

Run the full RAG pipeline on a clinical note and return a validated SOAP draft.

**Request**
```json
{ "note_text": "Patient reports chest pain for 2 days..." }
```

**Response `200`**
```json
{
  "subjective": "Patient reports 2 days of chest pain, worse on exertion...",
  "objective": "BP 145/92, HR 88, EKG shows ST changes in II, III, aVF...",
  "assessment": "Acute coronary syndrome, rule out NSTEMI. ICD-10: I24.9",
  "plan": "Admit for cardiac monitoring. Aspirin 325mg, heparin drip...",
  "validation_status": "passed",
  "validation_errors": [],
  "validation_warnings": []
}
```

**Errors**
- `400` — `note_text` missing or empty
- `500` — pipeline or Gemini API error

---

## POST `/api/validate`

Re-validate an already-generated (or manually edited) SOAP dict without re-running the full pipeline.

**Request**
```json
{
  "subjective": "...",
  "objective": "...",
  "assessment": "...",
  "plan": "..."
}
```

**Response `200`**
```json
{
  "validation_status": "passed",
  "validation_errors": [],
  "validation_warnings": ["No ICD-10 codes detected in Assessment/Plan."]
}
```

---

## POST `/api/export`

Render a SOAP note to a downloadable PDF via WeasyPrint.

**Request**
```json
{
  "patient_id": "P001",
  "subjective": "...",
  "objective": "...",
  "assessment": "...",
  "plan": "..."
}
```

**Response `200`**  
`Content-Type: application/pdf`  
Binary PDF stream, `Content-Disposition: attachment; filename="soap_P001.pdf"`

**Errors**
- `400` — one or more SOAP sections missing

---

## GET `/api/notes`

List indexed clinical notes with optional filters.

**Query params**
| Param | Type | Default | Description |
|---|---|---|---|
| `page` | int | 1 | Page number |
| `per_page` | int | 20 | Results per page (max 100) |
| `patient_id` | string | — | Filter by patient ID |

**Response `200`**
```json
{
  "notes": [
    {
      "id": "3fa85f64-...",
      "patient_id": "P001",
      "note_type": "discharge",
      "content": "...",
      "created_at": "2024-11-15T10:30:00"
    }
  ],
  "total": 1204,
  "page": 1,
  "pages": 61
}
```
