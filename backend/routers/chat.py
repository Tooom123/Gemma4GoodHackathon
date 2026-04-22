import json
import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from backend.models.schemas import ChatRequest
from backend.services import ollama_client

router = APIRouter(prefix="/chat", tags=["chat"])


async def _event_stream(request: ChatRequest):
    """Generate SSE events from Ollama streaming response."""
    messages = [m.model_dump() for m in request.messages]
    try:
        async for chunk in ollama_client.stream_chat(
            messages=messages,
            model=request.model,
            temperature=request.temperature,
        ):
            data = json.dumps({"content": chunk, "done": False})
            yield f"data: {data}\n\n"
        yield f"data: {json.dumps({'content': '', 'done': True})}\n\n"
    except (httpx.HTTPError, Exception):
        yield f"data: {json.dumps({'error': 'Ollama stream error', 'done': True})}\n\n"


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """
    POST /chat/stream — streams Gemma 4 response as Server-Sent Events.
    Each event: data: {"content": "...", "done": false}
    Final event: data: {"content": "", "done": true}
    """
    ollama_ok = await ollama_client.health_check()
    if not ollama_ok:
        raise HTTPException(
            status_code=503,
            detail="Ollama is not running. Start it with: ollama serve",
        )
    return StreamingResponse(
        _event_stream(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/health")
async def ollama_health():
    """Check if Ollama is reachable and return available models."""
    ok = await ollama_client.health_check()
    if not ok:
        raise HTTPException(status_code=503, detail="Ollama unreachable")
    models = await ollama_client.list_models()
    return {"status": "ok", "models": models}
