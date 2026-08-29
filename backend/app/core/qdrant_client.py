import os
from typing import Optional, List, Dict, Any
from qdrant_client import QdrantClient, AsyncQdrantClient
from qdrant_client.http import models
from backend.app.config import get_settings
from backend.app.core.logging import logger

settings = get_settings()


class QdrantService:
    def __init__(self):
        self.sync_client: Optional[QdrantClient] = None
        self._is_local_fallback = False

    def get_sync_client(self) -> QdrantClient:
        if self.sync_client is None:
            try:
                client = QdrantClient(
                    url=settings.QDRANT_URL,
                    api_key=settings.QDRANT_API_KEY,
                    timeout=2.0,
                )
                client.get_collections()
                self.sync_client = client
            except Exception as e:
                logger.info(f"External Qdrant not available at {settings.QDRANT_URL} ({e}). Using embedded local Qdrant storage.")
                self._is_local_fallback = True
                os.makedirs("./qdrant_data_local", exist_ok=True)
                self.sync_client = QdrantClient(path="./qdrant_data_local")
        return self.sync_client

    def search_points(
        self,
        collection_name: str,
        query_vector: List[float],
        query_filter: Optional[models.Filter] = None,
        limit: int = 5,
    ) -> List[Any]:
        """Universal vector search supporting both query_points and search APIs."""
        client = self.get_sync_client()
        try:
            if hasattr(client, "query_points"):
                result = client.query_points(
                    collection_name=collection_name,
                    query=query_vector,
                    query_filter=query_filter,
                    limit=limit,
                )
                return result.points
            elif hasattr(client, "search"):
                return client.search(
                    collection_name=collection_name,
                    query_vector=query_vector,
                    query_filter=query_filter,
                    limit=limit,
                )
        except Exception as e:
            logger.warning(f"Error querying collection {collection_name}: {e}")
        return []

    async def init_collections(self):
        """Ensure the three distinct collections exist with their schema."""
        client = self.get_sync_client()
        collections_to_create = [
            settings.QDRANT_COLLECTION_TRUST,
            settings.QDRANT_COLLECTION_FILING,
            settings.QDRANT_COLLECTION_SENTIMENT,
        ]

        try:
            existing = client.get_collections()
            existing_names = {c.name for c in existing.collections}

            for coll_name in collections_to_create:
                if coll_name not in existing_names:
                    logger.info(f"Creating Qdrant collection: {coll_name}")
                    client.create_collection(
                        collection_name=coll_name,
                        vectors_config=models.VectorParams(
                            size=settings.EMBEDDING_DIMENSION,
                            distance=models.Distance.COSINE,
                        ),
                    )
                else:
                    logger.debug(f"Collection {coll_name} already exists.")
        except Exception as e:
            logger.warning(f"Error during collection initialization: {e}")

    async def is_healthy(self) -> bool:
        try:
            client = self.get_sync_client()
            client.get_collections()
            return True
        except Exception:
            return False


qdrant_service = QdrantService()

def get_qdrant_service() -> QdrantService:
    return qdrant_service
