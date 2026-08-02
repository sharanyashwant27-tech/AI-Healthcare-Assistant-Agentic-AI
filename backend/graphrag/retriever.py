"""GraphRAG retrieval combining Neo4j reasoning with vector search."""

from typing import Any, Dict, List, Optional

from graphrag.langchain_graphrag import LangChainGraphRAG


class GraphRAGRetriever:
    def __init__(self) -> None:
        self.engine = LangChainGraphRAG()

    async def retrieve(
        self,
        query: str,
        symptoms: Optional[List[str]] = None,
        patient_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        return await self.engine.aquery(query, symptoms=symptoms, patient_key=patient_key)
