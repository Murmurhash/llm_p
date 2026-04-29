from datetime import datetime

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Incoming chat request from the client."""

    prompt: str = Field(min_length=1, description="User prompt to the LLM")
    system: str | None = Field(
        default=None,
        description="Optional system instruction prepended to the conversation",
    )
    max_history: int = Field(
        default=10,
        ge=0,
        le=100,
        description="How many previous messages to include as context",
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Sampling temperature for the LLM",
    )


class ChatResponse(BaseModel):
    """Response from POST /chat with the LLM's answer."""

    answer: str


class ChatMessagePublic(BaseModel):
    """Single chat-history item (used by GET /chat/history)."""

    id: int
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}
