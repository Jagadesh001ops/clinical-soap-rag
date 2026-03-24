"""
POST /api/validate
Runs the SoapValidator against an already-generated SOAP dict
without re-running the full RAG pipeline. Useful for re-validation
after manual inline edits in the Vue.js editor.
"""

from flask import Blueprint, request, jsonify
from app.pipeline.validator import SoapValidator
import json

validate_bp = Blueprint("validate", __name__)
_validator = SoapValidator()


@validate_bp.route("/api/validate", methods=["POST"])
def validate_soap():
    """
    Request body:
        {
          "subjective": "...",
          "objective": "...",
          "assessment": "...",
          "plan": "..."
        }

    Response:
        {
          "validation_status": "passed|failed",
          "validation_errors": [...],
          "validation_warnings": [...]
        }
    """
    soap = request.get_json(force=True)

    if not isinstance(soap, dict):
        return jsonify({"error": "Request body must be a JSON object"}), 400

    # Re-use the Haystack component by passing a pre-serialised reply
    result = _validator.run(replies=[json.dumps(soap)])
    validated = result["soap"]

    return jsonify({
        "validation_status": validated.get("validation_status", "unknown"),
        "validation_errors": validated.get("validation_errors", []),
        "validation_warnings": validated.get("validation_warnings", []),
    })
