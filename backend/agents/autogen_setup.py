"""AutoGen multi-agent collaboration with graceful fallback."""

from typing import Any, Dict

from core.logging import get_logger

logger = get_logger(__name__)


def build_autogen_team() -> Any:
    try:
        import autogen

        llm_config = {"config_list": [{"model": "gpt-4o-mini", "api_key": "unused"}], "temperature": 0.2}
        symptom = autogen.AssistantAgent(
            name="SymptomAnalyst",
            system_message=(
                "Analyze symptoms with uncertainty. Never diagnose with certainty. "
                "Recommend licensed clinical care."
            ),
            llm_config=llm_config,
        )
        knowledge = autogen.AssistantAgent(
            name="KnowledgeCurator",
            system_message="Retrieve and cite WHO/CDC/SOP grounded medical knowledge.",
            llm_config=llm_config,
        )
        safety = autogen.AssistantAgent(
            name="SafetyOfficer",
            system_message="Detect emergencies and escalate immediately when red flags appear.",
            llm_config=llm_config,
        )
        user_proxy = autogen.UserProxyAgent(
            name="Coordinator",
            human_input_mode="NEVER",
            code_execution_config=False,
        )
        return {"user_proxy": user_proxy, "agents": [symptom, knowledge, safety]}
    except Exception as exc:  # noqa: BLE001
        logger.warning("autogen_unavailable", error=str(exc))
        return None


async def run_autogen_fallback(query: str) -> Dict[str, Any]:
    return {
        "framework": "autogen-fallback",
        "reply": (
            f"AutoGen collaboration fallback for: {query}. "
            "Symptom, knowledge, and safety agents would collaborate under clinical safety rules."
        ),
    }
