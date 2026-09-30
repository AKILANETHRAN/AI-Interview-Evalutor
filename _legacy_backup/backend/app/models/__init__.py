"""
Import every model here so `Base.metadata` is fully populated wherever
this package is imported -- critical for Alembic autogenerate, which only
sees tables that have actually been imported into the running process.
"""
from app.core.database import Base  # noqa: F401
from app.models.answer import Answer  # noqa: F401
from app.models.candidate_skill import CandidateSkill, Skill  # noqa: F401
from app.models.evaluation import Evaluation  # noqa: F401
from app.models.interview import InterviewQuestion, InterviewSession  # noqa: F401
from app.models.question import Question  # noqa: F401
from app.models.result import InterviewResult  # noqa: F401
from app.models.user import User  # noqa: F401

__all__ = [
    "Base",
    "User",
    "Skill",
    "CandidateSkill",
    "Question",
    "InterviewSession",
    "InterviewQuestion",
    "Answer",
    "Evaluation",
    "InterviewResult",
]
