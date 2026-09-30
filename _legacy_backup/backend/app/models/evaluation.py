"""
Per-answer evaluation output from the NLP/AI pipeline (section 6-8).

Category scores are stored as individual float columns (not JSONB) because
they're queried/aggregated directly for the dashboard (section 14); JSONB is
reserved for open-ended, variable-shaped content like strengths/weaknesses.
"""
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, Float, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampedUUIDMixin
from app.models.enums import EvaluationMethod

if TYPE_CHECKING:
    from app.models.answer import Answer


class Evaluation(Base, TimestampedUUIDMixin):
    __tablename__ = "evaluations"

    answer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("answers.id", ondelete="CASCADE"), nullable=False, unique=True
    )

    # ---- Category scores, 0-10 each (section 6) ----
    technical_accuracy: Mapped[float] = mapped_column(Float, nullable=False)
    relevance: Mapped[float] = mapped_column(Float, nullable=False)
    completeness: Mapped[float] = mapped_column(Float, nullable=False)
    clarity: Mapped[float] = mapped_column(Float, nullable=False)
    conciseness: Mapped[float] = mapped_column(Float, nullable=False)
    concept_coverage: Mapped[float] = mapped_column(Float, nullable=False)
    semantic_similarity: Mapped[float] = mapped_column(Float, nullable=False)

    # ---- Weighted composite, normalized 0-100 (section 8) ----
    overall_score: Mapped[float] = mapped_column(Float, nullable=False)

    # ---- Structured, per-answer feedback (section 9) ----
    strengths: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    weaknesses: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    suggestions: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)

    # ---- Provenance (section 21 fallback system) ----
    evaluation_method: Mapped[EvaluationMethod] = mapped_column(
        Enum(EvaluationMethod, name="evaluation_method"), nullable=False
    )

    answer: Mapped["Answer"] = relationship(back_populates="evaluation")

    def __repr__(self) -> str:
        return f"<Evaluation answer={self.answer_id} overall={self.overall_score}>"
