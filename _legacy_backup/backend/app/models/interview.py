"""
InterviewSession: one candidate's configured interview attempt.
InterviewQuestion: join table ordering Questions within a Session, and the
anchor point Answers/Evaluations attach to.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampedUUIDMixin
from app.models.enums import (
    DifficultyLevel,
    ExperienceLevel,
    InterviewStatus,
    InterviewType,
)

if TYPE_CHECKING:
    from app.models.answer import Answer
    from app.models.question import Question
    from app.models.result import InterviewResult
    from app.models.user import User


class InterviewSession(Base, TimestampedUUIDMixin):
    __tablename__ = "interview_sessions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    job_role: Mapped[str] = mapped_column(String(100), nullable=False)
    experience: Mapped[ExperienceLevel] = mapped_column(
        Enum(ExperienceLevel, name="experience_level"), nullable=False
    )
    difficulty: Mapped[DifficultyLevel] = mapped_column(
        Enum(DifficultyLevel, name="difficulty_level"), nullable=False
    )
    interview_type: Mapped[InterviewType] = mapped_column(
        Enum(InterviewType, name="interview_type"), nullable=False
    )
    technology: Mapped[str] = mapped_column(String(100), nullable=False)
    requested_question_count: Mapped[int] = mapped_column(Integer, nullable=False)

    status: Mapped[InterviewStatus] = mapped_column(
        Enum(InterviewStatus, name="interview_status"),
        default=InterviewStatus.NOT_STARTED,
        nullable=False,
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship(back_populates="interview_sessions")
    interview_questions: Mapped[list["InterviewQuestion"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="InterviewQuestion.order_index",
    )
    result: Mapped[Optional["InterviewResult"]] = relationship(
        back_populates="session", cascade="all, delete-orphan", uselist=False
    )

    def __repr__(self) -> str:
        return f"<InterviewSession {self.id} {self.job_role}/{self.technology} {self.status}>"


class InterviewQuestion(Base, TimestampedUUIDMixin):
    __tablename__ = "interview_questions"

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False
    )
    question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("questions.id", ondelete="RESTRICT"), nullable=False
    )
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    asked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    skipped: Mapped[bool] = mapped_column(default=False, nullable=False)

    session: Mapped["InterviewSession"] = relationship(back_populates="interview_questions")
    question: Mapped["Question"] = relationship(back_populates="interview_links")
    answers: Mapped[list["Answer"]] = relationship(
        back_populates="interview_question", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<InterviewQuestion session={self.session_id} order={self.order_index}>"
