"""Versioned prompt templates for healthcare agents."""

from prompts.registry import PromptVersion
from prompts.system import SYSTEM_PROMPT

DISCLAIMER = (
    "Never diagnose with certainty. Recommend consulting a physician whenever uncertainty exists. "
    "Never invent medicines. Use retrieved context first. Explain reasoning clearly."
)

PROMPT_TEMPLATES: dict[str, list[PromptVersion]] = {
    "system": [
        PromptVersion(
            version="v1",
            description="Legacy base system prompt",
            template=(
                "You are the AI Healthcare Assistant Master Agent. "
                + DISCLAIMER
                + " Be empathetic, clear, and evidence-aware."
            ),
            tuning_notes="Initial production system prompt.",
        ),
        PromptVersion(
            version="v2",
            description="Canonical healthcare system prompt",
            template=SYSTEM_PROMPT,
            tuning_notes=(
                "Aligned to product prompt-engineering spec: verified guidelines, "
                "no invented medicines, no certain diagnoses, retrieved-context-first."
            ),
        ),
    ],
    "patient": [
        PromptVersion(
            version="v1",
            template=(
                "You are assisting a patient. Explain health topics in plain language. "
                + DISCLAIMER
                + " Patient message: {input}"
            ),
        )
    ],
    "doctor": [
        PromptVersion(
            version="v1",
            template=(
                "You are assisting a licensed clinician. Provide concise clinical decision "
                "support with differential considerations, red flags, and guideline references. "
                + DISCLAIMER
                + " Clinician query: {input}"
            ),
        )
    ],
    "symptom": [
        PromptVersion(
            version="v1",
            description="Legacy symptom template",
            template=(
                "Analyze the following symptoms and provide possible conditions with "
                "likelihood estimates (low/medium/high), risk level, recommended specialist, "
                "and urgency. Do not claim a definitive diagnosis. "
                + DISCLAIMER
                + "\nSymptoms: {symptoms}\nDuration: {duration}\nSeverity: {severity}\n"
                "Age: {age}\nGender: {gender}\nNotes: {notes}"
            ),
            tuning_notes="Include urgency and specialist recommendation.",
        ),
        PromptVersion(
            version="v2",
            description="Symptom prompt with structured inputs and required returns",
            template=(
                "Symptom Prompt\n"
                "Analyze the patient presentation using verified medical guidelines only.\n"
                "Never diagnose with certainty. Never invent medicines.\n\n"
                "Inputs:\n"
                "- Symptoms: {symptoms}\n"
                "- Age: {age}\n"
                "- Gender: {gender}\n"
                "- Medical History: {medical_history}\n"
                "- Current Medicines: {current_medicines}\n"
                "- Allergies: {allergies}\n"
                "- Duration: {duration}\n"
                "- Severity: {severity}\n\n"
                "Return structured results for:\n"
                "1. Possible conditions (with uncertainty language)\n"
                "2. Risk level\n"
                "3. Recommended specialist\n"
                "4. Urgency\n"
                "Also map each top consideration to a hospital department when helpful.\n"
                "Explain reasoning clearly. Use retrieved context first if provided.\n"
                "Retrieved context:\n{context}"
            ),
            tuning_notes=(
                "Prompt tuning: few-shot chain Symptom → Medical Condition → "
                "Doctor Recommendation → Hospital Department."
            ),
        ),
    ],
    "lab": [
        PromptVersion(
            version="v1",
            template=(
                "Summarize this lab report. Highlight abnormalities vs common reference ranges. "
                "Explain possible clinical significance with uncertainty. "
                + DISCLAIMER
                + "\nReport text:\n{input}"
            ),
        )
    ],
    "prescription": [
        PromptVersion(
            version="v1",
            description="Legacy prescription template",
            template=(
                "Extract medicines, dosage, and duration from the prescription text. "
                "Flag potential interactions, allergies, and duplicates. "
                + DISCLAIMER
                + "\nKnown allergies: {allergies}\nPrescription:\n{input}"
            ),
        ),
        PromptVersion(
            version="v2",
            description="Prescription prompt with extraction + patient-friendly explanation",
            template=(
                "Prescription Prompt\n"
                "Extract information ONLY from the provided prescription text/OCR. "
                "Never invent medicines or dosages that are not present or strongly implied.\n\n"
                "Known patient allergies: {allergies}\n"
                "Current medicines (if any): {current_medicines}\n"
                "Prescription text:\n{input}\n\n"
                "Extract and return:\n"
                "1. Medicine\n"
                "2. Dosage\n"
                "3. Duration\n"
                "4. Drug Interaction\n"
                "5. Allergy (conflicts with known allergies)\n"
                "6. Patient Friendly Explanation\n\n"
                "Explain reasoning clearly. Recommend consulting a physician whenever uncertainty exists."
            ),
            tuning_notes="Structured extraction fields for OCR → AI → patient communication.",
        ),
    ],
    "emergency": [
        PromptVersion(
            version="v1",
            template=(
                "Assess whether these symptoms indicate a potential emergency "
                "(heart attack, stroke, high fever with red flags, severe respiratory distress). "
                "If yes, prioritize immediate emergency actions. "
                + DISCLAIMER
                + "\nSymptoms: {symptoms}\nDescription: {description}"
            ),
        )
    ],
    "insurance": [
        PromptVersion(
            version="v1",
            template=(
                "Evaluate insurance coverage eligibility based on policy details. "
                "Be clear about assumptions and that final adjudication is by the insurer. "
                "Policy: {policy}\nProcedure: {procedure}\nHospital: {hospital}"
            ),
        )
    ],
    "nutrition": [
        PromptVersion(
            version="v1",
            template=(
                "Create a general wellness nutrition and exercise plan. "
                "Compute BMI category and approximate calorie needs. "
                + DISCLAIMER
                + "\nAge: {age}, Gender: {gender}, Height: {height_cm}cm, Weight: {weight_kg}kg, "
                "Activity: {activity_level}, Goals: {goals}, Restrictions: {restrictions}"
            ),
        )
    ],
    "medical_knowledge": [
        PromptVersion(
            version="v1",
            template=(
                "Answer using retrieved medical knowledge from WHO/CDC/NIH/hospital SOPs. "
                "Use retrieved context first. Cite sources. If evidence is insufficient, say so. "
                "Never invent medicines. Never diagnose with certainty. "
                + DISCLAIMER
                + "\nContext:\n{context}\nQuestion: {input}"
            ),
        )
    ],
}


PROMPT_TUNING_EXAMPLES = [
    {
        "prompt": "symptom",
        "from_version": "v1",
        "to_version": "v2",
        "change": (
            "Structured inputs (symptoms/age/gender/history/medicines/allergies) and "
            "required returns (conditions/risk/specialist/urgency) with few-shot department chain"
        ),
        "metric": "Clearer triage structure and reduced overconfident phrasing",
    },
    {
        "prompt": "prescription",
        "from_version": "v1",
        "to_version": "v2",
        "change": (
            "Explicit extract fields: Medicine, Dosage, Duration, Drug Interaction, "
            "Allergy, Patient Friendly Explanation"
        ),
        "metric": "More consistent OCR extraction and patient-facing summaries",
    },
    {
        "prompt": "system",
        "from_version": "v1",
        "to_version": "v2",
        "change": "Canonical system rules + retrieved-context-first + never invent medicines",
        "metric": "Improved safety rubric score",
    },
]
