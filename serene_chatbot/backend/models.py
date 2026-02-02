"""Pydantic models for request/response validation."""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    session_id: Optional[str] = None
    message: str = Field(..., min_length=1, max_length=2000)
    context: Optional[dict] = None


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str
    quick_replies: List[str] = []
    action: str = "none"  # none, collect_lead, show_form
    session_id: str


class LeadRequest(BaseModel):
    """Request model for lead registration."""
    name: str = Field(..., min_length=2, max_length=100)
    mobile: str = Field(..., pattern=r"^\d{10}$")
    location: str = Field(..., min_length=2, max_length=200)
    house_type: str = Field(..., min_length=1, max_length=50)
    budget_range: str = Field(..., min_length=1, max_length=100)
    session_id: Optional[str] = None


class LeadResponse(BaseModel):
    """Response model for lead registration."""
    success: bool
    message: str
    lead_id: Optional[str] = None


class Lead(BaseModel):
    """Lead data model for storage."""
    id: str
    name: str
    mobile: str
    location: str
    house_type: str
    budget_range: str
    session_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    source: str = "chatbot"


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    version: str
    timestamp: datetime
