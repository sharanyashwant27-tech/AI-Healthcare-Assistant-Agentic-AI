# Folder Structure

```text
ai-healthcare-assistant/
│
├── backend/
│   ├── agents/
│   ├── workflows/
│   ├── rag/
│   ├── graphrag/
│   ├── embeddings/
│   ├── vectordb/
│   ├── models/
│   ├── api/
│   ├── auth/
│   ├── services/
│   ├── database/
│   ├── prompts/
│   ├── utils/
│   └── main.py
│
├── frontend/
├── n8n/
├── docker/
├── docs/
├── tests/
└── README.md
```

## Backend notes

| Folder | Role |
|---|---|
| `agents/` | Master + specialist agents (LangGraph / CrewAI) |
| `workflows/` | n8n trigger helpers + catalog |
| `rag/` | RAG pipeline + knowledge sources |
| `graphrag/` | Neo4j GraphRAG |
| `embeddings/` | Content types + embedding models |
| `vectordb/` | Qdrant / Pinecone / Milvus |
| `models/` | SQLAlchemy models (Patients…MedicalHistory) — see `docs/DATABASE.md` |
| `api/` | FastAPI routers |
| `auth/` | JWT security + auth dependencies |
| `services/` | Domain services |
| `database/` | Engine, session, `Base`, `init_db` |
| `prompts/` | System prompt, templates, few-shot, dynamic |
| `utils/` | LLM, OCR, storage, seed |
| `main.py` | FastAPI entrypoint (`uvicorn main:app`) |

Supporting packages also under `backend/`: `core/` (config/logging/redis), `schemas/`, `repositories/`, `middleware/`.

## Top-level

| Path | Role |
|---|---|
| `frontend/` | Next.js app (`:8911`) |
| `n8n/workflows/` | Importable n8n workflow JSON |
| `docker/` | Dockerfiles + compose mirror |
| `docs/` | Architecture and module docs |
| `tests/` | Pytest suites (`pythonpath=backend`) |
| `infra/` | Kubernetes, Helm, monitoring, ELK |
