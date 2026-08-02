"""Speech-to-text (Whisper) and text-to-speech helpers."""

from pathlib import Path
from typing import Optional
from uuid import uuid4

from core.config import settings
from core.logging import get_logger

logger = get_logger(__name__)
_model = None


def transcribe_audio(file_path: str, language: Optional[str] = None) -> str:
    global _model
    path = Path(file_path)
    if not path.exists():
        return ""
    try:
        import whisper

        if _model is None:
            _model = whisper.load_model(settings.whisper_model)
        kwargs = {}
        if language:
            kwargs["language"] = language.split("-")[0]
        result = _model.transcribe(str(path), **kwargs)
        return str(result.get("text", "")).strip()
    except Exception as exc:  # noqa: BLE001
        logger.warning("whisper_unavailable", error=str(exc))
        sidecar = path.with_suffix(".txt")
        if sidecar.exists():
            return sidecar.read_text(encoding="utf-8")
        return ""


def synthesize_speech(text: str, language: str = "en", out_dir: Optional[str] = None) -> str:
    """
    Text-to-speech. Tries gTTS, then pyttsx3, else writes a .txt sidecar path marker.
    Returns path to audio (mp3/wav) or txt fallback.
    """
    out_dir = out_dir or settings.upload_dir
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    stem = Path(out_dir) / f"tts_{uuid4().hex}"
    lang = (language or "en").split("-")[0]

    try:
        from gtts import gTTS

        path = stem.with_suffix(".mp3")
        gTTS(text=text[:4000], lang=lang if lang != "zh" else "zh-CN").save(str(path))
        return str(path)
    except Exception as exc:  # noqa: BLE001
        logger.warning("gtts_unavailable", error=str(exc))

    try:
        import pyttsx3

        path = stem.with_suffix(".wav")
        engine = pyttsx3.init()
        engine.save_to_file(text[:4000], str(path))
        engine.runAndWait()
        if path.exists():
            return str(path)
    except Exception as exc:  # noqa: BLE001
        logger.warning("pyttsx3_unavailable", error=str(exc))

    path = stem.with_suffix(".txt")
    path.write_text(text, encoding="utf-8")
    return str(path)


def ocr_image(file_path: str) -> str:
    try:
        import pytesseract
        from PIL import Image

        return pytesseract.image_to_string(Image.open(file_path))
    except Exception as exc:  # noqa: BLE001
        logger.warning("tesseract_unavailable", error=str(exc))
        txt = Path(file_path).with_suffix(".txt")
        return txt.read_text(encoding="utf-8") if txt.exists() else ""
