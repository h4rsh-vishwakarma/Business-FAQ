from __future__ import annotations

import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


CONTACT_PATTERN = re.compile(r"(^[^@\s]+@[^@\s]+\.[^@\s]+$)|(^\+?[0-9][0-9\-\s]{8,}$)")


class ChatMessage(BaseModel):
    session_id: str = Field(min_length=3, max_length=64)
    message: str = Field(min_length=1, max_length=1000)


class ChatResponse(BaseModel):
    session_id: str
    message: str
    quick_replies: list[str] = Field(default_factory=list)
    requires_contact: bool = False
    lead_captured: bool = False


class LeadCapture(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    contact: str = Field(min_length=5, max_length=255)
    lead_type: str = Field(default="general_inquiry", max_length=64)
    notes: str | None = Field(default=None, max_length=2000)

    @field_validator("contact")
    @classmethod
    def validate_contact(cls, value: str) -> str:
        if not CONTACT_PATTERN.match(value.strip()):
            raise ValueError("Contact must be a valid email or phone number.")
        return value.strip()


class LeadOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    contact: str
    lead_type: str
    notes: str | None
    created_at: datetime


class HealthResponse(BaseModel):
    status: str
    business: str
