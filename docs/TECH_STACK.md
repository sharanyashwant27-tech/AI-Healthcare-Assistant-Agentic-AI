# Technology Stack

| Category | Technology | Project status |
| --- | --- | --- |
| Language | Python 3.12 | Implemented |
| IDE | Cursor | Used for development |
| Backend | FastAPI | Implemented (`backend/app`) |
| Frontend | React + Next.js | Implemented (`frontend`, port 8911) |
| AI Framework | LangGraph | Implemented (`agents/langgraph_workflow.py`) |
| Agent Framework | CrewAI / AutoGen | Both supported via `AGENT_FRAMEWORK` |
| LLM | GPT, Claude, Gemini, Llama | Factory in `utils/llm.py` |
| Prompt Engineering | System + templates + few-shot + dynamic | `prompts/` — see `docs/PROMPTS.md` |
| Embeddings | OpenAI text-embedding-3-large, BGE Large, E5 Large | `embeddings/factory.py` |
| Vector Database | Qdrant / Milvus / Pinecone | `VECTOR_DB_PROVIDER` factory |
| Graph Database | Neo4j | Implemented + memory fallback |
| GraphRAG | LangChain GraphRAG | `graphrag/langchain_graphrag.py` |
| Database | PostgreSQL | Docker Compose; local SQLite fallback |
| Cache | Redis | Conversation memory + cache client |
| Storage | MinIO | `utils/storage.py` + Compose service |
| OCR | Tesseract | Prescription/Lab agents + `utils/speech.py` |
| Speech | Whisper | `utils/speech.py` |
| Authentication | JWT | Access + refresh tokens, RBAC |
| Security | AES-256, consent, PHI masking, audit | `security/` — see `docs/SECURITY.md` |
| Workflow | n8n | Five pipelines in `n8n/workflows` — see `docs/N8N.md` |
| Monitoring | Prometheus + Grafana | Compose + `/metrics` |
| Logging | ELK | Structured logs + Logstash config |
| Deployment | Docker + Kubernetes | Compose, K8s manifests, Helm |

## Environment switches

```env
DEFAULT_LLM_PROVIDER=openai|anthropic|google|llama
DEFAULT_EMBEDDING_PROVIDER=openai|bge-large|e5-large
DEFAULT_EMBEDDING_MODEL=text-embedding-3-large
EMBEDDING_DIMENSIONS=1024
VECTOR_DB_PROVIDER=qdrant|milvus|pinecone
AGENT_FRAMEWORK=crewai|autogen
MINIO_ENDPOINT=localhost:9000
USE_SQLITE=false   # production / Compose Postgres
```
