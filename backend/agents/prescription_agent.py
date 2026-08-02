"""Prescription Agent — OCR extraction + interaction/allergy/duplicate checks."""

import json
import re
from pathlib import Path
from typing import Any, Dict, List

from agents.base import BaseAgent
from core.config import settings
from prompts.builder import build_prompt
from utils.llm import generate_text
from utils.speech import ocr_image


class PrescriptionAgent(BaseAgent):
    name = "prescription"

    KNOWN_DRUGS = {
        "paracetamol": {"class": "analgesic", "interactions": ["warfarin"]},
        "ibuprofen": {"class": "nsaid", "interactions": ["warfarin", "aspirin"]},
        "amoxicillin": {"class": "antibiotic", "interactions": ["methotrexate"]},
        "metformin": {"class": "antidiabetic", "interactions": ["alcohol"]},
        "atorvastatin": {"class": "statin", "interactions": ["clarithromycin"]},
        "aspirin": {"class": "antiplatelet", "interactions": ["ibuprofen", "warfarin"]},
        "warfarin": {"class": "anticoagulant", "interactions": ["aspirin", "ibuprofen", "paracetamol"]},
    }

    def ocr_image(self, file_path: str) -> str:
        text = ocr_image(file_path)
        if text:
            return text
        txt = Path(file_path).with_suffix(".txt")
        return txt.read_text(encoding="utf-8") if txt.exists() else ""

    def extract_medicines(self, text: str) -> List[Dict[str, str]]:
        found = []
        lower = text.lower()
        freq_map = [
            (r"\b(od|once daily|daily)\b", "once daily"),
            (r"\b(bd|twice daily|bid)\b", "twice daily"),
            (r"\b(tid|thrice|three times)\b", "three times daily"),
            (r"\b(qid|four times)\b", "four times daily"),
            (r"\b(sos|as needed|prn)\b", "as needed"),
        ]
        duration_match = re.search(r"for\s+(\d+\s*(?:day|days|week|weeks|month|months))", lower)
        default_duration = duration_match.group(1) if duration_match else "as prescribed"
        default_freq = "as prescribed"
        for pat, label in freq_map:
            if re.search(pat, lower):
                default_freq = label
                break

        for drug in self.KNOWN_DRUGS:
            if drug in lower:
                dosage_match = re.search(rf"{drug}\s*(\d+\s?mg)?", lower)
                found.append(
                    {
                        "name": drug.title(),
                        "dosage": (
                            dosage_match.group(1)
                            if dosage_match and dosage_match.group(1)
                            else "as prescribed"
                        ),
                        "frequency": default_freq,
                        "duration": default_duration,
                    }
                )
        if not found:
            for line in text.splitlines():
                if any(x in line.lower() for x in ["mg", "tab", "capsule", "syrup"]):
                    found.append(
                        {
                            "name": line.strip()[:80],
                            "dosage": "see text",
                            "frequency": default_freq,
                            "duration": default_duration,
                        }
                    )
        return found

    def detect_issues(self, medicines: List[Dict[str, str]], allergies: str) -> Dict[str, Any]:
        names = [m["name"].lower() for m in medicines]
        interactions = []
        for m in names:
            key = m.split()[0]
            for other in self.KNOWN_DRUGS.get(key, {}).get("interactions", []):
                if any(other in n for n in names):
                    interactions.append(f"{key} may interact with {other}")
        allergy_hits = []
        allergy_l = (allergies or "").lower()
        for n in names:
            if n.split()[0] in allergy_l or ("penicillin" in allergy_l and "amoxicillin" in n):
                allergy_hits.append(n)
        duplicates = list({n for n in names if names.count(n) > 1})
        return {
            "drug_interactions": interactions,
            "interactions": interactions,
            "allergy_alerts": allergy_hits,
            "duplicates": duplicates,
        }

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        text = payload.get("text") or ""
        file_path = payload.get("file_path")
        if file_path and not text:
            text = self.ocr_image(file_path)
        allergies = payload.get("allergies") or ""
        current_medicines = payload.get("current_medicines") or ""
        medicines = self.extract_medicines(text)
        issues = self.detect_issues(medicines, allergies)
        prompt = build_prompt(
            "prescription",
            {
                "allergies": allergies or "none reported",
                "current_medicines": current_medicines or "none reported",
                "input": text or json.dumps(medicines),
            },
            dynamic_payload={
                "patient_type": payload.get("patient_type") or "patient",
                "age": payload.get("age"),
                "disease": payload.get("disease"),
                "country": payload.get("country"),
                "hospital_protocol": payload.get("hospital_protocol"),
            },
        )
        analysis = await generate_text(prompt)
        return {
            "agent": self.name,
            "medicines": medicines,
            "dosage": ", ".join(m.get("dosage", "") for m in medicines),
            "frequency": ", ".join(m.get("frequency", "") for m in medicines),
            "duration": ", ".join(m.get("duration", "") for m in medicines),
            "issues": issues,
            "drug_interaction": issues.get("drug_interactions") or issues.get("interactions"),
            "allergy": issues.get("allergy_alerts"),
            "patient_friendly_explanation": analysis,
            "analysis": analysis,
            "reply": analysis,
            "disclaimer": settings.medical_disclaimer,
        }
