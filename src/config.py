"""Configuration management for the episodic memory system."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # OpenAI
    openai_api_key: str
    openai_model: str = "text-embedding-3-large"
    embedding_dimension: int = 3072

    # Qdrant Vector Database
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection_name: str = "episodic_memories"

    # PostgreSQL
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "memory_system"

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    # Memory Settings
    working_memory_max_tokens: int = 128000
    embedding_cache_ttl: int = 86400  # 24 hours

    # Importance Scoring Weights
    novelty_weight: float = 0.20
    task_success_weight: float = 0.30
    retrieval_frequency_weight: float = 0.25
    user_signal_weight: float = 0.15
    emotional_salience_weight: float = 0.10

    # Forgetting Curve
    high_importance_threshold: float = 0.7
    medium_importance_threshold: float = 0.4
    high_importance_lambda: float = 0.1
    medium_importance_lambda: float = 0.5
    low_importance_lambda: float = 1.5
    deletion_threshold: float = 0.05

    # Retrieval
    default_top_k: int = 5
    retrieval_importance_filter: float = 0.3

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


def get_settings() -> Settings:
    """Get the application settings (singleton)."""
    return Settings()


# PostgreSQL connection string
def get_postgres_url() -> str:
    """Generate PostgreSQL connection URL."""
    settings = get_settings()
    return (
        f"postgresql://{settings.postgres_user}:{settings.postgres_password}"
        f"@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"
    )


# Redis connection string
def get_redis_url() -> str:
    """Generate Redis connection URL."""
    settings = get_settings()
    return f"redis://{settings.redis_host}:{settings.redis_port}/{settings.redis_db}"
