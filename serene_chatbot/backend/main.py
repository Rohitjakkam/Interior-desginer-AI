"""FastAPI application for Serene Design Studio Chatbot."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import uvicorn

from .config import HOST, PORT, ALLOWED_ORIGINS
from .models import (
    ChatRequest,
    ChatResponse,
    LeadRequest,
    LeadResponse,
    HealthResponse
)
from .services.chat_service import get_chat_service
from .services.lead_service import get_lead_service

# Initialize FastAPI app
app = FastAPI(
    title="Serene Design Studio Chatbot API",
    description="AI-powered chatbot API for Serene Design Studio interior design services",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Serene Design Studio Chatbot API",
        "version": "1.0.0",
        "description": "AI-powered chatbot for interior design services",
        "endpoints": {
            "chat": "POST /chat",
            "register": "POST /register",
            "greeting": "GET /greeting",
            "health": "GET /health"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now()
    )


@app.get("/greeting", tags=["Chat"])
async def get_greeting(session_id: str = None):
    """Get initial greeting message for new chat session."""
    try:
        chat_service = get_chat_service()
        result = chat_service.get_initial_greeting(session_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    """
    Process a chat message and return AI response.

    - **session_id**: Optional session ID for conversation continuity
    - **message**: User's message
    - **context**: Optional context data
    """
    try:
        chat_service = get_chat_service()
        result = chat_service.process_message(
            message=request.message,
            session_id=request.session_id,
            context=request.context
        )
        return ChatResponse(**result)
    except Exception as e:
        print(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/register", response_model=LeadResponse, tags=["Lead"])
async def register_lead(request: LeadRequest):
    """
    Register a new lead/customer.

    - **name**: Customer name
    - **mobile**: 10-digit mobile number
    - **location**: Property location
    - **house_type**: Type of property (1BHK, 2BHK, etc.)
    - **budget_range**: Budget range for the project
    """
    try:
        lead_service = get_lead_service()
        lead = lead_service.create_lead(request)

        return LeadResponse(
            success=True,
            message="Thank you for registering! Our design expert will contact you shortly to discuss your project.",
            lead_id=lead.id
        )
    except Exception as e:
        print(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/leads", tags=["Lead"])
async def get_leads():
    """Get all leads (admin endpoint)."""
    try:
        lead_service = get_lead_service()
        leads = lead_service.get_all_leads()
        return {
            "success": True,
            "count": len(leads),
            "leads": [lead.model_dump() for lead in leads]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/leads/stats", tags=["Lead"])
async def get_leads_stats():
    """Get lead statistics (admin endpoint)."""
    try:
        lead_service = get_lead_service()
        stats = lead_service.get_leads_stats()
        return {"success": True, "stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "An unexpected error occurred",
            "detail": str(exc)
        }
    )


def start():
    """Start the server."""
    uvicorn.run(
        "backend.main:app",
        host=HOST,
        port=PORT,
        reload=True
    )


if __name__ == "__main__":
    start()
