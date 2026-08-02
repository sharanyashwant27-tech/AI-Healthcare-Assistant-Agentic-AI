"""Master AI Agent — multi-agent collaboration, memory, hybrid evidence, HITL gates."""

from typing import Any, Dict, List, Optional
from uuid import uuid4

from agents.appointment_agent import AppointmentAgent
from agents.autogen_setup import build_autogen_team, run_autogen_fallback
from agents.crew_setup import build_healthcare_crew, run_crew_fallback
from agents.emergency_agent import EmergencyAgent
from agents.followup_agent import FollowUpAgent
from agents.insurance_agent import InsuranceAgent
from agents.lab_agent import LabReportAgent
from agents.langgraph_workflow import build_langgraph_app, build_plan, classify_intent
from agents.medical_knowledge_agent import MedicalKnowledgeAgent
from agents.memory_agent import ConversationMemoryAgent
from agents.nutrition_agent import NutritionAgent
from agents.prescription_agent import PrescriptionAgent
from agents.reminder_agent import ReminderAgent
from agents.symptom_agent import SymptomAnalysisAgent
from core.config import settings
from core.logging import get_logger
from hitl.service import requires_human_review
from i18n.languages import ensure_language, normalize_language, t

logger = get_logger(__name__)


class MasterAgent:
    """
    User → Master AI Agent → specialist collaboration → Final Response
    (optional Human-in-the-loop for high-risk recommendations)
    """

    SPECIALISTS = (
        "symptom",
        "knowledge",
        "prescription",
        "lab",
        "nutrition",
        "appointment",
        "insurance",
        "emergency",
        "reminder",
    )

    # Intents that benefit from a secondary collaborator
    COLLABORATIONS = {
        "symptom": ["knowledge"],
        "knowledge": [],
        "emergency": ["knowledge"],
        "prescription": ["knowledge"],
        "lab": ["knowledge"],
    }

    def __init__(self) -> None:
        self.symptom = SymptomAnalysisAgent()
        self.knowledge = MedicalKnowledgeAgent()
        self.prescription = PrescriptionAgent()
        self.lab = LabReportAgent()
        self.nutrition = NutritionAgent()
        self.appointment = AppointmentAgent()
        self.insurance = InsuranceAgent()
        self.emergency = EmergencyAgent()
        self.reminder = ReminderAgent()
        self.followup = FollowUpAgent()
        self.memory = ConversationMemoryAgent()
        self.crew = build_healthcare_crew()
        self.autogen = build_autogen_team()
        self.graph = build_langgraph_app(self._execute_intent)

    def _agent_map(self) -> Dict[str, Any]:
        return {
            "symptom": self.symptom,
            "knowledge": self.knowledge,
            "medical": self.knowledge,
            "prescription": self.prescription,
            "lab": self.lab,
            "nutrition": self.nutrition,
            "appointment": self.appointment,
            "insurance": self.insurance,
            "emergency": self.emergency,
            "reminder": self.reminder,
            "followup": self.followup,
            "memory": self.memory,
        }

    async def understand(self, message: str) -> Dict[str, Any]:
        intent = classify_intent(message)
        plan = build_plan(intent, message)
        return {"intent": intent, "plan": plan}

    def _history_snippet(self, history: List[Dict[str, Any]], limit: int = 6) -> str:
        lines = []
        for item in history[-limit:]:
            role = item.get("role", "?")
            content = (item.get("content") or "")[:240]
            lines.append(f"{role}: {content}")
        return "\n".join(lines)

    async def _execute_intent(self, state: Dict[str, Any]) -> Dict[str, Any]:
        intent = state.get("intent") or classify_intent(state.get("message", ""))
        plan: List[str] = state.get("plan") or build_plan(intent, state.get("message", ""))
        payload = {**(state.get("payload") or {}), "message": state.get("message", "")}
        collaborators_run: List[str] = []

        # Always run emergency screen first for chat-like messages
        if intent != "emergency":
            emergency_check = await self.emergency.run(payload)
            if emergency_check.get("is_emergency"):
                return {
                    "agent": "emergency",
                    "intent": "emergency",
                    "plan": plan,
                    "reply": emergency_check.get("reply"),
                    "risk_level": "critical",
                    "results": emergency_check,
                    "sources": [],
                    "citations": [],
                    "confidence": {"score": 0.9, "label": "high", "rationale": "Emergency pattern match"},
                    "explanation": {
                        "method": "EmergencyAgent red-flag screen",
                        "evidence_used": emergency_check.get("emergency_flags")
                        or emergency_check.get("immediate_actions")
                        or [],
                    },
                    "collaborators": ["emergency"],
                }

        agent = self._agent_map().get(intent, self.knowledge)
        result = await agent.run(payload)
        collaborators_run.append(result.get("agent", intent))

        # Multi-agent collaboration: secondary knowledge pass for selected intents
        for collab in self.COLLABORATIONS.get(intent, []):
            if collab == intent:
                continue
            secondary = self._agent_map().get(collab)
            if not secondary:
                continue
            collab_payload = {
                **payload,
                "message": payload.get("message", ""),
                "query": payload.get("message", ""),
            }
            secondary_result = await secondary.run(collab_payload)
            collaborators_run.append(secondary_result.get("agent", collab))
            # Merge evidence
            if secondary_result.get("citations") and not result.get("citations"):
                result["citations"] = secondary_result.get("citations")
            if secondary_result.get("sources"):
                result["sources"] = (result.get("sources") or []) + secondary_result.get("sources", [])
            if secondary_result.get("confidence") and not result.get("confidence"):
                result["confidence"] = secondary_result.get("confidence")
            if secondary_result.get("explanation") and not result.get("explanation"):
                result["explanation"] = secondary_result.get("explanation")
            # Append brief collaborator note for explainability
            note = secondary_result.get("reply") or secondary_result.get("answer")
            if note and intent != "knowledge":
                result["reply"] = (
                    f"{result.get('reply') or result.get('advice') or ''}\n\n"
                    f"[Collaborator:{collab}] {note[:700]}"
                ).strip()

        return {
            "agent": result.get("agent", getattr(agent, "name", intent)),
            "intent": intent,
            "plan": plan,
            "reply": result.get("reply") or result.get("message") or result.get("advice") or "",
            "risk_level": result.get("risk_level"),
            "results": result,
            "sources": result.get("sources", []),
            "citations": result.get("citations", []),
            "confidence": result.get("confidence"),
            "explanation": result.get("explanation"),
            "collaborators": collaborators_run,
        }

    async def chat(self, message: str, conversation_id: Optional[str] = None, **payload: Any) -> Dict[str, Any]:
        conversation_id = conversation_id or str(uuid4())
        language = normalize_language(payload.get("language") or (payload.get("context") or {}).get("language") or "en")
        await self.memory.append(conversation_id, "user", message)
        history = await self.memory.get_history(conversation_id)
        history_snippet = self._history_snippet(history)

        understanding = await self.understand(message)
        state = {
            "message": message,
            "payload": {
                **payload,
                "language": language,
                "history_snippet": history_snippet,
                "conversation_id": conversation_id,
            },
            "conversation_id": conversation_id,
            **understanding,
        }
        final = await self.graph.ainvoke(state)
        reply = final.get("reply") or (
            "I can help with general health questions. Please consult a clinician for diagnosis."
        )
        reply = await ensure_language(reply, language)
        # Append localized safety line
        reply = f"{reply}\n\n{t('not_a_diagnosis', language)} {t('consult_clinician', language)}"

        confidence = final.get("confidence") or final.get("results", {}).get("confidence")
        citations = final.get("citations") or final.get("results", {}).get("citations") or []
        explanation = final.get("explanation") or final.get("results", {}).get("explanation")
        risk_level = final.get("risk_level") or final.get("results", {}).get("risk_level")

        hitl_required = requires_human_review(risk_level, confidence, final.get("intent"))
        pending_review = None
        if hitl_required and payload.get("enable_hitl", True):
            pending_review = {
                "required": True,
                "status": "pending_client_enqueue",
                "message": "High-risk recommendation flagged for clinician human-in-the-loop review.",
            }
            # Soft-gate: keep draft but mark clearly
            reply = (
                "[PENDING CLINICIAN REVIEW]\n"
                + reply
                + "\n\nThis draft will not be treated as actionable guidance until a clinician approves it."
            )

        final_response = {
            "conversation_id": conversation_id,
            "reply": reply,
            "agent": final.get("agent", "master"),
            "orchestrator": "master",
            "intent": final.get("intent"),
            "plan": final.get("plan") or understanding["plan"],
            "sources": final.get("sources", []),
            "citations": citations,
            "confidence": confidence,
            "explanation": explanation
            or {
                "method": "Master multi-agent orchestration",
                "collaborators": final.get("collaborators") or [final.get("agent")],
                "evidence_used": citations,
            },
            "risk_level": risk_level,
            "human_review": pending_review,
            "language": language,
            "memory": {"turns": len(history) + 1, "injected": bool(history_snippet)},
            "metadata": {
                **(final.get("results") or {}),
                "collaborators": final.get("collaborators") or [],
            },
            "architecture": {
                "flow": "User → Master AI Agent → Specialists (collab) → Evidence → (HITL?) → Final Response",
                "specialists": list(self.SPECIALISTS),
                "retrieval": "hybrid_vector_graphrag",
            },
            "disclaimer": settings.medical_disclaimer,
        }
        await self.memory.append(
            conversation_id,
            "assistant",
            reply,
            {
                "agent": final.get("agent"),
                "plan": final.get("plan"),
                "confidence": confidence,
                "hitl": bool(hitl_required),
            },
        )
        return final_response

    async def run_named(self, agent_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        agents = self._agent_map()
        if agent_name not in agents:
            raise KeyError(f"Unknown agent: {agent_name}")
        return await agents[agent_name].run(payload)

    async def run_crew(self, query: str) -> Dict[str, Any]:
        framework = (settings.agent_framework or "crewai").lower()
        if framework == "autogen":
            if self.autogen is None:
                return await run_autogen_fallback(query)
            try:
                proxy = self.autogen["user_proxy"]
                agents = self.autogen["agents"]
                proxy.initiate_chat(agents[0], message=query, max_turns=1)
                return {"crew": "autogen", "reply": f"AutoGen processed: {query}"}
            except Exception as exc:  # noqa: BLE001
                logger.warning("autogen_run_failed", error=str(exc))
                return await run_autogen_fallback(query)

        if self.crew is None:
            return await run_crew_fallback(query)
        try:
            output = self.crew.kickoff(inputs={"query": query})
            return {"crew": "crewai", "reply": str(output)}
        except Exception as exc:  # noqa: BLE001
            logger.warning("crew_run_failed", error=str(exc))
            return await run_crew_fallback(query)


_master: Optional[MasterAgent] = None


def get_master_agent() -> MasterAgent:
    global _master
    if _master is None:
        _master = MasterAgent()
    return _master
