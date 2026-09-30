"""A candidate's submitted answer to one InterviewQuestion (main or follow-up)."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampedUUIDMixin

if TYPE_CHECKING:
    from app.models.evaluation import Evaluation
    from app.models.interview import InterviewQuestion


class Answer(Base, TimestampedUUIDMixin):
    __tablename__ = "answers"

    interview_question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("interview_questions.id", ondelete="CASCADE"),
        nullable=False,
    )

    text: Mapped[str] = mapped_column(Text, nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    time_taken_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Populated only when submitted via the voice interview pipeline (Phase 10).
    transcript_source: Mapped[Optional[str]] = mapped_column(nullable=True)  # "text" | "voice"

    interview_question: Mapped["InterviewQuestion"] = relationship(back_populates="answers")
    evaluation: Mapped[Optional["Evaluation"]] = relationship(
        back_populates="answer", cascade="all, delete-orphan", uselist=False
    )

    def __repr__(self) -> str:
        return f"<Answer {self.id} for question={self.interview_question_id}>"
