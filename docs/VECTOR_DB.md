# Vector Database

## Recommended providers

1. **Qdrant** (default)
2. **Pinecone**
3. **Milvus**

Configure with:

```env
VECTOR_DB_PROVIDER=qdrant   # qdrant | pinecone | milvus
QDRANT_URL=http://localhost:6333
PINECONE_API_KEY=
MILVUS_HOST=localhost
MILVUS_PORT=19530
```

## Collections

| Collection | Purpose |
| --- | --- |
| `medical_books` | Clinical textbooks and handbooks |
| `research_papers` | Research and evidence summaries |
| `hospital_guidelines` | WHO/CDC guidance and hospital SOPs |
| `patient_records` | Patient history embeddings (privacy-controlled) |
| `drug_database` | Drug monographs and interactions |
| `insurance_rules` | Coverage rules and claim eligibility |
| `lab_reports` | Laboratory report embeddings |
| `doctor_notes` | Clinician notes embeddings |
| `prescriptions` | Prescription document embeddings |

See also [EMBEDDINGS.md](./EMBEDDINGS.md) for content-type → collection mapping and models.

## API

`GET /api/v1/vector-db` — provider status + collection catalog

## Code

- Collections: `backend/vectordb/collections.py`
- Factory: `backend/vectordb/factory.py`
- Qdrant: `backend/vectordb/qdrant_client.py`
