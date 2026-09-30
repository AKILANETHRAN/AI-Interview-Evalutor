"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-08-10

Creates the full Phase 2 relational schema:
users, skills, candidate_skills, questions, interview_sessions,
interview_questions, answers, evaluations, interview_results.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---- Enums ----
    # create_type=False on every enum: we create each PG type explicitly,
    # exactly once, below. Without this, SQLAlchemy would also try to
    # auto-create the type the first time it's used in a create_table call,
    # producing a duplicate/conflicting `CREATE TYPE` statement.
    user_role = postgresql.ENUM("CANDIDATE", "ADMIN", name="user_role", create_type=False)
    experience_level = postgresql.ENUM(
        "FRESHER", "JUNIOR", "INTERMEDIATE", "SENIOR", name="experience_level", create_type=False
    )
    difficulty_level = postgresql.ENUM(
        "EASY", "MEDIUM", "HARD", name="difficulty_level", create_type=False
    )
    interview_type = postgresql.ENUM(
        "TECHNICAL", "HR", "BEHAVIORAL", "MIXED", name="interview_type", create_type=False
    )
    interview_status = postgresql.ENUM(
        "NOT_STARTED",
        "IN_PROGRESS",
        "COMPLETED",
        "ABANDONED",
        name="interview_status",
        create_type=False,
    )
    question_category = postgresql.ENUM(
        "CONCEPTUAL",
        "CODING",
        "PROBLEM_SOLVING",
        "SCENARIO_BASED",
        "BEHAVIORAL",
        "FOLLOW_UP",
        name="question_category",
        create_type=False,
    )
    evaluation_method = postgresql.ENUM(
        "LLM", "FALLBACK", name="evaluation_method", create_type=False
    )
    readiness_level = postgresql.ENUM(
        "EXCELLENT",
        "GOOD",
        "AVERAGE",
        "NEEDS_IMPROVEMENT",
        name="readiness_level",
        create_type=False,
    )

    bind = op.get_bind()
    for enum_type in (
        user_role,
        experience_level,
        difficulty_level,
        interview_type,
        interview_status,
        question_category,
        evaluation_method,
        readiness_level,
    ):
        enum_type.create(bind, checkfirst=True)

    # ---- users ----
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("full_name", sa.String(150), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", user_role, nullable=False, server_default="CANDIDATE"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # ---- skills ----
    op.create_table(
        "skills",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("category", sa.String(100), nullable=False),
        sa.UniqueConstraint("name", name="uq_skills_name"),
    )

    # ---- questions (self-referencing for follow-ups) ----
    op.create_table(
        "questions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("category", question_category, nullable=False),
        sa.Column("difficulty", difficulty_level, nullable=False),
        sa.Column("technology", sa.String(100), nullable=False),
        sa.Column("job_role", sa.String(100), nullable=True),
        sa.Column("expected_concepts", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("evaluation_points", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("ideal_answer", sa.Text(), nullable=False),
        sa.Column("is_followup", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("parent_question_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("is_admin_curated", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.ForeignKeyConstraint(
            ["parent_question_id"], ["questions.id"], ondelete="SET NULL", name="fk_question_parent"
        ),
    )
    op.create_index("ix_questions_technology", "questions", ["technology"])

    # ---- interview_sessions ----
    op.create_table(
        "interview_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("job_role", sa.String(100), nullable=False),
        sa.Column("experience", experience_level, nullable=False),
        sa.Column("difficulty", difficulty_level, nullable=False),
        sa.Column("interview_type", interview_type, nullable=False),
        sa.Column("technology", sa.String(100), nullable=False),
        sa.Column("requested_question_count", sa.Integer(), nullable=False),
        sa.Column("status", interview_status, nullable=False, server_default="NOT_STARTED"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_interview_sessions_user_id", "interview_sessions", ["user_id"])

    # ---- candidate_skills ----
    op.create_table(
        "candidate_skills",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("skill_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("proficiency_score", sa.Float(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["skill_id"], ["skills.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id", "skill_id", name="uq_candidate_skill"),
    )

    # ---- interview_questions ----
    op.create_table(
        "interview_questions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("question_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("asked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("skipped", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.ForeignKeyConstraint(["session_id"], ["interview_sessions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"], ondelete="RESTRICT"),
    )
    op.create_index(
        "ix_interview_questions_session_order", "interview_questions", ["session_id", "order_index"]
    )

    # ---- answers ----
    op.create_table(
        "answers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("interview_question_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("time_taken_seconds", sa.Integer(), nullable=True),
        sa.Column("transcript_source", sa.String(20), nullable=True),
        sa.ForeignKeyConstraint(
            ["interview_question_id"], ["interview_questions.id"], ondelete="CASCADE"
        ),
    )

    # ---- evaluations ----
    op.create_table(
        "evaluations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("answer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("technical_accuracy", sa.Float(), nullable=False),
        sa.Column("relevance", sa.Float(), nullable=False),
        sa.Column("completeness", sa.Float(), nullable=False),
        sa.Column("clarity", sa.Float(), nullable=False),
        sa.Column("conciseness", sa.Float(), nullable=False),
        sa.Column("concept_coverage", sa.Float(), nullable=False),
        sa.Column("semantic_similarity", sa.Float(), nullable=False),
        sa.Column("overall_score", sa.Float(), nullable=False),
        sa.Column("strengths", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("weaknesses", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("suggestions", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("evaluation_method", evaluation_method, nullable=False),
        sa.ForeignKeyConstraint(["answer_id"], ["answers.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("answer_id", name="uq_evaluation_answer"),
    )

    # ---- interview_results ----
    op.create_table(
        "interview_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("overall_score", sa.Float(), nullable=False),
        sa.Column("category_scores", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("strengths", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("weaknesses", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("recommended_topics", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("improvement_plan", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("readiness_level", readiness_level, nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["interview_sessions.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("session_id", name="uq_result_session"),
    )


def downgrade() -> None:
    op.drop_table("interview_results")
    op.drop_table("evaluations")
    op.drop_table("answers")
    op.drop_table("interview_questions")
    op.drop_table("candidate_skills")
    op.drop_table("interview_sessions")
    op.drop_index("ix_questions_technology", table_name="questions")
    op.drop_table("questions")
    op.drop_table("skills")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

    bind = op.get_bind()
    for enum_name in (
        "readiness_level",
        "evaluation_method",
        "question_category",
        "interview_status",
        "interview_type",
        "difficulty_level",
        "experience_level",
        "user_role",
    ):
        postgresql.ENUM(name=enum_name).drop(bind, checkfirst=True)
