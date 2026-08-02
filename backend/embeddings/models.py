"""Supported embedding model catalog."""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class EmbeddingModelSpec:
    key: str
    provider: str
    model_id: str
    dimensions: int
    description: str


EMBEDDING_MODELS: List[EmbeddingModelSpec] = [
    EmbeddingModelSpec(
        key="openai-large",
        provider="openai",
        model_id="text-embedding-3-large",
        dimensions=3072,
        description="OpenAI text-embedding-3-large",
    ),
    EmbeddingModelSpec(
        key="bge-large",
        provider="bge-large",
        model_id="BAAI/bge-large-en-v1.5",
        dimensions=1024,
        description="BGE Large (BAAI/bge-large-en-v1.5)",
    ),
    EmbeddingModelSpec(
        key="e5-large",
        provider="e5-large",
        model_id="intfloat/e5-large-v2",
        dimensions=1024,
        description="E5 Large (intfloat/e5-large-v2)",
    ),
]

MODEL_BY_KEY: Dict[str, EmbeddingModelSpec] = {m.key: m for m in EMBEDDING_MODELS}


def resolve_model_spec(provider: Optional[str], model: Optional[str]) -> EmbeddingModelSpec:
    provider = (provider or "").lower()
    model = model or ""

    if provider in {"openai"} or "text-embedding-3-large" in model:
        return MODEL_BY_KEY["openai-large"]
    if provider in {"bge-large", "bge"} or "bge-large" in model:
        return MODEL_BY_KEY["bge-large"]
    if provider in {"e5-large", "e5"} or "e5-large" in model:
        return MODEL_BY_KEY["e5-large"]

    # Default recommended production embedding
    return MODEL_BY_KEY["openai-large"]
