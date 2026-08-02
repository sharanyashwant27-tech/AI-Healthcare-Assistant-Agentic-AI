# RAG Pipeline

```text
Medical documents
        ↓
PDF Loader (also Text / Word / CSV)
        ↓
Chunking
        ↓
Embeddings
        ↓
Vector Database (Qdrant / Pinecone / Milvus)
        ↓
Retriever
        ↓
LLM
        ↓
Answer
```

## Vector collections

`medical_books` · `research_papers` · `hospital_guidelines` · `patient_records` · `drug_database` · `insurance_rules` · `lab_reports` · `doctor_notes` · `prescriptions`

See also: [`VECTOR_DB.md`](VECTOR_DB.md) · [`EMBEDDINGS.md`](EMBEDDINGS.md)

## Knowledge Sources

| Source | Collection | Key |
| --- | --- | --- |
| WHO Guidelines | `hospital_guidelines` | `who` |
| CDC Guidelines | `hospital_guidelines` | `cdc` |
| Hospital SOP | `hospital_guidelines` | `sop` |
| Drug Database | `drug_database` | `drug` |
| Medical Books | `medical_books` | `books` |
| Research Papers | `research_papers` | `research` |
| Hospital Policies | `hospital_guidelines` | `policies` |
| Insurance Rules | `insurance_rules` | `insurance` |
| Patient History | `patient_records` | `patient` |
| Lab Reports | `lab_reports` | `labs` |
| Doctor Notes | `doctor_notes` | `notes` |
| Prescriptions | `prescriptions` | `rx` |

## APIs

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/v1/rag` | Describe pipeline + sources |
| POST | `/api/v1/rag/query` | Retrieve + generate answer |
| POST | `/api/v1/rag/ingest` | Upload document into a source |
| POST | `/api/v1/rag/seed` | Seed sample corpus for all sources |
| GET | `/api/v1/vector-db` | Vector DB provider + collections |

## Code

- Pipeline: `backend/rag/pipeline.py`
- Sources: `backend/rag/knowledge_sources.py`
- Vector DB: `backend/vectordb/`
