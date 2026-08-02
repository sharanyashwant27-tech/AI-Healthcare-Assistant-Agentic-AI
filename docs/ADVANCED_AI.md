# Advanced AI Features

| Feature | Implementation |
| --- | --- |
| Multi-agent collaboration | `MasterAgent` coordinates specialists; secondary collaborators for symptom/Rx/lab/emergency |
| Hybrid retrieval | `rag/hybrid.py` — Vector RAG + GraphRAG with RRF fusion |
| Conversational memory | Redis/local history injected into prompts (`ConversationMemoryAgent`) |
| Confidence + citations | Hybrid scorer + `[C#]` citation objects on chat/knowledge |
| Human-in-the-loop | `hitl_reviews` queue; doctor/admin approve/reject |
| Explainable AI | Graph path + evidence panel in chat UI / `explanation` payload |
| Voice consultations | `POST /voice/transcribe`, `/voice/consult`, `/voice/tts` (Whisper + gTTS/pyttsx3) |
| Multilingual | `i18n/languages.py` + chat `language` field |
| FHIR/HL7 | `interop/fhir.py` + `/fhir/*` and HL7 ORU parse |
| Continuous evaluation | `eval/framework.py` + `POST /eval/run` |

## Key APIs

| Method | Path |
| --- | --- |
| GET | `/api/v1/advanced-ai` |
| POST | `/api/v1/chat` (confidence, citations, explanation, HITL, language, memory) |
| GET | `/api/v1/hitl/reviews` |
| POST | `/api/v1/hitl/reviews/{id}/decision` |
| POST | `/api/v1/voice/consult` |
| GET | `/api/v1/fhir/metadata` |
| POST | `/api/v1/eval/run` |

## Packages

- `backend/rag/hybrid.py`
- `backend/hitl/`
- `backend/i18n/`
- `backend/interop/`
- `backend/eval/`
- `backend/utils/speech.py`
