"""Gemini AI service for chat responses."""

import google.generativeai as genai
from typing import List, Dict, Optional
from ..config import GEMINI_API_KEY, GEMINI_MODEL
from ..knowledge.company_data import SYSTEM_PROMPT


class GeminiService:
    """Service for interacting with Google Gemini API."""

    def __init__(self):
        """Initialize Gemini service."""
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found in environment variables")

        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel(model_name=GEMINI_MODEL)
        self.system_prompt = SYSTEM_PROMPT

    def generate_response(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Generate a response using Gemini.

        Args:
            message: User's message
            conversation_history: List of previous messages [{"role": "user/model", "parts": ["text"]}]

        Returns:
            Generated response text
        """
        try:
            # Build the chat history with system prompt as first exchange
            history = [
                {"role": "user", "parts": [f"System Instructions: {self.system_prompt}\n\nPlease acknowledge and follow these instructions."]},
                {"role": "model", "parts": ["I understand. I am a customer service representative for Serene Design Studio. I will follow all the guidelines provided and help customers with their interior design needs professionally and warmly."]}
            ]

            if conversation_history:
                for msg in conversation_history:
                    history.append({
                        "role": msg["role"],
                        "parts": [msg["content"]]
                    })

            # Start chat with history
            chat = self.model.start_chat(history=history)

            # Generate response
            response = chat.send_message(message)

            return response.text.strip()

        except Exception as e:
            print(f"Error generating response: {e}")
            return "I apologize, but I'm having trouble processing your request right now. Please try again or contact us directly at our office."

    def analyze_intent(self, message: str) -> Dict[str, any]:
        """
        Analyze user intent from message.

        Args:
            message: User's message

        Returns:
            Dictionary with intent analysis
        """
        message_lower = message.lower()

        # Check for greeting intent
        greetings = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening", "namaste"]
        is_greeting = any(greet in message_lower for greet in greetings)

        # Check for quote/estimate intent
        quote_keywords = ["quote", "estimate", "price", "cost", "budget", "how much", "pricing"]
        wants_quote = any(keyword in message_lower for keyword in quote_keywords)

        # Check for services intent
        service_keywords = ["service", "package", "offer", "basic", "premium", "luxury", "what do you"]
        asks_services = any(keyword in message_lower for keyword in service_keywords)

        # Check for contact intent
        contact_keywords = ["contact", "call", "phone", "address", "location", "visit", "meet"]
        asks_contact = any(keyword in message_lower for keyword in contact_keywords)

        # Check for registration intent
        register_keywords = ["register", "sign up", "interested", "book", "appointment", "consultation"]
        wants_register = any(keyword in message_lower for keyword in register_keywords)

        return {
            "is_greeting": is_greeting,
            "wants_quote": wants_quote,
            "asks_services": asks_services,
            "asks_contact": asks_contact,
            "wants_register": wants_register
        }


# Singleton instance
_gemini_service: Optional[GeminiService] = None


def get_gemini_service() -> GeminiService:
    """Get or create Gemini service instance."""
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service
