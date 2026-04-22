from fastapi import APIRouter

router = APIRouter(prefix="/tts", tags=["tts"])


@router.post("/")
async def synthesize():
    """Placeholder — Piper TTS integration coming in week 2."""
    return {"message": "TTS coming in week 2"}
