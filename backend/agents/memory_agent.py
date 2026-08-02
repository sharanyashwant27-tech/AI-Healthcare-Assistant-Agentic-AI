"""Conversation Memory Agent backed by Redis (with in-process fallback)."""

import json
from typing import Any, Dict, List, Optional
from uuid import uuid4

from agents.base import BaseAgent
from core.logging import get_logger

logger = get_logger(__name__)


class ConversationMemoryAgent(BaseAgent):
    name = "conversation_memory"

    def __init__(self) -> None:
        self._local: Dict[str, List[Dict[str, Any]]] = {}
        self._prefs: Dict[str, Dict[str, Any]] = {}

    async def _redis(self):
        try:
            from core.redis_client import get_redis

            return await get_redis()
        except Exception as exc:  # noqa: BLE001
            logger.warning("memory_redis_unavailable", error=str(exc))
            return None

    async def get_history(self, conversation_id: str) -> List[Dict[str, Any]]:
        r = await self._redis()
        if r is None:
            return self._local.get(conversation_id, [])
        raw = await r.lrange(f"chat:{conversation_id}", 0, -1)
        return [json.loads(x) for x in raw]

    async def append(self, conversation_id: str, role: str, content: str, meta: Optional[dict] = None) -> None:
        item = {"role": role, "content": content, "meta": meta or {}}
        r = await self._redis()
        if r is None:
            self._local.setdefault(conversation_id, []).append(item)
            return
        await r.rpush(f"chat:{conversation_id}", json.dumps(item))
        await r.expire(f"chat:{conversation_id}", 60 * 60 * 24 * 7)

    async def set_preferences(self, patient_key: str, prefs: Dict[str, Any]) -> None:
        r = await self._redis()
        if r is None:
            self._prefs[patient_key] = prefs
            return
        await r.set(f"prefs:{patient_key}", json.dumps(prefs), ex=60 * 60 * 24 * 30)

    async def get_preferences(self, patient_key: str) -> Dict[str, Any]:
        r = await self._redis()
        if r is None:
            return self._prefs.get(patient_key, {})
        raw = await r.get(f"prefs:{patient_key}")
        return json.loads(raw) if raw else {}

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        conversation_id = payload.get("conversation_id") or str(uuid4())
        action = payload.get("action") or "get"
        if action == "append":
            await self.append(conversation_id, payload.get("role", "user"), payload.get("content", ""))
        history = await self.get_history(conversation_id)
        prefs = {}
        if payload.get("patient_id"):
            prefs = await self.get_preferences(str(payload["patient_id"]))
        return {
            "agent": self.name,
            "conversation_id": conversation_id,
            "history": history,
            "preferences": prefs,
            "reply": f"Loaded {len(history)} messages for conversation {conversation_id}",
        }
