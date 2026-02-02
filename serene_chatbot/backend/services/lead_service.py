"""Lead management service for storing and managing customer leads."""

import json
import os
import uuid
from typing import List, Optional, Dict
from datetime import datetime
from ..config import LEADS_FILE, STORAGE_DIR
from ..models import Lead, LeadRequest


class LeadService:
    """Service for managing customer leads."""

    def __init__(self):
        """Initialize lead service and ensure storage exists."""
        self._ensure_storage_exists()

    def _ensure_storage_exists(self):
        """Ensure storage directory and file exist."""
        os.makedirs(STORAGE_DIR, exist_ok=True)
        if not os.path.exists(LEADS_FILE):
            self._save_leads([])

    def _load_leads(self) -> List[Dict]:
        """Load leads from JSON file."""
        try:
            with open(LEADS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save_leads(self, leads: List[Dict]):
        """Save leads to JSON file."""
        with open(LEADS_FILE, 'w', encoding='utf-8') as f:
            json.dump(leads, f, indent=2, default=str)

    def create_lead(self, lead_data: LeadRequest, session_id: Optional[str] = None) -> Lead:
        """
        Create a new lead.

        Args:
            lead_data: Lead request data
            session_id: Optional chat session ID

        Returns:
            Created Lead object
        """
        lead = Lead(
            id=str(uuid.uuid4()),
            name=lead_data.name,
            mobile=lead_data.mobile,
            location=lead_data.location,
            house_type=lead_data.house_type,
            budget_range=lead_data.budget_range,
            session_id=session_id or lead_data.session_id,
            created_at=datetime.now(),
            source="chatbot"
        )

        # Load existing leads
        leads = self._load_leads()

        # Check for duplicate (same mobile number in last 24 hours)
        recent_duplicate = self._check_recent_duplicate(leads, lead.mobile)
        if recent_duplicate:
            # Update existing lead instead of creating duplicate
            return self._update_existing_lead(leads, recent_duplicate, lead)

        # Add new lead
        leads.append(lead.model_dump())
        self._save_leads(leads)

        return lead

    def _check_recent_duplicate(self, leads: List[Dict], mobile: str) -> Optional[Dict]:
        """Check if there's a recent lead with same mobile number."""
        cutoff = datetime.now().timestamp() - (24 * 60 * 60)  # 24 hours ago

        for lead in leads:
            if lead.get("mobile") == mobile:
                try:
                    created_at = lead.get("created_at")
                    if isinstance(created_at, str):
                        lead_time = datetime.fromisoformat(created_at.replace('Z', '+00:00')).timestamp()
                    else:
                        lead_time = created_at.timestamp() if hasattr(created_at, 'timestamp') else 0

                    if lead_time > cutoff:
                        return lead
                except (ValueError, TypeError):
                    continue

        return None

    def _update_existing_lead(self, leads: List[Dict], existing: Dict, new_lead: Lead) -> Lead:
        """Update existing lead with new information."""
        for i, lead in enumerate(leads):
            if lead.get("id") == existing.get("id"):
                # Update with new data but keep original ID and created_at
                leads[i].update({
                    "name": new_lead.name,
                    "location": new_lead.location,
                    "house_type": new_lead.house_type,
                    "budget_range": new_lead.budget_range,
                    "updated_at": datetime.now().isoformat()
                })
                self._save_leads(leads)

                # Return the updated lead
                new_lead.id = existing.get("id")
                return new_lead

        return new_lead

    def get_lead(self, lead_id: str) -> Optional[Lead]:
        """Get a lead by ID."""
        leads = self._load_leads()
        for lead_data in leads:
            if lead_data.get("id") == lead_id:
                return Lead(**lead_data)
        return None

    def get_all_leads(self) -> List[Lead]:
        """Get all leads."""
        leads = self._load_leads()
        return [Lead(**lead_data) for lead_data in leads]

    def get_leads_by_session(self, session_id: str) -> List[Lead]:
        """Get leads associated with a specific session."""
        leads = self._load_leads()
        return [
            Lead(**lead_data)
            for lead_data in leads
            if lead_data.get("session_id") == session_id
        ]

    def delete_lead(self, lead_id: str) -> bool:
        """Delete a lead by ID."""
        leads = self._load_leads()
        original_count = len(leads)
        leads = [lead for lead in leads if lead.get("id") != lead_id]

        if len(leads) < original_count:
            self._save_leads(leads)
            return True
        return False

    def get_leads_stats(self) -> Dict:
        """Get statistics about leads."""
        leads = self._load_leads()

        # Count by house type
        house_types = {}
        budget_ranges = {}

        for lead in leads:
            ht = lead.get("house_type", "Unknown")
            br = lead.get("budget_range", "Unknown")

            house_types[ht] = house_types.get(ht, 0) + 1
            budget_ranges[br] = budget_ranges.get(br, 0) + 1

        return {
            "total_leads": len(leads),
            "by_house_type": house_types,
            "by_budget_range": budget_ranges
        }


# Singleton instance
_lead_service: Optional[LeadService] = None


def get_lead_service() -> LeadService:
    """Get or create lead service instance."""
    global _lead_service
    if _lead_service is None:
        _lead_service = LeadService()
    return _lead_service
