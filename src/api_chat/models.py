# Defines all shared Pydantic request/response models for the FastAPI app.
# Replaces the ad-hoc dicts that were passed between modules in the CLI version.
# -- Converted to FastAPI

from pydantic import BaseModel, Field
from typing import Optional


class Message(BaseModel):
    role: str                  # "system" | "user" | "assistant"
    content: str


class ConversationHistory(BaseModel):
    messages: list[Message]
    temperature: float = Field(default=1.0, ge=0.0, le=2.0)


class NewChatRequest(BaseModel):
    """Starts a fresh conversation — mirrors the first branch of FormatInput()."""
    user_text: str
    system_input: Optional[str] = None
    temperature: float = Field(default=1.0, ge=0.0, le=2.0)


class ContinueChatRequest(BaseModel):
    """Continues an existing conversation — mirrors the else branch of FormatInput()."""
    conversation_history: ConversationHistory
    user_text: str