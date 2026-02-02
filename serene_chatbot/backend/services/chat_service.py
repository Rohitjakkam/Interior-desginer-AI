"""Chat service for managing conversations."""

import uuid
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from ..config import SESSION_TIMEOUT_HOURS, MAX_CONVERSATION_HISTORY
from ..knowledge.company_data import (
    GREETING_MESSAGE,
    QUICK_REPLIES_INITIAL,
    QUICK_REPLIES_SERVICES,
    QUICK_REPLIES_AFTER_INFO,
    get_faq_response,
    COMPANY_INFO
)
from .gemini_service import get_gemini_service


class ChatSession:
    """Represents a chat session with conversation history."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.history: List[Dict[str, str]] = []
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.lead_collected = False
        self.context: Dict = {}

    def add_message(self, role: str, content: str):
        """Add a message to history."""
        self.history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self.last_activity = datetime.now()

        # Trim history if too long
        if len(self.history) > MAX_CONVERSATION_HISTORY * 2:
            self.history = self.history[-MAX_CONVERSATION_HISTORY * 2:]

    def get_gemini_history(self) -> List[Dict[str, str]]:
        """Get history formatted for Gemini API."""
        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in self.history
        ]

    def is_expired(self) -> bool:
        """Check if session has expired."""
        expiry_time = self.last_activity + timedelta(hours=SESSION_TIMEOUT_HOURS)
        return datetime.now() > expiry_time


class ChatService:
    """Service for handling chat interactions."""

    def __init__(self):
        self.sessions: Dict[str, ChatSession] = {}
        self.gemini = get_gemini_service()

    def get_or_create_session(self, session_id: Optional[str] = None) -> ChatSession:
        """Get existing session or create new one."""
        # Clean expired sessions
        self._cleanup_expired_sessions()

        if session_id and session_id in self.sessions:
            session = self.sessions[session_id]
            if not session.is_expired():
                return session

        # Create new session
        new_id = session_id or str(uuid.uuid4())
        session = ChatSession(new_id)
        self.sessions[new_id] = session
        return session

    def _cleanup_expired_sessions(self):
        """Remove expired sessions."""
        expired = [
            sid for sid, session in self.sessions.items()
            if session.is_expired()
        ]
        for sid in expired:
            del self.sessions[sid]

    def process_message(
        self,
        message: str,
        session_id: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Process a chat message and return response.

        Args:
            message: User's message
            session_id: Optional session ID
            context: Optional context data

        Returns:
            Response dictionary with text, quick replies, and action
        """
        session = self.get_or_create_session(session_id)

        if context:
            session.context.update(context)

        # Check for special commands/intents
        intent = self.gemini.analyze_intent(message)

        # Handle greeting for new sessions
        if not session.history and intent["is_greeting"]:
            return self._handle_greeting(session)

        # Check for FAQ match first
        faq_response = get_faq_response(message)
        if faq_response:
            session.add_message("user", message)
            session.add_message("model", faq_response)
            return {
                "response": faq_response,
                "quick_replies": QUICK_REPLIES_AFTER_INFO,
                "action": "none",
                "session_id": session.session_id
            }

        # Handle specific intents
        if intent["wants_quote"] or intent["wants_register"]:
            return self._handle_quote_request(session, message)

        if intent["asks_services"]:
            return self._handle_services_query(session, message)

        if intent["asks_contact"]:
            return self._handle_contact_query(session, message)

        # Default: Use Gemini for response
        return self._generate_ai_response(session, message)

    def _handle_greeting(self, session: ChatSession) -> Dict:
        """Handle greeting message."""
        session.add_message("user", "Hello")
        session.add_message("model", GREETING_MESSAGE)

        return {
            "response": GREETING_MESSAGE,
            "quick_replies": QUICK_REPLIES_INITIAL,
            "action": "none",
            "session_id": session.session_id
        }

    def _handle_quote_request(self, session: ChatSession, message: str) -> Dict:
        """Handle request for quote/estimate."""
        session.add_message("user", message)

        response = """That's great! I'd love to help you get a personalized quote.

To provide you with an accurate estimate, I'll need a few details:
- Your name
- Mobile number
- Property location
- Type of property (1BHK, 2BHK, etc.)
- Your budget range

Would you like to share these details now?"""

        session.add_message("model", response)

        return {
            "response": response,
            "quick_replies": ["Yes, let's proceed", "Tell me more first"],
            "action": "collect_lead",
            "session_id": session.session_id
        }

    def _handle_services_query(self, session: ChatSession, message: str) -> Dict:
        """Handle query about services."""
        session.add_message("user", message)

        services = COMPANY_INFO["services"]
        response = """At Serene Design Studio, we offer three interior design packages:

**Basic Interior** - Smart, functional designs for budget-friendly homes with clean layouts.

**Premium Interior** - Enhanced design details with quality finishes for modern homes.

**Luxury Interior** - Exclusive, high-end interiors with bespoke detailing.

We also offer Full Home Interiors, Custom Furniture, and Office Interiors.

Which package interests you?"""

        session.add_message("model", response)

        return {
            "response": response,
            "quick_replies": QUICK_REPLIES_SERVICES,
            "action": "none",
            "session_id": session.session_id
        }

    def _handle_contact_query(self, session: ChatSession, message: str) -> Dict:
        """Handle contact information query."""
        session.add_message("user", message)

        response = f"""You can reach us at:

**Address:** {COMPANY_INFO["address"]}

We'd be happy to schedule a consultation at your convenience. Would you like to share your details so our team can contact you?"""

        session.add_message("model", response)

        return {
            "response": response,
            "quick_replies": ["Schedule Consultation", "Get Directions"],
            "action": "none",
            "session_id": session.session_id
        }

    def _generate_ai_response(self, session: ChatSession, message: str) -> Dict:
        """Generate AI response using Gemini."""
        session.add_message("user", message)

        # Get response from Gemini
        response = self.gemini.generate_response(
            message,
            session.get_gemini_history()[:-1]  # Exclude current message as it's sent separately
        )

        session.add_message("model", response)

        # Determine quick replies based on response content
        quick_replies = QUICK_REPLIES_AFTER_INFO
        if "estimate" in response.lower() or "quote" in response.lower():
            quick_replies = ["Get Free Estimate", "More Questions"]

        return {
            "response": response,
            "quick_replies": quick_replies,
            "action": "none",
            "session_id": session.session_id
        }

    def get_initial_greeting(self, session_id: Optional[str] = None) -> Dict:
        """Get initial greeting for new chat."""
        session = self.get_or_create_session(session_id)

        return {
            "response": GREETING_MESSAGE,
            "quick_replies": QUICK_REPLIES_INITIAL,
            "action": "none",
            "session_id": session.session_id
        }


# Singleton instance
_chat_service: Optional[ChatService] = None


def get_chat_service() -> ChatService:
    """Get or create chat service instance."""
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
    return _chat_service
