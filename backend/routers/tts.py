from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from backend.services import piper_service

router = APIRouter(prefix="/tts", tags=["tts"])


class TTSRequest(BaseModel):
    text: str
    lang: str = "fr"


@router.post("/")
async def synthesize(request: TTSRequest):
    """
    POST /tts — synthesizes text to WAV via Piper TTS.
    Returns audio/wav bytes.
    Requires piper binary and voice model. See PIPER_BIN / PIPER_VOICE_* env vars.
    """
    try:
        wav_bytes = await piper_service.synthesize(request.text, lang=request.lang)
        return Response(content=wav_bytes, media_type="audio/wav")
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
