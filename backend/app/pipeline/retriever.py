"""
pgvector-backed document retriever for Haystack.
Co-locates vector search with structured patient data on PostgreSQL,
eliminating a separate vector database service.
"""

from __future__ import annotations

from typing import List

import numpy as np
from haystack import Document, component
from haystack.document_stores.types import DocumentStore
from sentence_transformers import SentenceTransformer
from sqlalchemy import text

EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


@component
class PgVectorRetriever:
    """
    Retrieves semantically similar clinical notes from the pgvector store.

    Uses cosine similarity over 768-dim embeddings stored in the
    `clinical_notes.embedding` column alongside structured patient metadata.
    """

    def __init__(self, document_store: DocumentStore, top_k: int = 5):
        self.document_store = document_store
        self.top_k = top_k
        self.embedder = SentenceTransformer(EMBED_MODEL)

    @component.output_types(documents=List[Document])
    def run(self, query: str) -> dict:
        query_embedding = self._embed(query)
        docs = self._vector_search(query_embedding)
        return {"documents": docs}

    def _embed(self, text: str) -> list[float]:
        vector = self.embedder.encode(text, normalize_embeddings=True)
        return vector.tolist()

    def _vector_search(self, embedding: list[float]) -> list[Document]:
        """
        Executes an ivfflat cosine-similarity search directly on PostgreSQL,
        returning the top-k most relevant clinical note excerpts.
        """
        vec_literal = "[" + ",".join(str(v) for v in embedding) + "]"
        sql = text(f"""
            SELECT id, content, note_type, patient_id,
                   1 - (embedding <=> :embedding::vector) AS score
            FROM clinical_notes
            ORDER BY embedding <=> :embedding::vector
            LIMIT :top_k
        """)

        with self.document_store.engine.connect() as conn:
            rows = conn.execute(sql, {"embedding": vec_literal, "top_k": self.top_k})
            return [
                Document(
                    id=str(row.id),
                    content=row.content,
                    meta={
                        "patient_id": row.patient_id,
                        "note_type": row.note_type,
                        "score": float(row.score),
                    },
                )
                for row in rows
            ]
