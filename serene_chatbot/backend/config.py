"""Configuration settings for the Serene Chatbot."""

import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.5-flash-lite"  # Fast and cost-effective model for chat

# Server Configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8001))

# CORS Configuration
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8080",
    "http://127.0.0.1:5500",
    "http://65.20.75.5",
    "https://65.20.75.5",
    "*"  # Allow all for development - restrict in production
]

# Storage Configuration
STORAGE_DIR = os.path.join(os.path.dirname(__file__), "storage")
LEADS_FILE = os.path.join(STORAGE_DIR, "leads.json")

# Session Configuration
SESSION_TIMEOUT_HOURS = 24
MAX_CONVERSATION_HISTORY = 20
