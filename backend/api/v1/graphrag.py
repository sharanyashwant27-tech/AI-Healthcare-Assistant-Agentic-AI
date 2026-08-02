"""GraphRAG API — Neo4j knowledge graph reasoning + retrieval."""

from typing import List, Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from auth.deps import CurrentUser
from graphrag.neo4j_client import get_graph_service
from graphrag.retriever import GraphRAGRetriever
from schemas.common import MedicalDisclaimerMixin

router = APIRouter()


class GraphRAGQuery(BaseModel):
    query: str = Field(min_length=2, max_length=4000)
    symptoms: Optional[List[str]] = None
    patient_key: Optional[str] = "john"


class GraphRAGResponse(MedicalDisclaimerMixin):
    answer: str
    explanation_path: list = []
    neighborhood: dict = {}
    vector_sources: list = []
    benefits: list = []
    database: str = "Neo4j"
    framework: str = "langchain-graphrag-neo4j"


@router.get("/graphrag")
async def describe_graph(user: CurrentUser):
    return get_graph_service().describe()


@router.get("/graphrag/patient/{patient_key}")
async def patient_graph(patient_key: str, user: CurrentUser):
    graph = get_graph_service()
    return {
        "patient_key": patient_key,
        "neighborhood": graph.patient_neighborhood(patient_key),
        "explanation_path": graph.explain_path(patient_key),
        "schema": graph.describe(),
    }


@router.get("/graphrag/example")
async def example_path(user: CurrentUser, patient_key: str = Query(default="john")):
    graph = get_graph_service()
    return {
        "example": "John → Diabetes → Metformin → Kidney Disease → Creatinine Test → Doctor → Hospital",
        "path": graph.explain_path(patient_key),
        "benefits": graph.BENEFITS,
    }


@router.post("/graphrag/query", response_model=GraphRAGResponse)
async def graphrag_query(data: GraphRAGQuery, user: CurrentUser):
    result = await GraphRAGRetriever().retrieve(
        data.query,
        symptoms=data.symptoms,
    )
    # Ensure patient-specific path if requested
    if data.patient_key:
        graph = get_graph_service()
        result["explanation_path"] = graph.explain_path(data.patient_key)
        result["neighborhood"] = graph.patient_neighborhood(data.patient_key)
    return GraphRAGResponse(
        answer=result.get("answer") or "",
        explanation_path=result.get("explanation_path") or [],
        neighborhood=result.get("neighborhood") or {},
        vector_sources=result.get("vector_sources") or [],
        benefits=result.get("benefits") or get_graph_service().BENEFITS,
        database=result.get("database") or "Neo4j",
        framework=result.get("framework") or "langchain-graphrag-neo4j",
    )
