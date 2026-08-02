# GraphRAG

## Knowledge Graph (Neo4j)

```text
Patient
 │
 ├── Disease
 ├── Symptoms
 ├── Medicine
 ├── Allergy
 ├── Doctor
 ├── Hospital
 ├── Lab Test
 ├── Insurance
 └── Appointment
```

## Example path

```text
John
 ↓
Diabetes
 ↓
Metformin
 ↓
Kidney Disease
 ↓
Creatinine Test
 ↓
Doctor
 ↓
Hospital
```

## Graph Database

**Neo4j** (with in-memory fallback for local development)

## Benefits

- Relationship reasoning
- Explainability
- Better retrieval (with vector RAG)
- Faster recommendations

## Relationships

`HAS_DISEASE` · `HAS_SYMPTOM` · `TAKES_MEDICINE` · `ALLERGIC_TO` · `TREATED_BY` · `VISITS` · `HAS_LAB_TEST` · `COVERED_BY` · `BOOKED` · `PRESCRIBED` · `REFERRED_TO` · `ASSOCIATED_WITH` · `MONITORED_BY` · `INDICATED_FOR`

## APIs

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/v1/graphrag` | Schema + benefits |
| GET | `/api/v1/graphrag/example` | John diabetes explainable path |
| GET | `/api/v1/graphrag/patient/{key}` | Patient neighborhood |
| POST | `/api/v1/graphrag/query` | GraphRAG answer |

## Code

- Schema: `backend/graphrag/schema.py`
- Neo4j client: `backend/graphrag/neo4j_client.py`
- LangChain GraphRAG: `backend/graphrag/langchain_graphrag.py`
