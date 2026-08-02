"""Prompt tuning — few-shot examples for symptom triage chains."""

from typing import Any, Dict, List

# Symptom → Medical Condition → Doctor Recommendation → Hospital Department
FEW_SHOT_SYMPTOM_EXAMPLES: List[Dict[str, str]] = [
    {
        "symptom": "Chest pain radiating to left arm with sweating",
        "medical_condition": "Possible acute coronary syndrome (uncertain — emergency evaluation required)",
        "doctor_recommendation": "Seek emergency care immediately; do not wait for outpatient review",
        "hospital_department": "Emergency Medicine / Cardiology",
    },
    {
        "symptom": "Fever, cough, and sore throat for 2 days",
        "medical_condition": "Possible viral upper respiratory infection (common consideration, not a diagnosis)",
        "doctor_recommendation": "Consult a general physician if symptoms worsen or persist beyond a few days",
        "hospital_department": "General Medicine / Internal Medicine / Primary Care",
    },
    {
        "symptom": "Sudden facial droop and slurred speech",
        "medical_condition": "Possible stroke (time-critical — not confirmed without clinical assessment)",
        "doctor_recommendation": "Call emergency services immediately (act FAST)",
        "hospital_department": "Emergency Medicine / Neurology / Stroke Unit",
    },
    {
        "symptom": "Burning urination with lower abdominal discomfort",
        "medical_condition": "Possible urinary tract infection (consideration only)",
        "doctor_recommendation": "See a physician or urologist for evaluation and urine testing",
        "hospital_department": "General Medicine / Urology",
    },
    {
        "symptom": "Wheezing and shortness of breath in a known asthmatic",
        "medical_condition": "Possible asthma exacerbation (severity-dependent)",
        "doctor_recommendation": "Use prescribed rescue plan if available; seek urgent care if breathing worsens",
        "hospital_department": "Pulmonology / Emergency Medicine (if severe)",
    },
]


def format_few_shot_block(examples: List[Dict[str, str]] | None = None) -> str:
    examples = examples or FEW_SHOT_SYMPTOM_EXAMPLES
    lines = [
        "Few-shot tuning examples (pattern: Symptom → Medical Condition → Doctor Recommendation → Hospital Department):",
        "",
    ]
    for i, ex in enumerate(examples, 1):
        lines.extend(
            [
                f"Example {i}:",
                f"  Symptom: {ex['symptom']}",
                f"  Medical Condition: {ex['medical_condition']}",
                f"  Doctor Recommendation: {ex['doctor_recommendation']}",
                f"  Hospital Department: {ex['hospital_department']}",
                "",
            ]
        )
    lines.append("Follow the same chain and never state a condition as certain.")
    return "\n".join(lines)


def few_shot_catalog() -> List[Dict[str, Any]]:
    return [
        {
            "chain": [
                "Symptom",
                "Medical Condition",
                "Doctor Recommendation",
                "Hospital Department",
            ],
            "examples": FEW_SHOT_SYMPTOM_EXAMPLES,
        }
    ]
