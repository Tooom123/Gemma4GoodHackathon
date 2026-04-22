from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.services import whisper_service

router = APIRouter(prefix="/whisper", tags=["whisper"])


@router.post("/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    """
    POST /whisper/transcribe — accepts audio file (webm, wav, mp3),
    returns {"text": "<transcription>"}.
    Requires whisper.cpp binary and a ggml model. See WHISPER_BIN / WHISPER_MODEL env vars.
    """
    audio_bytes = await audio.read()
    suffix = "." + (audio.filename or "audio.webm").rsplit(".", 1)[-1]
    try:
        text = await whisper_service.transcribe(audio_bytes, suffix=suffix)
        return {"text": text}
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
