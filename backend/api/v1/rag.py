"""RAG pipeline API — ingest and query medical knowledge sources."""

from typing import List, Optional

from fastapi import APIRouter, File, Form, UploadFile
from pydantic import BaseModel, Field

from core.config import settings
from auth.deps import CurrentUser
from rag.knowledge_sources import KNOWLEDGE_SOURCES, PIPELINE_STAGES
from rag.pipeline import get_rag_pipeline
from schemas.common import MedicalDisclaimerMixin
from utils.storage import get_storage

router = APIRouter()


class RAGQueryRequest(BaseModel):
    query: str = Field(min_length=2, max_length=4000)
    source_keys: Optional[List[str]] = None


class RAGQueryResponse(MedicalDisclaimerMixin):
    answer: str
    sources: list = []
    pipeline: list[str] = Field(default_factory=lambda: list(PIPELINE_STAGES))
    knowledge_sources: list[str] = []


@router.get("/rag")
async def rag_describe(user: CurrentUser):
    return get_rag_pipeline().describe()


@router.post("/rag/query", response_model=RAGQueryResponse)
async def rag_query(data: RAGQueryRequest, user: CurrentUser):
    result = await get_rag_pipeline().answer(data.query, source_keys=data.source_keys)
    return RAGQueryResponse(**result)


@router.post("/rag/ingest")
async def rag_ingest(
    user: CurrentUser,
    source_key: str = Form(default="sop"),
    file: UploadFile = File(...),
):
    data = await file.read()
    uri = get_storage().save_bytes(
        data, file.filename or "document.pdf", file.content_type or "application/pdf"
    )
    # Prefer local path for loader when storage is local filesystem
    path = uri.replace("minio://", "")
    from pathlib import Path

    local = Path(settings.upload_dir) / Path(file.filename or "document.pdf").name
    if not local.exists():
        local.write_bytes(data)
        path = str(local)
    elif not Path(path).exists():
        path = str(local)

    result = get_rag_pipeline().ingest_file(path, source_key=source_key)
    return result


@router.post("/rag/seed")
async def rag_seed(user: CurrentUser):
    counts = get_rag_pipeline().ingest_knowledge_corpus()
    return {
        "seeded": counts,
        "knowledge_sources": [s.name for s in KNOWLEDGE_SOURCES],
        "pipeline": PIPELINE_STAGES,
    }
