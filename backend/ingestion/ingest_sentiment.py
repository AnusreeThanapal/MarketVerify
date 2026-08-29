"""
Ingestion script for Sentiment Corpus Store.
Loads labeled English and Tamil market-sentiment samples with lead-lag price dynamics
into Qdrant collection 'sentiment_corpus'.
Used by the Sentiment Agent to ground sentiment classification and price timing dynamics.
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

def ingest_sentiment_data(seed_file_path: str = None) -> int:
    if seed_file_path is None:
        seed_file_path = os.path.join(
            Path(__file__).parent.parent, "data", "seed_sentiment.json"
        )

    logger.info(f"Ingesting Sentiment data from {seed_file_path}...")
    with open(seed_file_path, "r", encoding="utf-8") as f:
        records = json.load(f)

    qdrant_service = get_qdrant_service()
    client = qdrant_service.get_sync_client()
    embedding_svc = get_embedding_service()

    collection_name = settings.QDRANT_COLLECTION_SENTIMENT

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
        text_for_embedding = (
            f"Sample: {item['text_sample']} | "
            f"Sentiment: {item['sentiment_label']} | "
            f"Tone: {item['tone']} | "
            f"Lead-lag: {item['lead_lag_behavior']}"
        )
        vector = embedding_svc.get_embedding(text_for_embedding)

        points.append(
            models.PointStruct(
                id=idx + 1,
                vector=vector,
                payload={
                    "doc_id": item["id"],
                    "language": item["language"],
                    "text_sample": item["text_sample"],
                    "sentiment_label": item["sentiment_label"],
                    "tone": item["tone"],
                    "lead_lag_behavior": item["lead_lag_behavior"],
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
    ingest_sentiment_data()
