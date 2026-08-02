"""LangGraph workflow: understand → plan → orchestrate specialists."""

from typing import Any, Dict, List, Optional, TypedDict

from core.logging import get_logger

logger = get_logger(__name__)


class AgentState(TypedDict, total=False):
    message: str
    intent: str
    plan: List[str]
    payload: Dict[str, Any]
    results: Dict[str, Any]
    reply: str
    agent: str
    risk_level: Optional[str]
    sources: List[Dict[str, Any]]


def classify_intent(message: str) -> str:
    text = message.lower()
    rules = [
        ("emergency", ["chest pain", "stroke", "cannot breathe", "emergency", "ambulance"]),
        ("symptom", ["symptom", "fever", "pain", "cough", "headache", "nausea"]),
        ("prescription", ["prescription", "medicine", "dosage", "drug", "frequency"]),
        ("lab", ["lab", "cbc", "blood report", "urine", "liver", "creatinine", "glucose"]),
        ("appointment", ["appointment", "book doctor", "schedule", "reschedule", "department"]),
        ("reminder", ["reminder", "remind me", "medicine reminder", "take medicine"]),
        ("followup", ["follow-up", "follow up", "followup", "recheck", "next visit"]),
        ("insurance", ["insurance", "claim", "coverage", "policy"]),
        ("nutrition", ["diet", "nutrition", "bmi", "calories", "exercise", "water"]),
        ("knowledge", ["who", "cdc", "guideline", "what is", "explain", "disease", "interaction"]),
    ]
    for intent, keys in rules:
        if any(k in text for k in keys):
            return intent
    return "knowledge"


def build_plan(intent: str, message: str) -> List[str]:
    """Task decomposition / planning for the master orchestrator."""
    base = [
        "Understand user request and safety constraints",
        "Screen for emergency red flags",
        f"Route to specialist agent: {intent}",
        "Attach uncertainty disclaimer and clinician recommendation",
        "Persist conversation memory",
    ]
    extras = {
        "symptom": ["Estimate risk score", "Propose next action"],
        "lab": ["OCR if needed", "Flag abnormal values", "Provide suggestions"],
        "prescription": ["Extract meds/dosage/frequency/duration", "Check interactions/allergies/duplicates"],
        "appointment": ["Resolve doctor/department/time slot", "Sync HMS if configured"],
        "emergency": ["Trigger n8n workflow", "Request ambulance + alerts"],
        "reminder": ["Create medication/care reminder", "Set schedule notifications"],
        "followup": ["Schedule follow-up", "Recommend tests", "Queue notifications"],
        "insurance": ["Validate policy", "Estimate claim/hospital coverage"],
        "nutrition": ["Compute BMI/calories/water", "Build diet + exercise plan"],
        "knowledge": ["Retrieve WHO/CDC/SOP via RAG/GraphRAG"],
    }
    return base[:2] + extras.get(intent, []) + base[2:]


def build_langgraph_app(master_runner):
    """Build a LangGraph StateGraph if available; otherwise return a simple runner."""
    try:
        from langgraph.graph import END, StateGraph

        async def understand_node(state: AgentState) -> AgentState:
            intent = classify_intent(state.get("message", ""))
            return {**state, "intent": intent}

        async def plan_node(state: AgentState) -> AgentState:
            plan = build_plan(state.get("intent", "knowledge"), state.get("message", ""))
            return {**state, "plan": plan}

        async def execute_node(state: AgentState) -> AgentState:
            result = await master_runner(state)
            return {**state, **result}

        # Node name must not collide with AgentState keys (e.g. "plan").
        graph = StateGraph(AgentState)
        graph.add_node("understand", understand_node)
        graph.add_node("planner", plan_node)
        graph.add_node("execute", execute_node)
        graph.set_entry_point("understand")
        graph.add_edge("understand", "planner")
        graph.add_edge("planner", "execute")
        graph.add_edge("execute", END)
        return graph.compile()
    except Exception as exc:  # noqa: BLE001
        logger.warning("langgraph_unavailable", error=str(exc))

        class SimpleGraph:
            async def ainvoke(self, state: AgentState) -> AgentState:
                intent = classify_intent(state.get("message", ""))
                plan = build_plan(intent, state.get("message", ""))
                state = {**state, "intent": intent, "plan": plan}
                result = await master_runner(state)
                return {**state, **result}

        return SimpleGraph()
