# Embeddings

Healthcare content is chunked and embedded into vector collections for RAG retrieval.

## Content types

| Content type | Collection | Description |
|---|---|---|
| Patient History | `patient_records` | History, allergies, conditions, visit summaries |
| Medical Books | `medical_books` | Textbooks and clinical handbooks |
| Clinical Guidelines | `hospital_guidelines` | WHO/CDC, SOPs, protocols |
| Research Papers | `research_papers` | Peer-reviewed evidence |
| Lab Reports | `lab_reports` | Laboratory reports |
| Doctor Notes | `doctor_notes` | Clinician notes |
| Prescriptions | `prescriptions` | Medication lists and instructions |

## Embedding models

| Model | Provider key | Native dims | Notes |
|---|---|---|---|
| OpenAI `text-embedding-3-large` | `openai` | 3072 | Default; can shorten via `EMBEDDING_DIMENSIONS` |
| BGE Large (`BAAI/bge-large-en-v1.5`) | `bge-large` | 1024 | Local / HuggingFace |
| E5 Large (`intfloat/e5-large-v2`) | `e5-large` | 1024 | Local / HuggingFace |

Store vectors are normalized to `EMBEDDING_DIMENSIONS` (default **1024**).

## Configuration

```env
DEFAULT_EMBEDDING_PROVIDER=openai
DEFAULT_EMBEDDING_MODEL=text-embedding-3-large
EMBEDDING_DIMENSIONS=1024
```

Alternatives:

```env
DEFAULT_EMBEDDING_PROVIDER=bge-large
DEFAULT_EMBEDDING_MODEL=BAAI/bge-large-en-v1.5

DEFAULT_EMBEDDING_PROVIDER=e5-large
DEFAULT_EMBEDDING_MODEL=intfloat/e5-large-v2
```

Without an API key / HuggingFace model download, the app uses deterministic local hash embeddings at the configured dimension so RAG still runs offline.

## API

`GET /api/v1/embeddings` — content types, model catalog, and active configuration.

## Code

- `backend/embeddings/content_types.py`
- `backend/embeddings/models.py`
- `backend/embeddings/factory.py`
