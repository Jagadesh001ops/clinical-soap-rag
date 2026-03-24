"""
Flask application factory.
"""

import os
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
_pipeline = None


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@db:5432/clinicalsoap",
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    CORS(app, resources={r"/api/*": {"origins": os.getenv("CORS_ORIGIN", "*")}})
    db.init_app(app)

    from app.api.generate import generate_bp
    from app.api.ingest import ingest_bp
    from app.api.validate import validate_bp
    from app.api.export import export_bp

    app.register_blueprint(generate_bp)
    app.register_blueprint(ingest_bp)
    app.register_blueprint(validate_bp)
    app.register_blueprint(export_bp)

    return app


def get_pipeline():
    global _pipeline
    if _pipeline is None:
        from app.pipeline.rag_pipeline import build_soap_pipeline
        from app.models.document_store import PgDocumentStore
        store = PgDocumentStore()
        _pipeline = build_soap_pipeline(store)
    return _pipeline
