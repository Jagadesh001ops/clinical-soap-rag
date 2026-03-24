"""
POST /api/ingest
Accepts raw clinical note text, de-identifies it, embeds it,
and stores the document in the pgvector store.
"""

from flask import Blueprint, request, jsonify
from app import db
from app.models.note import ClinicalNote
from app.services.deidentifier import deidentify
from sentence_transformers import SentenceTransformer

ingest_bp = Blueprint("ingest", __name__)

_embedder = None


def get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return _embedder


@ingest_bp.route("/api/ingest", methods=["POST"])
def ingest_note():
    """
    Request body:
        {
          "patient_id": "P001",
          "note_type": "discharge",
          "content": "Patient is a 54-year-old male presenting with..."
        }

    Response:
        { "id": "<uuid>", "status": "indexed" }
    """
    body = request.get_json(force=True)
    patient_id = body.get("patient_id", "").strip()
    note_type = body.get("note_type", "general").strip()
    content = body.get("content", "").strip()

    if not patient_id or not content:
        return jsonify({"error": "patient_id and content are required"}), 400

    clean_content = deidentify(content)

    embedder = get_embedder()
    vector = embedder.encode(clean_content, normalize_embeddings=True).tolist()

    note = ClinicalNote(
        patient_id=patient_id,
        note_type=note_type,
        content=clean_content,
        embedding=vector,
    )
    db.session.add(note)
    db.session.commit()

    return jsonify({"id": str(note.id), "status": "indexed"}), 201


@ingest_bp.route("/api/notes", methods=["GET"])
def list_notes():
    """Return a paginated list of all indexed clinical notes."""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    patient_id = request.args.get("patient_id")

    query = ClinicalNote.query
    if patient_id:
        query = query.filter_by(patient_id=patient_id)

    paginated = query.order_by(ClinicalNote.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        "notes": [n.to_dict() for n in paginated.items],
        "total": paginated.total,
        "page": page,
        "pages": paginated.pages,
    })
