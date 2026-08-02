"""Embedding factory — OpenAI text-embedding-3-large, BGE Large, E5 Large."""

from functools import lru_cache
from typing import List, Optional

from core.config import settings
from core.logging import get_logger
from embeddings.models import EMBEDDING_MODELS, resolve_model_spec

logger = get_logger(__name__)


class LocalHashEmbeddings:
    """Deterministic local fallback embeddings when no provider/API key is available."""

    def __init__(self, dim: int = 1024) -> None:
        self.dim = dim

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._embed(t) for t in texts]

    def embed_query(self, text: str) -> List[float]:
        return self._embed(text)

    def _embed(self, text: str) -> List[float]:
        import hashlib
        import math

        digest = hashlib.sha256(text.encode("utf-8")).digest()
        values: List[float] = []
        while len(values) < self.dim:
            digest = hashlib.sha256(digest + text.encode("utf-8")).digest()
            for b in digest:
                values.append((b / 255.0) * 2 - 1)
                if len(values) >= self.dim:
                    break
        norm = math.sqrt(sum(v * v for v in values)) or 1.0
        return [v / norm for v in values]


def _normalize_dim(vec: List[float], dim: int) -> List[float]:
    if len(vec) == dim:
        return vec
    if len(vec) > dim:
        return vec[:dim]
    return vec + [0.0] * (dim - len(vec))


class DimensionNormalizedEmbeddings:
    """Wrap an embeddings backend and normalize output vector size."""

    def __init__(self, backend, dim: int) -> None:
        self.backend = backend
        self.dim = dim

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if hasattr(self.backend, "embed_documents"):
            vectors = self.backend.embed_documents(texts)
        else:
            vectors = [self.backend.embed_query(t) for t in texts]
        return [_normalize_dim(v, self.dim) for v in vectors]

    def embed_query(self, text: str) -> List[float]:
        return _normalize_dim(self.backend.embed_query(text), self.dim)


class EmbeddingFactory:
    @staticmethod
    def create(provider: Optional[str] = None, model: Optional[str] = None):
        provider = (provider or settings.default_embedding_provider).lower()
        model = model or settings.default_embedding_model
        spec = resolve_model_spec(provider, model)
        target_dim = int(getattr(settings, "embedding_dimensions", 0) or spec.dimensions)

        try:
            if spec.provider == "openai" and settings.openai_api_key:
                from langchain_openai import OpenAIEmbeddings

                # OpenAI supports shortened dimensions for text-embedding-3-*
                kwargs = {"model": spec.model_id, "api_key": settings.openai_api_key}
                if target_dim and target_dim < spec.dimensions:
                    kwargs["dimensions"] = target_dim
                backend = OpenAIEmbeddings(**kwargs)
                return DimensionNormalizedEmbeddings(backend, target_dim)

            if spec.provider in {"bge-large", "e5-large", "bge", "e5"}:
                from langchain_community.embeddings import HuggingFaceEmbeddings

                backend = HuggingFaceEmbeddings(model_name=spec.model_id)
                return DimensionNormalizedEmbeddings(backend, target_dim)
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "embedding_provider_fallback",
                provider=provider,
                model=spec.model_id,
                error=str(exc),
            )

        logger.info("using_local_hash_embeddings", dim=target_dim, intended_model=spec.model_id)
        return LocalHashEmbeddings(dim=target_dim)

    @staticmethod
    def catalog() -> list[dict]:
        return [
            {
                "key": m.key,
                "provider": m.provider,
                "model_id": m.model_id,
                "dimensions": m.dimensions,
                "description": m.description,
            }
            for m in EMBEDDING_MODELS
        ]


@lru_cache
def get_embeddings():
    return EmbeddingFactory.create()


def reset_embeddings_cache() -> None:
    get_embeddings.cache_clear()
