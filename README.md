# AI Healthcare Assistant (Agentic AI)

Enterprise agentic AI platform for patients, doctors, hospitals, and administrators.

**Repository:** [sharanyashwant27-tech/AI-Healthcare-Assistant-Agentic-AI](https://github.com/sharanyashwant27-tech/AI-Healthcare-Assistant-Agentic-AI)

**Not a medical device. Never diagnoses with certainty. Always recommends licensed clinical care.**

## Stack

See full matrix in [`docs/TECH_STACK.md`](docs/TECH_STACK.md).

| Category | Technology |
| --- | --- |
| Language | Python 3.12 |
| Backend | FastAPI |
| Frontend | React + Next.js (`:8911`) |
| AI Framework | LangGraph |
| Agent Framework | CrewAI / AutoGen |
| LLM | GPT, Claude, Gemini, Llama |
| Embeddings | BAAI/bge-large, OpenAI Embeddings |
| Vector DB | Qdrant / Milvus / Pinecone |
| Graph DB | Neo4j |
| GraphRAG | LangChain GraphRAG |
| Database | PostgreSQL (SQLite local fallback) |
| Cache | Redis |
| Storage | MinIO |
| OCR / Speech | Tesseract / Whisper |
| Auth | JWT + RBAC |
| Workflow | n8n |
| Monitoring / Logging | Prometheus + Grafana / ELK |
| Deployment | Docker + Kubernetes |

- **App UI:** http://localhost:8911
- **API:** http://localhost:8000
- **API docs:** http://localhost:8000/docs

## Demo accounts

| Role | Email | Password |
|------|-------|----------|
| Patient | patient@example.com | Patient@12345 |
| Doctor (Internal Medicine) | doctor@example.com | Doctor@12345 |
| Admin | admin@example.com | Admin@12345 |

Specialty doctors (password `Doctor@12345` for all):

| Specialty | Email |
|------|-------|
| Cardiology | cardio@example.com |
| Gastroenterology | gastro@example.com |
| ENT | ent@example.com |
| Neurology | neuro@example.com |
| Orthopedics | ortho@example.com |
| Dermatology | derma@example.com |
| Pediatrics | pedia@example.com |
| Pulmonology | pulmo@example.com |
| Gynecology | gyn@example.com |
| Ophthalmology | ophtho@example.com |
| Psychiatry | psych@example.com |
| Endocrinology | endo@example.com |
| Urology | uro@example.com |
| Dental | dental@example.com |

## Docker (recommended)

Docker images bake in this `README.md` (at `/app/README.md`) plus backend docs.

### Prerequisites

- Docker Desktop / Docker Engine + Compose v2
- Copy env template: `Copy-Item .env.example .env` (or `cp .env.example .env`)

### Build and run the full stack

From the repository root:

```bash
cp .env.example .env
# set USE_SQLITE=false when using Compose Postgres (already set in compose for backend)
docker compose up --build -d
```

| Service | URL / port |
| --- | --- |
| Frontend | http://localhost:8911 |
| Backend API | http://localhost:8000 |
| Swagger | http://localhost:8000/docs |
| n8n | http://localhost:5678 |
| Neo4j Browser | http://localhost:7474 |
| Qdrant | http://localhost:6333 |
| Grafana | http://localhost:3001 |
| Prometheus | http://localhost:9090 |
| Kibana | http://localhost:5601 |

### Images produced

| Image | Dockerfile | Includes |
| --- | --- | --- |
| `aihc-backend:latest` | `backend/Dockerfile` | FastAPI app, `/app/README.md`, `/app/docs` |
| `aihc-frontend:latest` | `frontend/Dockerfile` | Next.js standalone, `/app/README.md` |

Inspect docs inside a running backend container:

```bash
docker compose exec backend cat /app/README.md
docker compose exec backend cat /app/IMAGE_INFO.txt
```

### Build images only

```bash
docker compose build backend frontend
# or
docker build -f backend/Dockerfile -t aihc-backend:latest .
docker build -f frontend/Dockerfile -t aihc-frontend:latest .
```

### Stop

```bash
docker compose down
# add -v to also remove volumes
```

## Quick start (local, without Docker)

### 1) Backend

```powershell
cd "AI-Healthcare-Assistant-Agentic-AI"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
Copy-Item .env.example .env
Copy-Item .env backend\.env -Force
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 2) Frontend

```powershell
cd frontend
npm install
npm run build
npm run start
# or for hot reload: npm run dev
```

Open **http://localhost:8911**

## API docs

- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI: http://localhost:8000/openapi.json
- Human docs: [`docs/api/API.md`](docs/api/API.md)
- Architecture: [`docs/architecture/architecture.md`](docs/architecture/architecture.md)
- Advanced AI: [`docs/ADVANCED_AI.md`](docs/ADVANCED_AI.md)

## Agentic AI

Master Agent routes via LangGraph intent classification to:

1. Symptom Analysis  
2. Medical Knowledge (RAG + GraphRAG)  
3. Prescription (OCR)  
4. Lab Report (OCR)  
5. Nutrition  
6. Appointment  
7. Insurance  
8. Emergency  
9. Conversation Memory  

Hybrid Vector RAG + GraphRAG, HITL review, voice STT/TTS, multilingual replies, FHIR/HL7 stubs, and evaluation APIs are documented in [`docs/ADVANCED_AI.md`](docs/ADVANCED_AI.md).

## LLM providers

Configure in `.env`:

- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `GOOGLE_API_KEY`

Without keys, a safe offline responder is used so the app still runs locally.

## Tests

```powershell
# from repo root
.\.venv\Scripts\python.exe -m pytest -q
```

## Project layout

```text
AI-Healthcare-Assistant-Agentic-AI/
├── backend/          # FastAPI (uvicorn main:app)
├── frontend/         # Next.js UI on :8911
├── n8n/workflows/    # Automation pipelines
├── docker/           # Extra Docker helpers
├── docs/             # Architecture, API, security, roadmap
├── tests/            # Pytest suite
├── docker-compose.yml
└── README.md
```

See [`docs/STRUCTURE.md`](docs/STRUCTURE.md).

## Installation guide

See [`docs/INSTALLATION.md`](docs/INSTALLATION.md).

## Development roadmap

| Phase | Deliverable |
| ----- | ----------- |
| Phase 1 | FastAPI backend, authentication, patient management |
| Phase 2 | AI chat with RAG over medical knowledge |
| Phase 3 | Multi-agent orchestration using LangGraph/CrewAI |
| Phase 4 | Neo4j-based GraphRAG integration |
| Phase 5 | OCR for prescriptions and lab reports |
| Phase 6 | n8n automation for appointments, reminders, and emergency alerts |
| Phase 7 | Monitoring, testing, Docker, Kubernetes deployment |

Full status: [`docs/ROADMAP.md`](docs/ROADMAP.md).

## License / disclaimer

This project is for educational and prototyping purposes. It must not be used as a sole source of clinical decision-making.
