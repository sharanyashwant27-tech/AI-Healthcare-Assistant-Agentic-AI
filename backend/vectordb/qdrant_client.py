"""Qdrant vector database integration (recommended default)."""

from typing import Any, Dict, List, Optional
from uuid import uuid4

from core.config import settings
from core.logging import get_logger
from embeddings.factory import get_embeddings
from vectordb.collections import COLLECTIONS

logger = get_logger(__name__)


class InMemoryVectorStore:
    """Fallback store when Qdrant/Milvus/Pinecone is unavailable."""

    def __init__(self) -> None:
        self.data: Dict[str, List[Dict[str, Any]]] = {c: [] for c in COLLECTIONS}

    def upsert(self, collection: str, points: List[Dict[str, Any]]) -> None:
        self.data.setdefault(collection, []).extend(points)

    def search(self, collection: str, vector: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        import math

        docs = self.data.get(collection, [])

        def score(doc: Dict[str, Any]) -> float:
            v = doc.get("vector") or []
            if not v or len(v) != len(vector):
                return 0.0
            dot = sum(a * b for a, b in zip(vector, v))
            na = math.sqrt(sum(a * a for a in vector)) or 1.0
            nb = math.sqrt(sum(b * b for b in v)) or 1.0
            return dot / (na * nb)

        ranked = sorted(docs, key=score, reverse=True)[:limit]
        return [
            {"id": d["id"], "score": score(d), "payload": d.get("payload", {})}
            for d in ranked
        ]


class QdrantService:
    def __init__(self) -> None:
        self._client = None
        self._memory = InMemoryVectorStore()
        self._use_memory = False
        self.embeddings = get_embeddings()
        self.provider = "qdrant"
        self._connect()

    def _connect(self) -> None:
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.http import models as qm

            self._client = QdrantClient(
                url=settings.qdrant_url,
                api_key=settings.qdrant_api_key or None,
                timeout=5,
            )
            self._client.get_collections()
            for name in COLLECTIONS:
                exists = False
                try:
                    self._client.get_collection(name)
                    exists = True
                except Exception:  # noqa: BLE001
                    exists = False
                if not exists:
                    self._client.create_collection(
                        collection_name=name,
                        vectors_config=qm.VectorParams(
                            size=settings.embedding_dimensions,
                            distance=qm.Distance.COSINE,
                        ),
                    )
            logger.info("qdrant_connected", url=settings.qdrant_url, collections=COLLECTIONS)
        except Exception as exc:  # noqa: BLE001
            logger.warning("qdrant_fallback_memory", error=str(exc))
            self._use_memory = True
            self._client = None

    def _vector(self, text: str) -> List[float]:
        dim = settings.embedding_dimensions
        vec = self.embeddings.embed_query(text)
        if len(vec) > dim:
            return vec[:dim]
        if len(vec) < dim:
            return vec + [0.0] * (dim - len(vec))
        return vec

    def upsert_texts(
        self,
        collection: str,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> List[str]:
        if collection not in COLLECTIONS:
            # Allow extension but keep unknown collections in memory bucket
            self._memory.data.setdefault(collection, [])
        metadatas = metadatas or [{} for _ in texts]
        ids: List[str] = []
        points: List[Dict[str, Any]] = []
        for text, meta in zip(texts, metadatas):
            pid = str(uuid4())
            ids.append(pid)
            vector = self._vector(text)
            payload = {**meta, "text": text}
            points.append({"id": pid, "vector": vector, "payload": payload})

        if self._use_memory or self._client is None:
            self._memory.upsert(collection, points)
            return ids

        from qdrant_client.http import models as qm

        self._client.upsert(
            collection_name=collection,
            points=[
                qm.PointStruct(id=p["id"], vector=p["vector"], payload=p["payload"])
                for p in points
            ],
        )
        return ids

    def search(self, collection: str, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        vector = self._vector(query)
        if self._use_memory or self._client is None:
            return self._memory.search(collection, vector, limit=limit)

        hits = self._client.search(collection_name=collection, query_vector=vector, limit=limit)
        return [
            {"id": str(h.id), "score": float(h.score), "payload": h.payload or {}}
            for h in hits
        ]

    def health(self) -> str:
        return "memory" if self._use_memory else "qdrant"

    def describe(self) -> Dict[str, Any]:
        return {
            "provider": self.provider,
            "status": self.health(),
            "collections": COLLECTIONS,
        }


_service: Optional[QdrantService] = None


def get_qdrant_service() -> QdrantService:
    global _service
    if _service is None:
        _service = QdrantService()
    return _service
