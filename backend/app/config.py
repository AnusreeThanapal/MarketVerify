from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "MarketVerify"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # API Configuration
    API_V1_STR: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8005

    # PostgreSQL Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/marketverify"
    SYNC_DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/marketverify"

    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_STREAM_CHANNEL: str = "marketverify:agent_trace"

    # Qdrant Vector DB Configuration
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: Optional[str] = None
    
    # Qdrant Collection Names - Three distinct stores
    QDRANT_COLLECTION_TRUST: str = "trust_tier_store"
    QDRANT_COLLECTION_FILING: str = "filing_store"
    QDRANT_COLLECTION_SENTIMENT: str = "sentiment_corpus"

    # Embedding and LLM Settings
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMENSION: int = 384  # Standard dense embedding dimension
    USE_MOCK_EMBEDDINGS: bool = True  # True for deterministic offline embedding & tests
    OPENAI_API_KEY: Optional[str] = "mock-openai-key"
    OPENAI_MODEL_NAME: str = "gpt-4o-mini"

    # JWT Authentication Stub Settings
    JWT_SECRET_KEY: str = "marketverify-super-secret-jwt-key-2024"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Agent Thresholds & Tuning
    TRUST_LOW_CONFIDENCE_THRESHOLD: float = 0.40
    VERIFICATION_CONFIDENCE_RETRY_THRESHOLD: float = 0.50
    DEFAULT_RETRIEVAL_K: int = 3
    DEEP_RETRIEVAL_K: int = 7
    DEFAULT_SCORE_THRESHOLD: float = 0.65
    DEEP_SCORE_THRESHOLD: float = 0.45

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()
