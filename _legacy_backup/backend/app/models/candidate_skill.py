"""Skill taxonomy and per-candidate proficiency, used to personalize question generation."""
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampedUUIDMixin

if TYPE_CHECKING:
    from app.models.user import User


class Skill(Base, TimestampedUUIDMixin):
    __tablename__ = "skills"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g. "Language", "Concept"

    candidate_links: Mapped[list["CandidateSkill"]] = relationship(back_populates="skill")

    def __repr__(self) -> str:
        return f"<Skill {self.name}>"


class CandidateSkill(Base, TimestampedUUIDMixin):
    __tablename__ = "candidate_skills"
    __table_args__ = (UniqueConstraint("user_id", "skill_id", name="uq_candidate_skill"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False
    )
    # Rolling proficiency estimate, 0-100, updated after each evaluated interview.
    proficiency_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    user: Mapped["User"] = relationship(back_populates="candidate_skills")
    skill: Mapped["Skill"] = relationship(back_populates="candidate_links")
