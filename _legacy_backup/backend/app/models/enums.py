"""
Centralized enums.

Defined once, imported by both SQLAlchemy models (as native Postgres ENUM
types) and Pydantic schemas, so the API contract and the DB constraint can
never drift apart.
"""
import enum


class UserRole(str, enum.Enum):
    CANDIDATE = "CANDIDATE"
    ADMIN = "ADMIN"


class ExperienceLevel(str, enum.Enum):
    FRESHER = "FRESHER"
    JUNIOR = "JUNIOR"
    INTERMEDIATE = "INTERMEDIATE"
    SENIOR = "SENIOR"


class DifficultyLevel(str, enum.Enum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"


class InterviewType(str, enum.Enum):
    TECHNICAL = "TECHNICAL"
    HR = "HR"
    BEHAVIORAL = "BEHAVIORAL"
    MIXED = "MIXED"


class InterviewStatus(str, enum.Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    ABANDONED = "ABANDONED"


class QuestionCategory(str, enum.Enum):
    CONCEPTUAL = "CONCEPTUAL"
    CODING = "CODING"
    PROBLEM_SOLVING = "PROBLEM_SOLVING"
    SCENARIO_BASED = "SCENARIO_BASED"
    BEHAVIORAL = "BEHAVIORAL"
    FOLLOW_UP = "FOLLOW_UP"


class EvaluationMethod(str, enum.Enum):
    LLM = "LLM"
    FALLBACK = "FALLBACK"


class ReadinessLevel(str, enum.Enum):
    EXCELLENT = "EXCELLENT"
    GOOD = "GOOD"
    AVERAGE = "AVERAGE"
    NEEDS_IMPROVEMENT = "NEEDS_IMPROVEMENT"
