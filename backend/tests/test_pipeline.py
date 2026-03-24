"""
Tests for the SOAP validation pipeline and API endpoints.
Run with: pytest tests/ -v
"""

import json
import pytest
from unittest.mock import patch, MagicMock

from app import create_app, db
from app.pipeline.validator import SoapValidator


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })
    with app.app_context():
        db.create_all()
        yield app


@pytest.fixture
def client(app):
    return app.test_client()


# ---------------------------------------------------------------------------
# SoapValidator unit tests
# ---------------------------------------------------------------------------

class TestSoapValidator:
    def setup_method(self):
        self.validator = SoapValidator()

    def test_passes_complete_soap(self):
        soap = {
            "subjective": "Patient reports chest pain for 2 days, worse on exertion.",
            "objective": "BP 145/92, HR 88. EKG shows ST changes in leads II, III, aVF.",
            "assessment": "Acute coronary syndrome, rule out NSTEMI. ICD-10: I24.9",
            "plan": "Admit for cardiac monitoring. Aspirin 325mg, heparin drip. Cardiology consult.",
        }
        result = self.validator.run(replies=[json.dumps(soap)])
        assert result["soap"]["validation_status"] == "passed"
        assert result["soap"]["validation_errors"] == []

    def test_fails_missing_section(self):
        soap = {
            "subjective": "Patient reports headache.",
            "objective": "Neuro exam normal.",
            # assessment missing
            "plan": "Ibuprofen 400mg PRN.",
        }
        result = self.validator.run(replies=[json.dumps(soap)])
        assert result["soap"]["validation_status"] == "failed"
        assert any("assessment" in e.lower() for e in result["soap"]["validation_errors"])

    def test_warns_missing_icd_code(self):
        soap = {
            "subjective": "Fatigue and weight gain over 3 months.",
            "objective": "TSH elevated at 8.2 mIU/L.",
            "assessment": "Hypothyroidism suspected.",  # no ICD code
            "plan": "Start levothyroxine 50mcg daily. Recheck TSH in 6 weeks.",
        }
        result = self.validator.run(replies=[json.dumps(soap)])
        warnings = result["soap"]["validation_warnings"]
        assert any("icd" in w.lower() for w in warnings)

    def test_handles_malformed_json(self):
        result = self.validator.run(replies=["not valid json {{"])
        assert "error" in result["soap"]

    def test_handles_empty_replies(self):
        result = self.validator.run(replies=[])
        assert "error" in result["soap"] or result["soap"].get("validation_status") == "failed"


# ---------------------------------------------------------------------------
# API endpoint tests
# ---------------------------------------------------------------------------

class TestValidateEndpoint:
    def test_validate_valid_soap(self, client):
        payload = {
            "subjective": "Patient presents with fever 38.9°C and productive cough for 4 days.",
            "objective": "Temp 38.9, RR 22, SpO2 94%. CXR shows right lower lobe consolidation.",
            "assessment": "Community-acquired pneumonia, right lower lobe. ICD-10: J18.1",
            "plan": "Amoxicillin-clavulanate 875mg BID x 7 days. Follow-up in 1 week.",
        }
        resp = client.post("/api/validate", json=payload)
        assert resp.status_code == 200
        data = resp.get_json()
        assert "validation_status" in data

    def test_validate_rejects_empty_body(self, client):
        resp = client.post("/api/validate", data="not json", content_type="text/plain")
        assert resp.status_code == 400


class TestIngestEndpoint:
    def test_ingest_requires_fields(self, client):
        resp = client.post("/api/ingest", json={"content": "some note"})
        # patient_id missing → 400
        assert resp.status_code == 400

    @patch("app.api.ingest.get_embedder")
    def test_ingest_returns_id(self, mock_embedder, client):
        mock_emb = MagicMock()
        mock_emb.encode.return_value = __import__("numpy").zeros(768)
        mock_embedder.return_value = mock_emb

        payload = {
            "patient_id": "TEST001",
            "note_type": "progress",
            "content": "Patient doing well post-op day 2. Ambulating independently.",
        }
        resp = client.post("/api/ingest", json=payload)
        assert resp.status_code == 201
        data = resp.get_json()
        assert "id" in data
        assert data["status"] == "indexed"
