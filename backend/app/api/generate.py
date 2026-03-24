"""
POST /api/generate
Accepts a clinical note and returns a validated SOAP summary.
"""

from flask import Blueprint, request, jsonify
from app.pipeline.rag_pipeline import build_soap_pipeline, run_soap_pipeline
from app.services.deidentifier import deidentify

generate_bp = Blueprint("generate", __name__)


@generate_bp.route("/api/generate", methods=["POST"])
def generate_soap():
    """
    Request body:
        { "note_text": "..." }

    Response:
        {
          "subjective": "...",
          "objective": "...",
          "assessment": "...",
          "plan": "...",
          "validation_status": "passed|failed",
          "validation_errors": [],
          "validation_warnings": []
        }
    """
    body = request.get_json(force=True)
    note_text = body.get("note_text", "").strip()

    if not note_text:
        return jsonify({"error": "note_text is required"}), 400

    # De-identify before processing
    clean_note = deidentify(note_text)

    from app import get_pipeline  # lazy import to avoid circular deps
    pipeline = get_pipeline()

    try:
        soap = run_soap_pipeline(pipeline, clean_note)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

    return jsonify(soap), 200
