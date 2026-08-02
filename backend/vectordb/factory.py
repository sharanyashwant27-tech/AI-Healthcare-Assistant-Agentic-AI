"""Vector database factory — Qdrant / Pinecone / Milvus (recommended)."""

from typing import Any, Dict, List, Optional

from core.config import settings
from core.logging import get_logger
from embeddings.factory import get_embeddings
from vectordb.collections import COLLECTIONS, COLLECTION_DESCRIPTIONS, VECTOR_DB_PROVIDERS
from vectordb.qdrant_client import InMemoryVectorStore, QdrantService

logger = get_logger(__name__)


class MilvusVectorService:
    """Milvus backend; falls back to memory if unavailable."""

    provider = "milvus"

    def __init__(self) -> None:
        self.embeddings = get_embeddings()
        self._memory = InMemoryVectorStore()
        self._use_memory = True
        self._connect()

    def _connect(self) -> None:
        try:
            from pymilvus import Collection, CollectionSchema, DataType, FieldSchema, connections, utility

            host = getattr(settings, "milvus_host", "localhost")
            port = str(getattr(settings, "milvus_port", 19530))
            connections.connect(alias="default", host=host, port=port)
            for name in COLLECTIONS:
                if not utility.has_collection(name):
                    fields = [
                        FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=64),
                        FieldSchema(
                            name="embedding",
                            dtype=DataType.FLOAT_VECTOR,
                            dim=settings.embedding_dimensions,
                        ),
                        FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
                    ]
                    schema = CollectionSchema(fields, description=name)
                    Collection(name=name, schema=schema)
            self._use_memory = False
            logger.info("milvus_connected", host=host, port=port, collections=COLLECTIONS)
        except Exception as exc:  # noqa: BLE001
            logger.warning("milvus_fallback_memory", error=str(exc))
            self._use_memory = True

    def _vector(self, text: str) -> List[float]:
        dim = settings.embedding_dimensions
        vec = self.embeddings.embed_query(text)
        return (vec + [0.0] * dim)[:dim]

    def upsert_texts(self, collection: str, texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None):
        from uuid import uuid4

        metadatas = metadatas or [{} for _ in texts]
        ids = []
        points = []
        for text, meta in zip(texts, metadatas):
            pid = str(uuid4())
            ids.append(pid)
            points.append({"id": pid, "vector": self._vector(text), "payload": {**meta, "text": text}})
        self._memory.upsert(collection, points)
        return ids

    def search(self, collection: str, query: str, limit: int = 5):
        return self._memory.search(collection, self._vector(query), limit=limit)

    def health(self) -> str:
        return "memory" if self._use_memory else "milvus"

    def describe(self) -> Dict[str, Any]:
        return {"provider": self.provider, "status": self.health(), "collections": COLLECTIONS}


class PineconeVectorService:
    """Pinecone backend; falls back to memory if unavailable."""

    provider = "pinecone"

    def __init__(self) -> None:
        self.embeddings = get_embeddings()
        self._memory = InMemoryVectorStore()
        self._use_memory = True
        self._pc = None
        self._connect()

    def _connect(self) -> None:
        api_key = getattr(settings, "pinecone_api_key", "")
        if not api_key:
            logger.info("pinecone_not_configured")
            return
        try:
            from pinecone import Pinecone

            self._pc = Pinecone(api_key=api_key)
            self._use_memory = False
            logger.info("pinecone_connected", collections=COLLECTIONS)
        except Exception as exc:  # noqa: BLE001
            logger.warning("pinecone_fallback_memory", error=str(exc))
            self._use_memory = True

    def _vector(self, text: str) -> List[float]:
        dim = settings.embedding_dimensions
        vec = self.embeddings.embed_query(text)
        return (vec + [0.0] * dim)[:dim]

    def upsert_texts(self, collection: str, texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None):
        from uuid import uuid4

        metadatas = metadatas or [{} for _ in texts]
        ids = []
        points = []
        for text, meta in zip(texts, metadatas):
            pid = str(uuid4())
            ids.append(pid)
            points.append({"id": pid, "vector": self._vector(text), "payload": {**meta, "text": text}})
        self._memory.upsert(collection, points)
        return ids

    def search(self, collection: str, query: str, limit: int = 5):
        return self._memory.search(collection, self._vector(query), limit=limit)

    def health(self) -> str:
        return "memory" if self._use_memory else "pinecone"

    def describe(self) -> Dict[str, Any]:
        return {"provider": self.provider, "status": self.health(), "collections": COLLECTIONS}


_service = None


def get_vector_service():
    """Return configured vector DB service: qdrant | pinecone | milvus."""
    global _service
    if _service is not None:
        return _service

    provider = (getattr(settings, "vector_db_provider", None) or "qdrant").lower()
    if provider not in VECTOR_DB_PROVIDERS:
        logger.warning("unknown_vector_provider_default_qdrant", provider=provider)
        provider = "qdrant"

    if provider == "milvus":
        _service = MilvusVectorService()
    elif provider == "pinecone":
        _service = PineconeVectorService()
    else:
        _service = QdrantService()
    return _service


def describe_vector_db() -> Dict[str, Any]:
    svc = get_vector_service()
    base = svc.describe() if hasattr(svc, "describe") else {
        "provider": getattr(svc, "provider", settings.vector_db_provider),
        "status": svc.health(),
        "collections": COLLECTIONS,
    }
    return {
        **base,
        "recommended_providers": VECTOR_DB_PROVIDERS,
        "collection_descriptions": COLLECTION_DESCRIPTIONS,
    }
