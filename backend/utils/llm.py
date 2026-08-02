"""Multi-provider LLM factory: GPT / Claude / Gemini / Llama with offline fallback."""

from typing import Any, Optional

from core.config import settings
from core.logging import get_logger

logger = get_logger(__name__)


class OfflineLLM:
    """Rule-based offline responder used when no LLM API keys are configured."""

    def invoke(self, prompt: str, **_: Any) -> str:
        text = prompt.lower()
        if any(k in text for k in ["chest pain", "stroke", "can't breathe", "cannot breathe"]):
            return (
                "Potential emergency indicators detected. Call emergency services immediately. "
                "This is not a diagnosis. Seek urgent in-person care now."
            )
        if "symptom" in text:
            return (
                "Based on the described symptoms, possible considerations may include common "
                "viral illness, allergy-related irritation, or stress-related tension. "
                "Confidence is low without clinical examination. Please consult a licensed clinician."
            )
        if "lab" in text or "cbc" in text:
            return (
                "Lab values should be interpreted by a clinician in clinical context. "
                "I can highlight out-of-range markers, but this is not a diagnosis."
            )
        if "insurance" in text:
            return (
                "Insurance validation requires policy and network checks. "
                "Treat this as a preliminary eligibility estimate only."
            )
        return (
            "I can help with general health information, appointments, and document understanding. "
            "I do not provide definitive medical diagnoses. Please consult a licensed healthcare professional."
        )

    async def ainvoke(self, prompt: str, **kwargs: Any) -> str:
        return self.invoke(prompt, **kwargs)


def get_llm(provider: Optional[str] = None, model: Optional[str] = None):
    provider = (provider or settings.default_llm_provider).lower()
    model = model or settings.default_llm_model

    try:
        if provider == "openai" and settings.openai_api_key:
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(model=model, api_key=settings.openai_api_key, temperature=0.2)

        if provider in {"anthropic", "claude"} and settings.anthropic_api_key:
            from langchain_anthropic import ChatAnthropic

            return ChatAnthropic(
                model=model if "claude" in model else "claude-3-5-sonnet-latest",
                api_key=settings.anthropic_api_key,
                temperature=0.2,
            )

        if provider in {"google", "gemini"} and settings.google_api_key:
            from langchain_google_genai import ChatGoogleGenerativeAI

            return ChatGoogleGenerativeAI(
                model=model if "gemini" in model else "gemini-1.5-flash",
                google_api_key=settings.google_api_key,
                temperature=0.2,
            )

        if provider in {"llama", "ollama"}:
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(
                model=model if model not in {"gpt-4o-mini", "gpt-4o"} else "llama3.2",
                api_key=settings.llama_api_key or "ollama",
                base_url=settings.llama_base_url,
                temperature=0.2,
            )
    except Exception as exc:  # noqa: BLE001
        logger.warning("llm_init_failed", provider=provider, error=str(exc))

    logger.info("using_offline_llm")
    return OfflineLLM()


async def generate_text(prompt: str, provider: Optional[str] = None) -> str:
    text = prompt
    if getattr(settings, "phi_masking_enabled", True):
        from security.phi import mask_phi

        text = mask_phi(prompt)
    llm = get_llm(provider)
    result = await llm.ainvoke(text) if hasattr(llm, "ainvoke") else llm.invoke(text)
    if hasattr(result, "content"):
        return str(result.content)
    return str(result)
