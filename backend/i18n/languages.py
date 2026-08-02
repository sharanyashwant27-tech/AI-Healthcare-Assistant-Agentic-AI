"""Multilingual helpers for patients and clinicians."""

from __future__ import annotations

from typing import Dict, Optional

SUPPORTED_LANGUAGES: Dict[str, str] = {
    "en": "English",
    "hi": "Hindi",
    "es": "Spanish",
    "fr": "French",
    "ar": "Arabic",
    "zh": "Chinese",
    "pt": "Portuguese",
    "bn": "Bengali",
    "ta": "Tamil",
    "te": "Telugu",
}


_PHRASES: Dict[str, Dict[str, str]] = {
    "consult_clinician": {
        "en": "Please consult a licensed clinician for medical decisions.",
        "hi": "कृपया चिकित्सा निर्णय के लिए लाइसेंस प्राप्त चिकित्सक से परामर्श करें।",
        "es": "Consulte a un médico autorizado para decisiones médicas.",
        "fr": "Veuillez consulter un clinicien agréé pour les décisions médicales.",
        "ar": "يرجى استشارة طبيب مرخص للقرارات الطبية.",
        "zh": "请咨询持证临床医生以做出医疗决定。",
        "pt": "Consulte um clínico licenciado para decisões médicas.",
        "bn": "চিকিৎসা সিদ্ধান্তের জন্য অনুগ্রহ করে লাইসেন্সপ্রাপ্ত চিকিৎসকের পরামর্শ নিন।",
        "ta": "மருத்துவ முடிவுகளுக்கு உரிமம் பெற்ற மருத்துவரை அணுகவும்.",
        "te": "వైద్య నిర్ణయాల కోసం లైసెన్స్ పొందిన వైద్యుడిని సంప్రదించండి.",
    },
    "not_a_diagnosis": {
        "en": "This is not a diagnosis.",
        "hi": "यह निदान नहीं है।",
        "es": "Esto no es un diagnóstico.",
        "fr": "Ceci n'est pas un diagnostic.",
        "ar": "هذا ليس تشخيصًا.",
        "zh": "这不是诊断。",
        "pt": "Isto não é um diagnóstico.",
        "bn": "এটি কোনো রোগ নির্ণয় নয়।",
        "ta": "இது ஒரு நோய் கண்டறிதல் அல்ல.",
        "te": "ఇది రోగ నిర్ధారణ కాదు.",
    },
}


def normalize_language(code: Optional[str]) -> str:
    if not code:
        return "en"
    code = code.lower().strip().replace("_", "-")
    base = code.split("-")[0]
    return base if base in SUPPORTED_LANGUAGES else "en"


def t(key: str, language: str = "en") -> str:
    lang = normalize_language(language)
    bucket = _PHRASES.get(key) or {}
    return bucket.get(lang) or bucket.get("en") or key


def language_instruction(language: str) -> str:
    lang = normalize_language(language)
    name = SUPPORTED_LANGUAGES.get(lang, "English")
    if lang == "en":
        return "Respond in English."
    return f"Respond in {name} (language code: {lang}). Keep medical safety disclaimers."


async def ensure_language(text: str, language: str) -> str:
    lang = normalize_language(language)
    if lang == "en" or not text:
        return text
    from utils.llm import generate_text

    prompt = (
        f"{language_instruction(lang)}\n"
        "Preserve medical uncertainty and do not add new clinical claims.\n\n"
        f"Text:\n{text}"
    )
    return await generate_text(prompt)
