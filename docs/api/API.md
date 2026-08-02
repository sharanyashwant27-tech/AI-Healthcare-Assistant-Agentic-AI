# API Documentation

Base URL: `http://localhost:8000`  
API prefix: `/api/v1`  
Interactive docs: [Swagger UI](http://localhost:8000/docs) · [ReDoc](http://localhost:8000/redoc)  
Catalog: `GET /api/v1/apis`

## Core APIs

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/login` | No | JWT login |
| POST | `/api/v1/register` | No | User registration |
| POST | `/api/v1/symptom-analysis` | Yes | Symptom triage support |
| POST | `/api/v1/chat` | Yes | Master agent chatbot |
| POST | `/api/v1/appointment` | Yes | Book appointment |
| POST | `/api/v1/prescription` | Yes | Prescription OCR/analysis |
| POST | `/api/v1/lab-report` | Yes | Lab report OCR/analysis |
| POST | `/api/v1/insurance` | Yes | Insurance eligibility assist |
| POST | `/api/v1/reminder` | Yes | Medication reminder |
| GET | `/api/v1/patient` | Yes | List patients |
| GET | `/api/v1/doctor` | Yes | List doctors |
| GET | `/api/v1/dashboard` | Yes | Role-aware dashboard |

## Auth extras

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/refresh` | Refresh access token |
| GET | `/api/v1/me` | Current user profile |

## Additional modules

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/nutrition` | Nutrition plan |
| POST | `/api/v1/emergency` | Emergency detection + alerts |
| POST | `/api/v1/follow-up` | Follow-up scheduling |
| POST | `/api/v1/knowledge` | Medical knowledge (RAG + GraphRAG) |
| GET | `/api/v1/appointment` | List appointments |
| GET | `/api/v1/reminder` | List reminders |
| WS | `/ws/chat` | Chat over WebSocket |
| GET | `/health` | Health checks |

All AI responses include medical disclaimer language and avoid definitive diagnosis.
