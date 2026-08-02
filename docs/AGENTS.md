# AI Agents

## Architecture

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

## 1. Master Agent
- User understanding, task decomposition, orchestration, memory, planning
- LangGraph flow: `understand → plan → execute`
- Delegates to 9 specialists, then returns Final Response
- File: `backend/agents/master.py`

## 2. Symptom Analysis Agent
- Inputs: symptoms, age, gender, medical history
- Outputs: possible conditions, risk score, next action
- File: `backend/agents/symptom_agent.py`

## 3. Medical Knowledge Agent
- RAG + GraphRAG over WHO / CDC / Hospital SOPs
- Disease info, treatment guidelines, drug interactions
- File: `backend/agents/medical_knowledge_agent.py`

## 4. Lab Report Agent
- Blood, urine, CBC, liver, kidney; OCR supported
- Summary, abnormal values, suggestions
- File: `backend/agents/lab_agent.py`

## 5. Prescription Agent
- Extracts medicines, dosage, frequency, duration
- Checks interactions, allergies, duplicates
- File: `backend/agents/prescription_agent.py`

## 6. Appointment Agent
- Books doctor, department, time slot
- Optional HMS webhook via `HMS_WEBHOOK_URL`
- File: `backend/agents/appointment_agent.py`

## 7. Emergency Agent
- Heart attack / stroke / emergency recognition
- Calls n8n workflow, alerts, ambulance request
- File: `backend/agents/emergency_agent.py`

## 8. Nutrition Agent
- Diet plan, calories, water intake, BMI, exercise
- File: `backend/agents/nutrition_agent.py`

## 9. Reminder Agent
- Medication/care reminders and schedules
- File: `backend/agents/reminder_agent.py`
- UI: `/reminders`

## 10. Insurance Agent
- Verifies insurance, claims eligibility, hospital coverage
- File: `backend/agents/insurance_agent.py`

## Supporting
- **Follow-up Agent** (`followup_agent.py`) — follow-up visits/tests/notifications via `POST /follow-up`
- **Memory Agent** — conversation memory under Master (Redis/local)
