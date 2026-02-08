from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from enum import Enum

class Role(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANCE = "assistance"

class Message(BaseModel):
    role: Role
    content: str

class TokenUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

class LLMResponse(BaseModel):
    content: str
    raw_response: Dict[str, Any] = {}
    usage: TokenUsage
    model_name: str
    finish_reason: Optional[str] = None

class GenerationConfig(BaseModel):
    temperature: float = Field(default = 0.7, ge = 0.0, le = 2.0)
    max_token: Optional[int] = Field(default = 1000)
    top_p: Optional[float] = 1.0