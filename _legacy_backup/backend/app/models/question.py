"""
Question bank.

`expected_concepts` / `evaluation_points` are JSONB so the NLP evaluator can
attach structured, variable-shaped criteria without new migrations.
`ideal_answer` must NEVER be serialized to a candidate-facing response —
enforced at the schema layer (see schemas/question.py, Phase 4), not here.
"""
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampedUUIDMixin
from app.models.enums import DifficultyLevel, QuestionCategory

if TYPE_CHECKING:
    from app.models.interview import InterviewQuestion


class Question(Base, TimestampedUUIDMixin):
    __tablename__ = "questions"

    text: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[QuestionCategory] = mapped_column(
        Enum(QuestionCategory, name="question_category"), nullable=False
    )
    difficulty: Mapped[DifficultyLevel] = mapped_column(
        Enum(DifficultyLevel, name="difficulty_level"), nullable=False
    )
    technology: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    job_role: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Structured evaluation criteria — internal only.
    expected_concepts: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    evaluation_points: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    ideal_answer: Mapped[str] = mapped_column(Text, nullable=False)

    # Follow-up support (section 10): a follow-up question points back at its parent.
    is_followup: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    parent_question_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("questions.id", ondelete="SET NULL"), nullable=True
    )

    # AI-generated questions are cached here; True for admin-curated bank entries.
    is_admin_curated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    parent_question: Mapped[Optional["Question"]] = relationship(
        remote_side="Question.id", backref="followup_questions"
    )
    interview_links: Mapped[list["InterviewQuestion"]] = relationship(back_populates="question")

    def __repr__(self) -> str:
        return f"<Question {self.technology}/{self.difficulty} {self.text[:40]!r}>"
