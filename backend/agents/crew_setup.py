"""CrewAI multi-agent crew definition with graceful fallback."""

from typing import Any, Dict

from core.logging import get_logger

logger = get_logger(__name__)


def build_healthcare_crew() -> Any:
    try:
        from crewai import Agent, Crew, Process, Task

        symptom_analyst = Agent(
            role="Symptom Analyst",
            goal="Analyze symptoms with uncertainty-aware recommendations",
            backstory="Clinical triage specialist AI that never overstates certainty.",
            verbose=False,
            allow_delegation=False,
        )
        knowledge_curator = Agent(
            role="Medical Knowledge Curator",
            goal="Retrieve WHO/CDC/SOP grounded answers",
            backstory="Evidence librarian for medical guidelines and research.",
            verbose=False,
            allow_delegation=False,
        )
        safety_officer = Agent(
            role="Emergency Safety Officer",
            goal="Detect emergencies and escalate",
            backstory="Safety-first agent monitoring red-flag presentations.",
            verbose=False,
            allow_delegation=False,
        )

        task = Task(
            description=(
                "Collaborate to answer the patient query safely with sources and uncertainty."
            ),
            expected_output="Safe healthcare guidance with disclaimer",
            agents=[symptom_analyst, knowledge_curator, safety_officer],
        )
        crew = Crew(
            agents=[symptom_analyst, knowledge_curator, safety_officer],
            tasks=[task],
            process=Process.sequential,
            verbose=False,
        )
        return crew
    except Exception as exc:  # noqa: BLE001
        logger.warning("crewai_unavailable", error=str(exc))
        return None


async def run_crew_fallback(query: str) -> Dict[str, Any]:
    return {
        "crew": "fallback",
        "reply": (
            f"Crew orchestration fallback for: {query}. "
            "Specialist agents would analyze symptoms, retrieve guidelines, and check emergencies."
        ),
    }
