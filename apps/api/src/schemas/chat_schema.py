# apps/api/src/schemas/chat_schema.py
"""Schemas for FraudShield citizen AI advisor chat."""

from pydantic import BaseModel, Field

class ChatMessage(BaseModel):
    role: str = Field(..., description="Message author role: 'user' or 'assistant'")
    content: str = Field(..., description="Message text payload")

class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(default_factory=list, description="Conversation history")
    transcript: str | None = Field(default=None, description="Optional raw call transcript for assessment")

class ChatResponse(BaseModel):
    reply: str = Field(..., description="AI safety advice and explanation")
    risk_score: float = Field(..., description="Consolidated risk score 0.0 - 1.0")
    risk_band: str = Field(..., description="'low', 'needs_review', or 'high'")
    flagged_indicators: list[str] = Field(default_factory=list, description="Fired scam indicators")
    recommended_action: str = Field(default="", description="Citizen defensive action guideline")
