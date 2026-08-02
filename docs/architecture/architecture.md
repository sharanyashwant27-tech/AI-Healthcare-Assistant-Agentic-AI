# Architecture

## Agent Architecture

```text
                    User
                      │
              Master AI Agent
      ┌─────────┼──────────┐
 Symptom   Medical   Prescription
 Lab        Nutrition  Appointment
 Insurance  Emergency  Reminder
                      │
              Final Response
```

```mermaid
flowchart TB
  U[User] --> M[Master AI Agent]
  M --> S[Symptom]
  M --> MK[Medical]
  M --> RX[Prescription]
  M --> L[Lab]
  M --> N[Nutrition]
  M --> A[Appointment]
  M --> I[Insurance]
  M --> E[Emergency]
  M --> R[Reminder]
  S --> F[Final Response]
  MK --> F
  RX --> F
  L --> F
  N --> F
  A --> F
  I --> F
  E --> F
  R --> F
```

## System Architecture

```mermaid
flowchart TB
  subgraph Client
    UI[Next.js Frontend :8911]
  end

  subgraph API
    GW[FastAPI API :8000]
    WS[WebSocket Chat]
    AUTH[JWT + RBAC]
  end

  subgraph Agents
    MASTER[Master Agent]
    LG[LangGraph understand → plan → execute]
    SA[Symptom]
    MK[Medical Knowledge]
    RX[Prescription]
    LAB[Lab]
    NUT[Nutrition]
    APT[Appointment]
    INS[Insurance]
    EMG[Emergency]
    REM[Reminder]
    MEM[Memory]
  end

  subgraph Data
    PG[(PostgreSQL / SQLite)]
    RD[(Redis)]
    N4[(Neo4j GraphRAG)]
    QD[(Qdrant VectorDB)]
  end

  subgraph Ops
    PROM[Prometheus]
    GRAF[Grafana]
    ELK[ELK]
    N8N[n8n Workflows]
  end

  UI --> GW
  UI --> WS
  GW --> AUTH
  GW --> MASTER
  MASTER --> LG
  LG --> SA & MK & RX & LAB & NUT & APT & INS & EMG & REM
  MASTER --> MEM
  MK --> QD
  MK --> N4
  MEM --> RD
  GW --> PG
  GW --> PROM
  GW --> ELK
  N8N --> GW
```

## Sequence: Chat

```mermaid
sequenceDiagram
  participant U as User
  participant FE as Frontend
  participant API as FastAPI
  participant M as Master Agent
  participant E as Emergency Agent
  participant S as Specialist Agent
  participant MEM as Memory Agent

  U->>FE: Send message
  FE->>API: POST /api/v1/chat (JWT)
  API->>M: chat(message)
  M->>MEM: store user message
  M->>E: emergency screen
  alt emergency
    E-->>M: critical actions
  else normal
    M->>S: route by intent
    S-->>M: reply + sources
  end
  M->>MEM: store assistant reply
  M-->>API: ChatResponse + disclaimer
  API-->>FE: JSON
  FE-->>U: Render answer
```

## ER Diagram

```mermaid
erDiagram
  USERS ||--o{ USER_ROLES : has
  ROLES ||--o{ USER_ROLES : grants
  USERS ||--o| PATIENTS : profile
  USERS ||--o| DOCTORS : profile
  PATIENTS ||--o{ APPOINTMENTS : books
  DOCTORS ||--o{ APPOINTMENTS : hosts
  PATIENTS ||--o{ PRESCRIPTIONS : has
  PATIENTS ||--o{ REPORTS : has
  PATIENTS ||--o{ INSURANCE : holds
  PATIENTS ||--o{ MEDICAL_HISTORY : records
  USERS ||--o{ NOTIFICATIONS : receives
  USERS ||--o{ AUDIT_LOG : generates
```
