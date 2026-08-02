# Prompt Engineering

## System Prompt

```text
You are an AI Healthcare Assistant.

Always answer according to verified medical guidelines.
Never invent medicines.
Never diagnose with certainty.
Recommend consulting a physician whenever uncertainty exists.
Use retrieved context first.
Explain reasoning clearly.
```

Source: `backend/prompts/system.py`

## Prompt Templates

### Symptom Prompt

**Inputs:** Symptoms · Age · Gender · Medical History · Current Medicines · Allergies  

**Returns:** Possible conditions · Risk level · Recommended specialist · Urgency

### Prescription Prompt

**Extract:** Medicine · Dosage · Duration · Drug Interaction · Allergy · Patient Friendly Explanation

Templates live in `backend/prompts/templates.py` (active versions: `symptom` v2, `prescription` v2, `system` v2).

## Prompt Tuning (Few-shot)

Chain:

```text
Symptom → Medical Condition → Doctor Recommendation → Hospital Department
```

Examples: `backend/prompts/few_shot.py`

## Dynamic Prompting

Chain:

```text
Patient Type → Age → Disease → Country → Hospital Protocol
```

Source: `backend/prompts/dynamic.py`

Composition helper: `build_prompt()` in `backend/prompts/builder.py`  
(system + dynamic context + optional few-shot + task template)

## API

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/v1/prompts` | Full catalog |
| `POST` | `/api/v1/prompts/preview` | Render a composed prompt |
