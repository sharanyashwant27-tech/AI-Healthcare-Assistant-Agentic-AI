"""Lab Report Agent — blood, urine, CBC, liver, kidney with OCR."""

import re
from pathlib import Path
from typing import Any, Dict, List

from agents.base import BaseAgent
from core.config import settings
from prompts.registry import get_prompt_registry
from utils.llm import generate_text
from utils.speech import ocr_image

REFERENCE_RANGES = {
    "hemoglobin": (12.0, 17.5),
    "wbc": (4000, 11000),
    "platelets": (150000, 450000),
    "glucose": (70, 99),
    "creatinine": (0.6, 1.3),
    "alt": (7, 56),
    "ast": (10, 40),
    "urea": (7, 20),
    "bilirubin": (0.1, 1.2),
    "urine_protein": (0.0, 0.0),  # ideally negative/trace
}


class LabReportAgent(BaseAgent):
    name = "lab_report"

    def __init__(self) -> None:
        self.prompts = get_prompt_registry()

    def ocr(self, file_path: str) -> str:
        text = ocr_image(file_path)
        if text:
            return text
        txt = Path(file_path).with_suffix(".txt")
        return txt.read_text(encoding="utf-8") if txt.exists() else ""

    def parse_values(self, text: str) -> Dict[str, float]:
        values: Dict[str, float] = {}
        patterns = {
            "hemoglobin": r"hemoglobin[:\s]+(\d+\.?\d*)",
            "wbc": r"wbc[:\s]+(\d+\.?\d*)",
            "platelets": r"platelet[s]?[:\s]+(\d+\.?\d*)",
            "glucose": r"(?:glucose|blood sugar)[:\s]+(\d+\.?\d*)",
            "creatinine": r"creatinine[:\s]+(\d+\.?\d*)",
            "alt": r"alt[:\s]+(\d+\.?\d*)",
            "ast": r"ast[:\s]+(\d+\.?\d*)",
            "urea": r"(?:urea|bun)[:\s]+(\d+\.?\d*)",
            "bilirubin": r"bilirubin[:\s]+(\d+\.?\d*)",
            "urine_protein": r"urine\s*protein[:\s]+(\d+\.?\d*)",
        }
        lower = text.lower()
        for key, pat in patterns.items():
            m = re.search(pat, lower)
            if m:
                values[key] = float(m.group(1))
        return values

    def highlight(self, values: Dict[str, float]) -> List[str]:
        flags = []
        for k, v in values.items():
            low, high = REFERENCE_RANGES[k]
            if k == "urine_protein":
                if v > 0:
                    flags.append(f"{k} elevated ({v}) — correlate clinically")
                continue
            if v < low:
                flags.append(f"{k} low ({v} < {low})")
            elif v > high:
                flags.append(f"{k} high ({v} > {high})")
        return flags

    def detect_report_type(self, text: str, values: Dict[str, float]) -> str:
        lower = text.lower()
        types = []
        if "urine" in lower or "urine_protein" in values:
            types.append("Urine")
        if any(k in values for k in ("hemoglobin", "wbc", "platelets")) or "cbc" in lower:
            types.append("CBC")
        if any(k in values for k in ("alt", "ast", "bilirubin")) or "liver" in lower:
            types.append("Liver")
        if any(k in values for k in ("creatinine", "urea")) or "kidney" in lower:
            types.append("Kidney")
        if "glucose" in values or "blood sugar" in lower:
            types.append("Blood Sugar")
        return "+".join(types) if types else "Blood/General"

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        text = payload.get("text") or ""
        if payload.get("file_path") and not text:
            text = self.ocr(payload["file_path"])
        values = self.parse_values(text)
        abnormalities = self.highlight(values)
        prompt = self.prompts.as_langchain("lab").format(input=text or str(values))
        summary = await generate_text(prompt)
        suggestions = [
            "Review results with a licensed clinician in clinical context",
            "Repeat abnormal tests if recommended by your care team",
        ]
        if abnormalities:
            suggestions.append("Prioritize discussion of flagged abnormal values")

        report_type = self.detect_report_type(text, values)
        return {
            "agent": self.name,
            "report_type": report_type,
            "results": values,
            "abnormal_values": abnormalities,
            "abnormalities": abnormalities,
            "summary": summary,
            "suggestions": suggestions,
            "reply": summary,
            "disclaimer": settings.medical_disclaimer,
        }
