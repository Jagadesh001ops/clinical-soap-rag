"""
POST /api/export
Renders a finalised SOAP note to a downloadable PDF using WeasyPrint.
"""

import io
from flask import Blueprint, request, jsonify, send_file
from app.services.pdf_exporter import render_soap_pdf

export_bp = Blueprint("export", __name__)


@export_bp.route("/api/export", methods=["POST"])
def export_pdf():
    """
    Request body:
        {
          "patient_id": "P001",
          "subjective": "...",
          "objective": "...",
          "assessment": "...",
          "plan": "..."
        }

    Response:
        application/pdf binary stream
    """
    body = request.get_json(force=True)

    required = {"subjective", "objective", "assessment", "plan"}
    missing = required - body.keys()
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    pdf_bytes = render_soap_pdf(body)

    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"soap_{body.get('patient_id', 'note')}.pdf",
    )
