from __future__ import annotations

from datetime import datetime, timezone

UTC = timezone.utc

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    session_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    current_stage: Mapped[str] = mapped_column(String(32), default="idle")
    pending_intent: Mapped[str | None] = mapped_column(String(64), nullable=True)
    lead_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    last_user_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    messages: Mapped[list["ConversationLog"]] = relationship(back_populates="session", cascade="all, delete-orphan")
    leads: Mapped[list["Lead"]] = relationship(back_populates="session", cascade="all, delete-orphan")


class ConversationLog(Base):
    __tablename__ = "conversation_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("chat_sessions.id"), index=True)
    sender: Mapped[str] = mapped_column(String(16))
    message: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))

    session: Mapped[ChatSession] = relationship(back_populates="messages")


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("chat_sessions.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    contact: Mapped[str] = mapped_column(String(255))
    lead_type: Mapped[str] = mapped_column(String(64), default="general_inquiry")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))

    session: Mapped[ChatSession] = relationship(back_populates="leads")
