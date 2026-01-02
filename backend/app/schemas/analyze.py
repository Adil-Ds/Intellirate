"""
Schemas for Groq API analyze endpoint
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class ChatMessage(BaseModel):
    """Single chat message"""
    role: str = Field(..., description="Message role (system/user/assistant)")
    content: str = Field(..., description="Message content")


class AnalyzeRequest(BaseModel):
    """Request schema for /api/v1/analyze endpoint"""
    model: str = Field(..., description="AI model to use")
    messages: List[ChatMessage] = Field(..., description="List of chat messages")
    temperature: Optional[float] = Field(0.7, description="Sampling temperature")
    max_tokens: Optional[int] = Field(1024, description="Maximum tokens to generate")
    stream: Optional[bool] = Field(False, description="Enable streaming")


class AnalyzeResponse(BaseModel):
    """Response schema from Groq API (pass-through)"""
    choices: List[Dict[str, Any]]
    usage: Optional[Dict[str, int]] = None
    model: Optional[str] = None
    id: Optional[str] = None
    created: Optional[int] = None


class ErrorResponse(BaseModel):
    """Standardized error response"""
    error: str = Field(..., description="Error message")
    code: str = Field(..., description="Error code")
    details: Optional[str] = Field(None, description="Additional details")
