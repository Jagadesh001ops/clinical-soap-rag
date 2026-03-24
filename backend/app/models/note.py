"""
SQLAlchemy model for clinical notes.
The `embedding` column stores 768-dim sentence-transformer vectors
using the pgvector extension, co-locating semantic search with
structured patient metadata in a single PostgreSQL table.
"""

import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID

from app import db


class ClinicalNote(db.Model):
    __tablename__ = "clinical_notes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(String(64), nullable=False, index=True)
    note_type = Column(String(64))          # e.g. "discharge", "progress", "consult"
    content = Column(Text, nullable=False)
    embedding = Column(Vector(768))          # ivfflat cosine index defined in migration
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "patient_id": self.patient_id,
            "note_type": self.note_type,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
        }
