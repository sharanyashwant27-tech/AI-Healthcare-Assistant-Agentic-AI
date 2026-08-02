"""WebSocket chat endpoint."""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from agents.master import get_master_agent
from core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    master = get_master_agent()
    conversation_id = None
    try:
        while True:
            data = await websocket.receive_json()
            message = data.get("message", "")
            conversation_id = data.get("conversation_id") or conversation_id
            result = await master.chat(message, conversation_id=conversation_id)
            conversation_id = result["conversation_id"]
            await websocket.send_json(result)
    except WebSocketDisconnect:
        logger.info("websocket_disconnected")
    except Exception as exc:  # noqa: BLE001
        logger.error("websocket_error", error=str(exc))
        await websocket.close()
