"""
PostgreSQL + pgvector document store adapter.
Provides the SQLAlchemy engine used by PgVectorRetriever.
"""

import os
from sqlalchemy import create_engine, text


class PgDocumentStore:
    """
    Thin wrapper around a SQLAlchemy engine that exposes
    the connection interface expected by PgVectorRetriever.

    Also handles first-run schema initialisation:
      - Enables the pgvector extension
      - Creates the clinical_notes table if it doesn't exist
      - Builds the ivfflat cosine index
    """

    def __init__(self, database_url: str | None = None):
        url = database_url or os.getenv(
            "DATABASE_URL",
            "postgresql://postgres:postgres@db:5432/clinicalsoap",
        )
        self.engine = create_engine(url, pool_pre_ping=True)
        self._init_schema()

    def _init_schema(self):
        ddl = """
        CREATE EXTENSION IF NOT EXISTS vector;

        CREATE TABLE IF NOT EXISTS clinical_notes (
            id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            patient_id  TEXT NOT NULL,
            note_type   TEXT,
            content     TEXT NOT NULL,
            embedding   vector(768),
            created_at  TIMESTAMPTZ DEFAULT now()
        );

        CREATE INDEX IF NOT EXISTS clinical_notes_embedding_idx
            ON clinical_notes
            USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 100);
        """
        with self.engine.begin() as conn:
            for statement in ddl.strip().split(";"):
                stmt = statement.strip()
                if stmt:
                    conn.execute(text(stmt))
