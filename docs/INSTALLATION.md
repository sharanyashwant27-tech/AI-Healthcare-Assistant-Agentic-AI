# Installation Guide

## Prerequisites

- Python 3.12+
- Node.js 20+
- Docker Desktop (optional, for full infra)
- Git

## Local development (recommended first run)

1. Clone/open the project folder.
2. Copy `.env.example` to `.env` and set `SECRET_KEY`.
3. Keep `USE_SQLITE=true` for zero-dependency local DB.
4. Create venv and install `backend/requirements-core.txt`.
5. Start FastAPI on port **8000**.
6. Install frontend deps and start Next.js on port **8911**.
7. Login with `patient@example.com` / `Patient@12345`.

## Production-like stack

1. Set API keys and strong `SECRET_KEY`.
2. Set `USE_SQLITE=false` and start `docker compose up --build`.
3. Apply Alembic migrations against Postgres if desired:
   ```powershell
   cd backend
   alembic revision --autogenerate -m "init"
   alembic upgrade head
   ```
4. Import n8n workflows from `n8n/workflows` (see [`docs/N8N.md`](N8N.md) for the five pipelines).
5. Open Grafana at `:3001` (admin/admin) and Kibana at `:5601`.

## Kubernetes

```powershell
kubectl apply -f infra/kubernetes/namespace.yaml
kubectl apply -f infra/kubernetes/
helm upgrade --install ai-healthcare infra/helm/ai-healthcare -n ai-healthcare
```

## Optional heavy AI extras

```powershell
pip install -r backend\requirements.txt
```

Includes Whisper, sentence-transformers, CrewAI extras, OCR tooling dependencies.
