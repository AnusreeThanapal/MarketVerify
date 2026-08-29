"""
Ingestion script for Trust-Tier Store.
Loads historical trajectory records from seed JSON / CSV into Qdrant collection 'trust_tier_store'.
Used to compute source trust score and credibility history.
"""
import json
import os
import sys
from pathlib import Path
from qdrant_client import models
from backend.app.config import get_settings
from backend.app.core.logging import logger
from backend.app.core.qdrant_client import get_qdrant_service
from backend.app.agents.llm_provider import get_embedding_service

settings = get_settings()

def ingest_trust_tier_data(seed_file_path: str = None) -> int:
    if seed_file_path is None:
        seed_file_path = os.path.join(
            Path(__file__).parent.parent, "data", "seed_trust_tier.json"
        )

    logger.info(f"Ingesting Trust Tier data from {seed_file_path}...")
    with open(seed_file_path, "r", encoding="utf-8") as f:
        records = json.load(f)

    qdrant_service = get_qdrant_service()
    client = qdrant_service.get_sync_client()
    embedding_svc = get_embedding_service()

    collection_name = settings.QDRANT_COLLECTION_TRUST

    # Recreate / ensure collection
    collections = [c.name for c in client.get_collections().collections]
    if collection_name not in collections:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=settings.EMBEDDING_DIMENSION,
                distance=models.Distance.COSINE,
            ),
        )

    points = []
    for idx, item in enumerate(records):
        text_for_embedding = f"Source: {item['source_handle']} {item.get('source_name', '')}. Claim: {item['past_claim_text']}. Category: {item['category']}."
        vector = embedding_svc.get_embedding(text_for_embedding)

        points.append(
            models.PointStruct(
                id=idx + 1,
                vector=vector,
                payload={
                    "doc_id": item["id"],
                    "source_handle": item["source_handle"].lower(),
                    "source_name": item.get("source_name", ""),
                    "past_claim_text": item["past_claim_text"],
                    "ticker": item.get("ticker", ""),
                    "was_accurate": item["was_accurate"],
                    "lag_hours": item.get("lag_hours", 24),
                    "category": item.get("category", "rumor"),
                    "outcome_summary": item["outcome_summary"],
                    "outcome_date": item["outcome_date"],
                },
            )
        )

    client.upsert(
        collection_name=collection_name,
        points=points,
    )
    logger.info(f"Successfully ingested {len(points)} records into '{collection_name}'.")
    return len(points)

if __name__ == "__main__":
    ingest_trust_tier_data()
