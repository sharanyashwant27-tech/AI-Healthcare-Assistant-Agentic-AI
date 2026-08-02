"""
RAG Pipeline

Medical documents
    ↓
PDF / Document Loader
    ↓
Chunking
    ↓
Embeddings
    ↓
Vector Database
    ↓
Retriever
    ↓
LLM
    ↓
Answer
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from core.config import settings
from core.logging import get_logger
from embeddings.factory import get_embeddings
from prompts.registry import get_prompt_registry
from rag.knowledge_sources import (
    KNOWLEDGE_SOURCES,
    PIPELINE_STAGES,
    SOURCE_BY_KEY,
)
from vectordb.collections import DEFAULT_RETRIEVAL_COLLECTIONS
from rag.loaders import load_document
from utils.llm import generate_text
from vectordb.factory import get_vector_service

logger = get_logger(__name__)


class RAGPipeline:
    """Full medical RAG pipeline with source-aware retrieval."""

    stages = PIPELINE_STAGES
    knowledge_sources = KNOWLEDGE_SOURCES

    def __init__(self) -> None:
        self.vector_db = get_vector_service()
        self.embeddings = get_embeddings()
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=120,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        self.prompts = get_prompt_registry()

    # ---- Stage helpers -------------------------------------------------

    def load_documents(self, path: str | Path) -> List[Document]:
        """Loader stage: PDF / text / Word / CSV."""
        return load_document(path)

    def chunk_documents(self, docs: List[Document]) -> List[Document]:
        """Chunking stage."""
        return self.splitter.split_documents(docs)

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embeddings stage."""
        if hasattr(self.embeddings, "embed_documents"):
            return self.embeddings.embed_documents(texts)
        return [self.embeddings.embed_query(t) for t in texts]

    def extract_metadata(self, doc: Document, source_key: str = "general") -> Dict[str, Any]:
        text = doc.page_content[:500]
        meta = dict(doc.metadata)
        meta["char_count"] = len(doc.page_content)
        meta["preview"] = text.replace("\n", " ")[:200]
        meta["knowledge_source"] = source_key
        if source_key in SOURCE_BY_KEY:
            meta["knowledge_source_name"] = SOURCE_BY_KEY[source_key].name
        return meta

    def resolve_collection(self, source_key: str, fallback: str = "hospital_guidelines") -> str:
        src = SOURCE_BY_KEY.get(source_key)
        return src.collection if src else fallback

    # ---- Ingest --------------------------------------------------------

    def ingest_file(
        self,
        path: str | Path,
        source_key: str = "sop",
        collection: Optional[str] = None,
    ) -> Dict[str, Any]:
        docs = self.load_documents(path)
        for d in docs:
            d.metadata["source_type"] = source_key
        chunks = self.chunk_documents(docs)
        texts = [c.page_content for c in chunks]
        metadatas = [self.extract_metadata(c, source_key) for c in chunks]
        target = collection or self.resolve_collection(source_key)
        ids = self.vector_db.upsert_texts(target, texts, metadatas)
        logger.info("rag_ingested_file", path=str(path), chunks=len(chunks), collection=target)
        return {
            "path": str(path),
            "source": source_key,
            "collection": target,
            "chunks": len(chunks),
            "ids": ids,
            "stages": self.stages,
        }

    def ingest_texts(
        self,
        texts: List[str],
        collection: str,
        source_type: str = "general",
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> int:
        docs = [
            Document(
                page_content=t,
                metadata={"source_type": source_type, **(metadatas[i] if metadatas else {})},
            )
            for i, t in enumerate(texts)
        ]
        chunks = self.chunk_documents(docs)
        self.vector_db.upsert_texts(
            collection,
            [c.page_content for c in chunks],
            [self.extract_metadata(c, source_type) for c in chunks],
        )
        return len(chunks)

    def ingest_knowledge_corpus(self) -> Dict[str, int]:
        """Seed all configured knowledge sources with sample medical content."""
        corpus: Dict[str, List[Dict[str, str]]] = {
            "who": [
                {
                    "text": (
                        "WHO guidance: Hand hygiene, vaccination, and respiratory etiquette "
                        "reduce influenza transmission. Seek care for severe breathing difficulty."
                    )
                },
                {
                    "text": (
                        "WHO clinical note: Antimicrobial stewardship requires culture-guided therapy "
                        "whenever feasible and avoidance of unnecessary antibiotics."
                    )
                },
            ],
            "cdc": [
                {
                    "text": (
                        "CDC guidance: Seek emergency care for chest pain, stroke signs (FAST), "
                        "severe allergic reaction, or difficulty breathing."
                    )
                },
                {
                    "text": (
                        "CDC immunization guidance: Stay current with recommended adult and pediatric "
                        "vaccination schedules as advised by clinicians."
                    )
                },
            ],
            "sop": [
                {
                    "text": (
                        "Hospital SOP: Patients with chest pain or suspected stroke must be escalated "
                        "to the emergency pathway immediately. AI assists documentation only."
                    )
                }
            ],
            "drug": [
                {
                    "text": (
                        "Drug database: Paracetamol (acetaminophen) is used for fever/pain. "
                        "Follow labeled dosing; caution with liver disease and warfarin interactions."
                    )
                },
                {
                    "text": (
                        "Drug database: Ibuprofen is an NSAID. Avoid in active GI bleeding; "
                        "may interact with anticoagulants and other NSAIDs."
                    )
                },
            ],
            "books": [
                {
                    "text": (
                        "Medical book excerpt: Migraine is a primary headache disorder. Management may "
                        "include trigger avoidance and clinician-guided acute/preventive therapy."
                    )
                }
            ],
            "research": [
                {
                    "text": (
                        "Research summary: Early recognition of sepsis and rapid antibiotics improve "
                        "outcomes; this is not a substitute for institutional sepsis protocols."
                    )
                }
            ],
            "policies": [
                {
                    "text": (
                        "Hospital policy: Informed consent is required before invasive procedures. "
                        "Emergency exceptions follow local legal and clinical policy."
                    )
                },
                {
                    "text": (
                        "Hospital policy: Medication reconciliation must be completed at admission "
                        "and discharge by authorized clinical staff."
                    )
                },
            ],
            "insurance": [
                {
                    "text": (
                        "Insurance rules: In-network outpatient consultations at City General Hospital "
                        "are typically claim-eligible under HealthPlus Gold subject to deductible."
                    )
                },
                {
                    "text": (
                        "Insurance rules: Prior authorization may be required for MRI and elective "
                        "specialty procedures. Final adjudication is by the insurer."
                    )
                },
            ],
            "patient": [
                {
                    "text": (
                        "Patient history: Adult with history of seasonal allergies; "
                        "no penicillin allergy documented in this sample record."
                    )
                }
            ],
            "labs": [
                {
                    "text": (
                        "Lab report: Fasting glucose 118 mg/dL (mildly elevated). "
                        "Creatinine within reference range in this sample report."
                    )
                }
            ],
            "notes": [
                {
                    "text": (
                        "Doctor note: Follow-up for type 2 diabetes. Discuss lifestyle measures "
                        "and medication adherence; refer to licensed clinician for plan changes."
                    )
                }
            ],
            "rx": [
                {
                    "text": (
                        "Prescription: Metformin 500 mg twice daily with meals. "
                        "Counsel on GI side effects; do not change dosing without a clinician."
                    )
                }
            ],
        }

        counts: Dict[str, int] = {}
        for key, items in corpus.items():
            collection = self.resolve_collection(key)
            n = self.ingest_texts(
                [i["text"] for i in items],
                collection=collection,
                source_type=key,
                metadatas=[{"source": SOURCE_BY_KEY[key].name, "knowledge_source": key} for _ in items],
            )
            counts[key] = n
        logger.info("rag_knowledge_corpus_seeded", counts=counts)
        return counts

    # ---- Retrieve + Answer ---------------------------------------------

    def retrieve(
        self,
        query: str,
        collections: Optional[List[str]] = None,
        source_keys: Optional[List[str]] = None,
        limit: int = 6,
    ) -> List[Dict[str, Any]]:
        """Retriever stage over one or more knowledge collections."""
        if source_keys:
            collections = [self.resolve_collection(k) for k in source_keys]
        collections = collections or DEFAULT_RETRIEVAL_COLLECTIONS
        # de-dupe while preserving order
        seen = set()
        ordered = []
        for c in collections:
            if c not in seen:
                seen.add(c)
                ordered.append(c)

        results: List[Dict[str, Any]] = []
        per = max(1, limit // len(ordered))
        for coll in ordered:
            hits = self.vector_db.search(coll, query, limit=per)
            for h in hits:
                payload = h.get("payload") or {}
                results.append(
                    {
                        **h,
                        "collection": coll,
                        "knowledge_source": payload.get("knowledge_source_name")
                        or payload.get("knowledge_source")
                        or coll,
                    }
                )
        results.sort(key=lambda x: x.get("score", 0), reverse=True)
        return results[:limit]

    async def answer(
        self,
        query: str,
        collections: Optional[List[str]] = None,
        source_keys: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        End-to-end RAG:
        retrieve context → LLM generation → answer + citations.
        """
        sources = self.retrieve(query, collections=collections, source_keys=source_keys)
        context = "\n\n".join(
            f"[{s.get('knowledge_source')}|{s.get('collection')}] "
            f"{s.get('payload', {}).get('text', '')[:800]}"
            for s in sources
        ) or (
            "No retrieved documents from WHO/CDC/SOP/drug/book/research/policy stores. "
            "Answer cautiously and state evidence limitations."
        )

        prompt = self.prompts.as_langchain("medical_knowledge").format(
            context=context,
            input=query,
        )
        answer = await generate_text(prompt)
        return {
            "answer": answer,
            "sources": sources,
            "pipeline": self.stages,
            "knowledge_sources": [s.name for s in self.knowledge_sources],
            "disclaimer": settings.medical_disclaimer,
        }

    def describe(self) -> Dict[str, Any]:
        return {
            "pipeline": self.stages,
            "knowledge_sources": [
                {
                    "key": s.key,
                    "name": s.name,
                    "collection": s.collection,
                    "description": s.description,
                }
                for s in self.knowledge_sources
            ],
            "vector_db": getattr(self.vector_db, "health", lambda: "unknown")(),
        }


_pipeline: Optional[RAGPipeline] = None


def get_rag_pipeline() -> RAGPipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = RAGPipeline()
    return _pipeline
