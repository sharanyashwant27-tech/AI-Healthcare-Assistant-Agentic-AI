"""Application configuration loaded from environment variables."""

from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "AI Healthcare Assistant"
    app_env: str = "development"
    app_debug: bool = True
    secret_key: str = "change-me"
    encryption_key: str = ""  # AES-256 key material; falls back to SECRET_KEY
    phi_masking_enabled: bool = True
    tls_enabled: bool = False  # set true behind HTTPS reverse proxy
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    api_prefix: str = "/api/v1"
    cors_origins: str = "http://localhost:8911"

    frontend_port: int = 8911
    backend_port: int = 8000

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "healthcare"
    postgres_password: str = "healthcare_secret"
    postgres_db: str = "ai_healthcare"

    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_url: str = "redis://localhost:6379/0"

    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "healthcare_neo4j"

    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str = ""
    vector_db_provider: str = "qdrant"  # qdrant | milvus | pinecone
    milvus_host: str = "localhost"
    milvus_port: int = 19530
    pinecone_api_key: str = ""
    pinecone_index: str = "ai-healthcare"

    openai_api_key: str = ""
    anthropic_api_key: str = ""
    google_api_key: str = ""
    llama_base_url: str = "http://localhost:11434/v1"  # Ollama-compatible
    llama_api_key: str = "ollama"
    default_llm_provider: str = "openai"  # openai | anthropic | google | llama
    default_llm_model: str = "gpt-4o-mini"
    default_embedding_provider: str = "openai"  # openai | bge-large | e5-large
    default_embedding_model: str = "text-embedding-3-large"
    embedding_dimensions: int = 1024  # normalized store dim (OpenAI large can shorten)

    minio_endpoint: str = ""
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "healthcare"
    minio_secure: bool = False

    whisper_model: str = "base"
    ocr_engine: str = "tesseract"
    agent_framework: str = "crewai"  # crewai | autogen
    rate_limit_per_minute: int = 60
    prometheus_enabled: bool = True
    log_level: str = "INFO"
    elasticsearch_url: str = "http://localhost:9200"
    n8n_webhook_url: str = "http://localhost:5678/webhook"
    hms_webhook_url: str = ""  # Hospital Management System integration endpoint
    use_sqlite: bool = True
    sqlite_path: str = "./ai_healthcare.db"

    upload_dir: str = "uploads"
    medical_disclaimer: str = (
        "This assistant provides general health information only and does not "
        "diagnose medical conditions. Always consult a licensed healthcare professional. "
        "If this is an emergency, call your local emergency services immediately."
    )

    @property
    def database_url(self) -> str:
        if self.use_sqlite:
            return f"sqlite+aiosqlite:///{self.sqlite_path}"
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def database_url_sync(self) -> str:
        if self.use_sqlite:
            return f"sqlite:///{self.sqlite_path}"
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def cors_origin_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @field_validator("secret_key")
    @classmethod
    def validate_secret(cls, v: str) -> str:
        if len(v) < 16:
            raise ValueError("SECRET_KEY must be at least 16 characters")
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
