"""Embeddings catalog API — content types and models."""

from fastapi import APIRouter

from core.config import settings
from auth.deps import CurrentUser
from embeddings.content_types import EMBEDDING_CONTENT_TYPES
from embeddings.factory import EmbeddingFactory
from embeddings.models import resolve_model_spec

router = APIRouter()


@router.get("/embeddings")
async def embeddings_info(user: CurrentUser):
    active = resolve_model_spec(
        settings.default_embedding_provider,
        settings.default_embedding_model,
    )
    return {
        "content_types": [
            {
                "key": c.key,
                "name": c.name,
                "collection": c.collection,
                "description": c.description,
            }
            for c in EMBEDDING_CONTENT_TYPES
        ],
        "models": EmbeddingFactory.catalog(),
        "active": {
            "provider": settings.default_embedding_provider,
            "model": settings.default_embedding_model,
            "model_id": active.model_id,
            "native_dimensions": active.dimensions,
            "store_dimensions": settings.embedding_dimensions,
        },
        "pipeline": [
            "Content type documents",
            "Loader / OCR",
            "Chunking",
            "Embedding model",
            "Vector collection",
            "Retriever → LLM",
        ],
    }
