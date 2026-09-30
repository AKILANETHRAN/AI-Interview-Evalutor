"""
Final, generated-once-per-session report (section 13).

Computed after the last question is submitted; aggregates all Evaluations
for the session. Stored (not recomputed on every dashboard view) so
historical reports remain stable even if scoring weights change later.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, Float, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampedUUIDMixin
from app.models.enums import ReadinessLevel

if TYPE_CHECKING:
    from app.models.interview import InterviewSession


class InterviewResult(Base, TimestampedUUIDMixin):
    __tablename__ = "interview_results"

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("interview_sessions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    overall_score: Mapped[float] = mapped_column(Float, nullable=False)  # 0-100

    # Aggregated per-category averages: technical, problem_solving,
    # communication, concept_coverage — kept as JSONB since the exact set
    # of categories reported may evolve (section 14 dashboard).
    category_scores: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    strengths: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    weaknesses: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    recommended_topics: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    improvement_plan: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)

    readiness_level: Mapped[ReadinessLevel] = mapped_column(
        Enum(ReadinessLevel, name="readiness_level"), nullable=False
    )
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    session: Mapped["InterviewSession"] = relationship(back_populates="result")

    def __repr__(self) -> str:
        return f"<InterviewResult session={self.session_id} overall={self.overall_score}>"
