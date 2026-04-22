from pydantic import BaseModel, Field
from typing import Literal


class Message(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]
    scenario_id: str | None = None
    model: str = "gemma4:e4b"
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)


class ChatChunk(BaseModel):
    content: str
    done: bool = False


class PedagogyBlock(BaseModel):
    corrections: list[dict] = []
    vocabulary: list[dict] = []
    encouragement: str = ""
