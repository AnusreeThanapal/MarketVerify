"""
Ingestion script for Filing Store.
Loads SEBI filings, exchange disclosures, board meeting outcomes, and official press releases
into Qdrant collection 'filing_store'.
Used by the Verification Agent to corroborate or contradict claims.
"""
import json
import os
from pathlib import Path
from qdrant_client import models
from backend.app.config import get_settings
from backend.app.core.logging import logger
from backend.app.core.qdrant_client import get_qdrant_service
from backend.app.agents.llm_provider import get_embedding_service

settings = get_settings()

def ingest_filings_data(seed_file_path: str = None) -> int:
    if seed_file_path is None:
        seed_file_path = os.path.join(
            Path(__file__).parent.parent, "data", "seed_filings.json"
        )

    logger.info(f"Ingesting Filings data from {seed_file_path}...")
    with open(seed_file_path, "r", encoding="utf-8") as f:
        records = json.load(f)

    qdrant_service = get_qdrant_service()
    client = qdrant_service.get_sync_client()
    embedding_svc = get_embedding_service()

    collection_name = settings.QDRANT_COLLECTION_FILING

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
        # Rich contextual text for dense vector indexing
        text_for_embedding = (
            f"Company: {item['company_name']} ({item['ticker']}). "
            f"Type: {item['filing_type']}. Date: {item['filing_date']}. "
            f"Headline: {item['headline']}. Content: {item['content_chunk']}"
        )
        vector = embedding_svc.get_embedding(text_for_embedding)

        points.append(
            models.PointStruct(
                id=idx + 1,
                vector=vector,
                payload={
                    "doc_id": item["filing_id"],
                    "ticker": item["ticker"].upper(),
                    "company_name": item["company_name"],
                    "filing_type": item["filing_type"],
                    "filing_date": item["filing_date"],
                    "headline": item["headline"],
                    "content_chunk": item["content_chunk"],
                    "source_url": item.get("source_url", ""),
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
    ingest_filings_data()
