"""Voice consultation APIs — STT + TTS + chat."""

from pathlib import Path

import aiofiles
from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from agents.master import get_master_agent
from auth.deps import CurrentUser
from core.config import settings
from i18n.languages import normalize_language
from utils.speech import synthesize_speech, transcribe_audio

router = APIRouter()


class TTSRequest(BaseModel):
    text: str = Field(min_length=1, max_length=4000)
    language: str = "en"


@router.post("/voice/transcribe")
async def voice_transcribe(
    user: CurrentUser,
    file: UploadFile = File(...),
    language: str = Form(default="en"),
):
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    path = upload_dir / f"voice_{user.id}_{file.filename}"
    async with aiofiles.open(path, "wb") as f:
        await f.write(await file.read())
    text = transcribe_audio(str(path), language=normalize_language(language))
    return {"text": text, "language": normalize_language(language), "file_path": str(path)}


@router.post("/voice/consult")
async def voice_consult(
    user: CurrentUser,
    file: UploadFile = File(...),
    language: str = Form(default="en"),
    conversation_id: str | None = Form(default=None),
):
    """Speech-to-text → Master Agent → optional TTS file path."""
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    path = upload_dir / f"consult_{user.id}_{file.filename}"
    async with aiofiles.open(path, "wb") as f:
        await f.write(await file.read())
    lang = normalize_language(language)
    transcript = transcribe_audio(str(path), language=lang)
    master = get_master_agent()
    result = await master.chat(
        transcript or "No speech detected",
        conversation_id=conversation_id,
        language=lang,
        enable_hitl=True,
    )
    audio_path = synthesize_speech(result.get("reply") or "", language=lang)
    return {
        "transcript": transcript,
        "chat": result,
        "tts_path": audio_path,
        "language": lang,
    }


@router.post("/voice/tts")
async def voice_tts(data: TTSRequest, user: CurrentUser):
    path = synthesize_speech(data.text, language=normalize_language(data.language))
    suffix = Path(path).suffix.lower()
    media = "audio/mpeg" if suffix == ".mp3" else ("audio/wav" if suffix == ".wav" else "text/plain")
    return FileResponse(path, media_type=media, filename=Path(path).name)
