from __future__ import annotations

import re

from rapidfuzz import fuzz
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ChatSession, ConversationLog, Lead
from app.schemas import LeadCapture


GREETING_KEYWORDS = {"hi", "hello", "hey", "good morning", "good evening"}
LEAD_KEYWORDS = {
    "book",
    "booking",
    "reserve",
    "reservation",
    "table",
    "callback",
    "call back",
    "contact",
    "catering",
    "event",
    "party",
    "private dining",
    "human",
}
DEFAULT_QUICK_REPLIES = ["Menu", "Hours", "Reservations", "Catering"]


class ChatEngine:
    def __init__(self, business_name: str, faqs: list[dict]) -> None:
        self.business_name = business_name
        self.faqs = faqs

    def respond(self, db: Session, session_key: str, message: str) -> dict:
        clean_message = message.strip()
        session = self._get_or_create_session(db, session_key)
        session.last_user_message = clean_message
        self._log_message(db, session, "user", clean_message)

        if session.current_stage == "awaiting_name":
            response = self._handle_name_step(session, clean_message)
        elif session.current_stage == "awaiting_contact":
            response = self._handle_contact_step(db, session, clean_message)
        else:
            response = self._handle_general_message(session, clean_message)

        self._log_message(db, session, "bot", response["message"])
        db.commit()
        return response

    def _handle_name_step(self, session: ChatSession, message: str) -> dict:
        name = re.sub(r"\s+", " ", message).strip()
        if len(name) < 2:
            return {
                "message": "I need a little more than that for your name. What should our team call you?",
                "quick_replies": [],
                "requires_contact": True,
                "lead_captured": False,
            }

        session.lead_name = name
        session.current_stage = "awaiting_contact"
        return {
            "message": f"Thanks, {name}. Share your phone number or email and our team will follow up shortly.",
            "quick_replies": [],
            "requires_contact": True,
            "lead_captured": False,
        }

    def _handle_contact_step(self, db: Session, session: ChatSession, message: str) -> dict:
        try:
            payload = LeadCapture(
                name=session.lead_name or "Guest",
                contact=message,
                lead_type=session.pending_intent or "general_inquiry",
                notes=session.last_user_message,
            )
        except Exception:
            return {
                "message": "That contact detail does not look valid. Send a phone number or email address.",
                "quick_replies": [],
                "requires_contact": True,
                "lead_captured": False,
            }

        lead = Lead(
            session=session,
            name=payload.name,
            contact=payload.contact,
            lead_type=payload.lead_type,
            notes="Captured through chatbot lead flow.",
        )
        db.add(lead)
        session.current_stage = "idle"
        session.pending_intent = None
        session.lead_name = None
        return {
            "message": f"All set. We’ve saved your details and the {self.business_name} team will reach out soon.",
            "quick_replies": ["Menu", "Hours", "Location"],
            "requires_contact": False,
            "lead_captured": True,
        }

    def _handle_general_message(self, session: ChatSession, message: str) -> dict:
        normalized = message.lower()
        if any(keyword in normalized for keyword in GREETING_KEYWORDS):
            return {
                "message": (
                    f"Welcome to {self.business_name}. I can help with menu questions, opening hours, "
                    "reservations, catering, or connect you with the team."
                ),
                "quick_replies": DEFAULT_QUICK_REPLIES,
                "requires_contact": False,
                "lead_captured": False,
            }

        if any(keyword in normalized for keyword in LEAD_KEYWORDS):
            session.current_stage = "awaiting_name"
            session.pending_intent = self._classify_lead_type(normalized)
            return {
                "message": "Happy to help with that. First, what is your name?",
                "quick_replies": [],
                "requires_contact": True,
                "lead_captured": False,
            }

        faq_match = self._match_faq(normalized)
        if faq_match is not None:
            return {
                "message": faq_match["answer"],
                "quick_replies": faq_match.get("suggested_replies", DEFAULT_QUICK_REPLIES),
                "requires_contact": False,
                "lead_captured": False,
            }

        return {
            "message": (
                "I don’t have a confident answer for that yet. If you want, I can have a team member follow up. "
                "Start with your name, or ask about menu, hours, reservations, catering, or parking."
            ),
            "quick_replies": ["Talk to team", "Hours", "Menu", "Parking"],
            "requires_contact": False,
            "lead_captured": False,
        }

    def _match_faq(self, message: str) -> dict | None:
        best_score = 0
        best_faq = None
        for faq in self.faqs:
            question_score = fuzz.partial_ratio(message, faq["question"].lower())
            keyword_score = max((fuzz.partial_ratio(message, keyword.lower()) for keyword in faq["keywords"]), default=0)
            score = max(question_score, keyword_score)
            if score > best_score:
                best_score = score
                best_faq = faq

        if best_score >= 72:
            return best_faq
        return None

    def _classify_lead_type(self, message: str) -> str:
        if "cater" in message or "event" in message or "party" in message:
            return "catering_inquiry"
        if "book" in message or "reserve" in message or "table" in message:
            return "reservation_request"
        return "general_inquiry"

    def _get_or_create_session(self, db: Session, session_key: str) -> ChatSession:
        query = select(ChatSession).where(ChatSession.session_id == session_key)
        session = db.scalar(query)
        if session is None:
            session = ChatSession(session_id=session_key)
            db.add(session)
            db.flush()
        return session

    def _log_message(self, db: Session, session: ChatSession, sender: str, message: str) -> None:
        db.add(ConversationLog(session=session, sender=sender, message=message))
