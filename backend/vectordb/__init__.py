"""Vector database integration — Qdrant / Pinecone / Milvus."""

from vectordb.collections import COLLECTIONS, VECTOR_DB_PROVIDERS
from vectordb.factory import describe_vector_db, get_vector_service
from vectordb.qdrant_client import QdrantService, get_qdrant_service

__all__ = [
    "COLLECTIONS",
    "VECTOR_DB_PROVIDERS",
    "get_vector_service",
    "describe_vector_db",
    "QdrantService",
    "get_qdrant_service",
]
