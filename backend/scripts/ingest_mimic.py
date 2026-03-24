"""
scripts/ingest_mimic.py
-----------------------
One-time ingestion script for MIMIC-IV clinical notes.

Usage:
    python scripts/ingest_mimic.py \
        --notes_csv /data/mimic-iv/note/discharge.csv \
        --limit 5000

Requires MIMIC-IV credentialed access via PhysioNet.
De-identifies notes before embedding and inserting into pgvector store.

MIMIC-IV note columns used:
    note_id, subject_id, note_type, text
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
from tqdm import tqdm
from sentence_transformers import SentenceTransformer

from app import create_app, db
from app.models.note import ClinicalNote
from app.services.deidentifier import deidentify

EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
BATCH_SIZE = 64


def parse_args():
    parser = argparse.ArgumentParser(description="Ingest MIMIC-IV notes into pgvector")
    parser.add_argument("--notes_csv", required=True, help="Path to MIMIC-IV note CSV")
    parser.add_argument("--limit", type=int, default=None, help="Max rows to ingest")
    return parser.parse_args()


def main():
    args = parse_args()

    print(f"Loading notes from {args.notes_csv}...")
    df = pd.read_csv(args.notes_csv, usecols=["note_id", "subject_id", "note_type", "text"])
    if args.limit:
        df = df.head(args.limit)
    print(f"  {len(df):,} notes to process")

    print("Loading embedding model...")
    embedder = SentenceTransformer(EMBED_MODEL)

    app = create_app()
    with app.app_context():
        db.create_all()
        inserted = 0

        for start in tqdm(range(0, len(df), BATCH_SIZE), desc="Ingesting"):
            batch = df.iloc[start : start + BATCH_SIZE]
            texts = [deidentify(str(row["text"])) for _, row in batch.iterrows()]
            vectors = embedder.encode(texts, normalize_embeddings=True, show_progress_bar=False)

            notes = [
                ClinicalNote(
                    patient_id=str(row["subject_id"]),
                    note_type=str(row.get("note_type", "discharge")),
                    content=texts[i],
                    embedding=vectors[i].tolist(),
                )
                for i, (_, row) in enumerate(batch.iterrows())
            ]

            db.session.bulk_save_objects(notes)
            db.session.commit()
            inserted += len(notes)

    print(f"\n✓ Ingested {inserted:,} notes into pgvector store.")


if __name__ == "__main__":
    main()
