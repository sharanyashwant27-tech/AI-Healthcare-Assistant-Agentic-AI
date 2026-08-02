# Development Roadmap

Suggested phased delivery for **AI Healthcare Assistant**. Status reflects the current codebase.

| Phase | Deliverable | Status |
| ------- | ---------------------------------------------------------------- | ------ |
| Phase 1 | FastAPI backend, authentication, patient management | Done |
| Phase 2 | AI chat with RAG over medical knowledge | Done |
| Phase 3 | Multi-agent orchestration using LangGraph/CrewAI | Done |
| Phase 4 | Neo4j-based GraphRAG integration | Done |
| Phase 5 | OCR for prescriptions and lab reports | Done |
| Phase 6 | n8n automation for appointments, reminders, and emergency alerts | Done |
| Phase 7 | Monitoring, testing, Docker, Kubernetes deployment | Done |

---

## Phase 1 — FastAPI backend, authentication, patient management

**Goals:** Core API, JWT auth, RBAC, patient/doctor profiles, appointments, dashboards.

**Implemented**
- FastAPI app (`backend/main.py`) on `:8000`
- `POST /api/v1/register`, `POST /api/v1/login`, JWT + RBAC
- Models: Patients, Doctors, Appointments, Hospitals, …
- Dashboards: patient / doctor / admin
- Security: audit logging, consent, AES-256 helpers, PHI masking

**Key paths:** `backend/api/`, `backend/auth/`, `backend/models/`, `docs/DATABASE.md`, `docs/SECURITY.md`

---

## Phase 2 — AI chat with RAG over medical knowledge

**Goals:** Grounded answers from medical sources via embeddings + vector DB.

**Implemented**
- Master chat (`POST /api/v1/chat`)
- RAG pipeline: load → chunk → embed → retrieve → LLM
- Collections for guidelines, books, research, patient history, labs, notes, Rx
- Embedding models: OpenAI large, BGE Large, E5 Large

**Key paths:** `backend/rag/`, `backend/embeddings/`, `backend/vectordb/`, `docs/RAG.md`, `docs/EMBEDDINGS.md`

---

## Phase 3 — Multi-agent orchestration (LangGraph / CrewAI)

**Goals:** Master agent routes to specialists with planned tool use.

**Implemented**
- LangGraph: understand → plan → execute
- CrewAI / AutoGen via `AGENT_FRAMEWORK`
- Specialists: symptom, medical knowledge, prescription, lab, nutrition, appointment, insurance, emergency, reminder, follow-up, memory

**Key paths:** `backend/agents/`, `docs/AGENTS.md`

---

## Phase 4 — Neo4j GraphRAG

**Goals:** Patient-centered knowledge graph retrieval alongside vector RAG.

**Implemented**
- Neo4j client + memory fallback
- GraphRAG query APIs and example patient paths
- Combined use from medical knowledge agent

**Key paths:** `backend/graphrag/`, `docs/GRAPHRAG.md`

---

## Phase 5 — OCR for prescriptions and lab reports

**Goals:** Document upload → OCR → AI extraction / analysis.

**Implemented**
- `POST /api/v1/prescription` (OCR + medicine extraction + interactions)
- `POST /api/v1/lab-report` (OCR + AI summary)
- Tesseract / Whisper utilities

**Key paths:** `backend/agents/prescription_agent.py`, `backend/agents/lab_agent.py`, `backend/utils/speech.py`

---

## Phase 6 — n8n automation

**Goals:** Workflow automation for registration, appointments, emergency, Rx, labs.

**Implemented**
- Five n8n pipelines under `n8n/workflows/`
- Backend triggers on register, book, emergency, prescription, lab
- UI catalog at `/workflows`

**Key paths:** `n8n/workflows/`, `backend/workflows/`, `docs/N8N.md`

---

## Phase 7 — Monitoring, testing, Docker, Kubernetes

**Goals:** Operability and deployability.

**Implemented**
- Pytest suite (`tests/`, 9+ tests)
- Docker Compose (`docker-compose.yml`, `docker/`)
- Prometheus / Grafana / ELK configs under `infra/`
- Kubernetes + Helm stubs under `infra/kubernetes`, `infra/helm`
- GitHub Actions CI under `.github/workflows`

**Key paths:** `docs/INSTALLATION.md`, `infra/`, `docker/`

---

## Suggested next hardening (post Phase 7)

| Area | Next step |
| --- | --- |
| Production TLS | Terminate HTTPS at nginx/ingress; set `TLS_ENABLED=true` |
| Secrets | Move API keys to Vault/KMS; rotate `SECRET_KEY` / `ENCRYPTION_KEY` |
| Graph/Vector | Run Neo4j + Qdrant in Compose for full RAG/GraphRAG (not memory fallback) |
| Eval | Expand golden sets; wire `POST /eval/run` into CI |
| Load | Locust/k6 smoke against chat + appointment APIs |
| Voice | Install `gTTS` / Whisper models for production voice consults |
| FHIR | Map full EHR sync jobs beyond read scaffolds |

## Advanced AI (implemented)

See [`docs/ADVANCED_AI.md`](ADVANCED_AI.md) for multi-agent collaboration, hybrid retrieval, memory, confidence/citations, HITL, XAI, voice, multilingual, FHIR/HL7, and continuous evaluation.

## How to use this roadmap

1. Treat Phases 1–7 as the **baseline product** already in-repo.
2. Use the hardening table for production readiness.
3. Track feature docs from [`docs/STRUCTURE.md`](STRUCTURE.md) and [`docs/MODULES.md`](MODULES.md).
