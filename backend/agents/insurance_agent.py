"""Insurance Agent — policy verification, claims, hospital coverage."""

from typing import Any, Dict

from agents.base import BaseAgent
from core.config import settings
from prompts.registry import get_prompt_registry
from utils.llm import generate_text


class InsuranceAgent(BaseAgent):
    name = "insurance"

    NETWORK = {
        "city general hospital": True,
        "metro care clinic": True,
        "riverside specialty center": False,
    }

    def __init__(self) -> None:
        self.prompts = get_prompt_registry()

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        policy = payload.get("policy_number") or "UNKNOWN"
        provider = payload.get("provider_name") or "HealthPlus"
        procedure = payload.get("procedure") or payload.get("claim_type") or "general consultation"
        hospital = (payload.get("hospital_name") or "City General Hospital").lower()
        in_network = self.NETWORK.get(hospital, False)
        is_valid = bool(policy) and policy != "UNKNOWN"
        claim_eligible = is_valid and in_network
        prompt = self.prompts.as_langchain("insurance").format(
            policy=f"{provider} #{policy}",
            procedure=procedure,
            hospital=hospital,
        )
        summary = await generate_text(prompt)
        return {
            "agent": self.name,
            "is_valid": is_valid,
            "insurance_verified": is_valid,
            "coverage_summary": summary,
            "claim_eligible": claim_eligible,
            "claims": {
                "eligible": claim_eligible,
                "procedure": procedure,
                "notes": "Final claim adjudication is by the insurer.",
            },
            "hospital_coverage": {
                "hospital": hospital,
                "network_status": "in_network" if in_network else "out_of_network",
                "covered": in_network and is_valid,
            },
            "network_status": "in_network" if in_network else "out_of_network",
            "details": {
                "provider": provider,
                "policy_number": policy,
                "procedure": procedure,
                "hospital": hospital,
            },
            "reply": summary,
            "disclaimer": settings.medical_disclaimer,
        }
