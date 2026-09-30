# AI Interview Evaluator

An AI/NLP-powered platform that simulates technical interviews and evaluates
candidate answers using semantic similarity, concept coverage detection, and
LLM-based feedback generation — not keyword matching.

> **Status: Phase 2 — Database Models & Migrations.**
> Auth, question generation, evaluation, and UI are implemented in
> subsequent phases.

---

## 1. System Architecture

```
┌─────────────────────┐
│   React + TS SPA     │  Landing, Auth, Interview Room, Reports, Dashboard
│ (Vite, Tailwind,      │
│  Recharts)            │
└──────────┬───────────┘
           │ REST (JSON) / HTTPS
┌──────────▼───────────┐
│   FastAPI Backend     │  Routers → Pydantic schemas → Services
│  (app/api/*)          │
└──────────┬───────────┘
           │
┌──────────▼───────────┐        ┌─────────────────────────┐
│   Service Layer        │──────▶│  AI Provider Abstraction │
│ (app/services/*)       │       │  Claude / OpenAI / Local │
└──────────┬───────────┘        └───────────┬─────────────┘
           │                                  │
┌──────────▼───────────┐        ┌───────────▼─────────────┐
│  Repository Layer      │       │   NLP Evaluation Engine  │
│ (app/repositories/*)   │       │  (sentence-transformers, │
└──────────┬───────────┘        │   spaCy, NLTK)           │
           │                     └───────────────────────────┘
┌──────────▼───────────┐
│     PostgreSQL          │
│  (SQLAlchemy + Alembic) │
└─────────────────────────┘

Redis: caching + rate-limit counters (optional, degrades gracefully if absent)
```

**Layering principle:** API routers never touch the database directly. They
call services; services call repositories (data access) and the AI/NLP layer
(intelligence). This keeps evaluation logic swappable and testable in
isolation from HTTP and persistence concerns.

---

## 2. Technology Stack & Justification

| Layer | Choice | Why |
|---|---|---|
| Frontend | React 18 + TypeScript + Vite | Fast dev loop, type-safe API contracts shared conceptually with backend Pydantic schemas |
| Styling | Tailwind CSS | Rapid, consistent design system for the SaaS-style UI in section 18 |
| Charts | Recharts | Native React charts for the radar/line/bar/donut dashboard requirements |
| State | Zustand | Lightweight vs Redux for auth/session/interview state |
| Backend | FastAPI | Async-native, automatic OpenAPI docs, first-class Pydantic validation |
| ORM | SQLAlchemy 2.0 + Alembic | Explicit relational modeling for the 10-entity schema, versioned migrations |
| Database | PostgreSQL | Relational integrity for interview/question/evaluation graph; JSONB for flexible metadata (expected_concepts, evaluation_points) |
| Auth | JWT (python-jose) + passlib/bcrypt | Stateless auth suitable for SPA + future mobile clients |
| NLP | sentence-transformers (`all-MiniLM-L6-v2`), spaCy, NLTK | Semantic similarity + linguistic preprocessing, runs locally without external API dependency (enables the fallback system in section 21) |
| LLM | Provider-abstracted: Anthropic Claude / OpenAI / local | Avoids vendor lock-in per section 20; question generation & rich feedback need generative reasoning that embeddings alone can't provide |
| Cache/Rate-limit | Redis (optional) | Rate limiting and caching generated questions; app must still run without it |
| Containerization | Docker Compose | One-command local + demo environment |

---

## 3. Database Architecture (overview — full DDL in Phase 2)

```
User (id, email, password_hash, role[CANDIDATE|ADMIN], created_at)
  └─< InterviewSession (id, user_id, role, experience, difficulty,
                         interview_type, technology, status, created_at)
        └─< InterviewQuestion (id, session_id, question_id, order_index,
                                asked_at)
              └── Question (id, text, category, difficulty, technology,
                             expected_concepts JSONB, evaluation_points JSONB,
                             ideal_answer, is_followup, parent_question_id)
              └─< Answer (id, interview_question_id, text, submitted_at,
                          time_taken_seconds)
                    └─1 Evaluation (id, answer_id, technical_accuracy,
                                     relevance, completeness, clarity,
                                     concept_coverage, semantic_similarity,
                                     overall_score, strengths JSONB,
                                     weaknesses JSONB, suggestions JSONB,
                                     evaluation_method[llm|fallback])
        └─1 InterviewResult (id, session_id, overall_score, category_scores
                              JSONB, readiness_level, recommended_topics
                              JSONB, generated_at)

Skill (id, name, category)
CandidateSkill (user_id, skill_id, proficiency_score)  -- for personalization
                                                            in question gen
```

Design notes:
- `expected_concepts`, `evaluation_points`, `strengths`, `weaknesses` are
  JSONB so the NLP pipeline can attach structured, variable-shaped output
  without new migrations for every new metric.
- `ideal_answer` on `Question` is never serialized into candidate-facing
  API responses — enforced at the Pydantic schema level (separate
  `QuestionPublic` vs `QuestionInternal` schemas), not just by convention.
- Migrations via Alembic from day one; no manual schema drift.

---

## 4. Backend Architecture

```
backend/app/
├── main.py            # FastAPI app, middleware, error handlers, health check
├── core/
│   ├── config.py       # Settings (env-driven, cached)
│   ├── security.py     # JWT + password hashing (Phase 3)
│   └── logging.py      # Structured JSON logging setup (Phase 3+)
├── api/                 # Routers only — thin, delegate to services
├── models/              # SQLAlchemy ORM models (Phase 2)
├── schemas/              # Pydantic request/response schemas
├── repositories/          # DB access, no business logic
├── services/               # Business logic, orchestration
├── ai/                       # AIProvider abstraction: Claude/OpenAI/Local
├── nlp/                        # Embedding, similarity, concept extraction
└── utils/                       # Shared helpers
```

The **AIProvider abstraction** (Phase 5+) defines one interface:

```python
class AIProvider(Protocol):
    async def generate_questions(self, params: QuestionGenParams) -> list[GeneratedQuestion]: ...
    async def generate_feedback(self, answer: str, question: Question, eval_scores: dict) -> Feedback: ...
```

`ClaudeProvider`, `OpenAIProvider`, and `LocalModelProvider` implement it.
`AI_PROVIDER` env var selects which is injected — routers and services never
import a concrete provider directly.

---

## 5. Frontend Architecture

```
frontend/src/
├── pages/          # Landing, Login, Register, Dashboard, CreateInterview,
│                    InterviewRoom, EvaluationResult, InterviewReport,
│                    Analytics, History, Profile, AdminDashboard
├── components/     # Reusable UI: QuestionCard, ScoreRadar, Timer, etc.
├── layouts/        # AuthLayout, AppLayout (sidebar+topbar), AdminLayout
├── hooks/          # useAuth, useInterviewSession, useTimer
├── services/       # axios API clients (auth.ts, interviews.ts, ...)
├── contexts/       # AuthContext, ThemeContext (dark/light)
├── types/          # Shared TS interfaces mirroring backend Pydantic schemas
└── utils/          # formatting, validation helpers
```

Routing is role-aware: `ADMIN` routes are guarded separately from
`CANDIDATE` routes via a `RequireRole` wrapper (implemented in Phase 3).

---

## 6. AI/NLP Architecture (implemented Phase 5–8)

```
Candidate Answer
   → Preprocessing (spaCy: tokenize, lemmatize, clean)
   → Sentence segmentation
   → Embedding generation (sentence-transformers: all-MiniLM-L6-v2)
   → Semantic similarity (cosine sim vs ideal_answer + expected_concepts)
   → Concept coverage detection (NER + keyphrase overlap, not raw keyword match)
   → LLM evaluation pass (technical correctness, clarity, feedback text)
   → Weighted scoring (configurable weights, see below)
   → Feedback + follow-up question generation
```

Default configurable weights (Phase 7, stored in `core/config.py` /
DB-backed admin setting later):

```
overall = 0.30*technical_accuracy + 0.20*semantic_relevance
        + 0.20*concept_coverage   + 0.15*completeness
        + 0.10*clarity            + 0.05*conciseness
```

Fallback mode (section 21): if `AI_PROVIDER` call fails, the service layer
catches the failure and evaluates using only the local
sentence-transformers + concept-matching pipeline, and the API response
includes `"evaluation_method": "fallback"` so the frontend can show
*"AI evaluation temporarily unavailable. Using fallback evaluation."*

---

## 7. Project Folder Structure

```
ai-interview-evaluator/
├── frontend/
│   ├── src/{components,pages,layouts,hooks,services,contexts,utils,types}
│   └── package.json
├── backend/
│   ├── app/{api,models,schemas,services,repositories,ai,nlp,core,utils}
│   ├── alembic/versions
│   ├── main.py
│   └── requirements.txt
├── ml/{embeddings,evaluation,preprocessing,models}
├── tests/{unit,integration,api}
├── docs/
├── docker/
│   ├── backend.Dockerfile
│   ├── frontend.Dockerfile
│   └── nginx.conf
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 8. Environment Variables

See [`.env.example`](.env.example) for the full list. Highlights:

- `AI_PROVIDER` — `claude` | `openai` | `local`, switches provider with no
  code change.
- `DATABASE_URL`, `JWT_SECRET_KEY` — required, no defaults, app fails fast
  at startup if missing (enforced by Pydantic `Settings` — no `Optional`
  fallback for secrets).
- `REDIS_URL` — optional; caching/rate-limiting degrade gracefully if unset.
- Never commit a real `.env`; only `.env.example` is version-controlled.

---

## 9. API Architecture (contracts finalized per-phase; skeleton now)

Base path: `/api` (versioning via `API_V1_PREFIX`, currently unversioned in
path for simplicity — can move to `/api/v1` before public launch).

```
POST   /api/auth/register
POST   /api/auth/login
POST   /api/auth/logout

POST   /api/interviews
GET    /api/interviews
GET    /api/interviews/{id}
POST   /api/interviews/{id}/start
POST   /api/interviews/{id}/submit

POST   /api/questions/generate
GET    /api/questions
GET    /api/questions/{id}

POST   /api/evaluate
GET    /api/evaluations/{id}

GET    /api/reports/{interviewId}

GET    /api/dashboard
GET    /api/dashboard/performance
GET    /api/dashboard/topics

GET    /api/health          # implemented now
```

Standard error envelope (implemented now, `main.py`):

```json
{
  "success": false,
  "message": "Human-readable message",
  "error_code": "MACHINE_READABLE_CODE"
}
```

---

## 10. Development Roadmap

| Phase | Scope |
|---|---|
| 1 ✅ | Architecture, scaffold, config, Docker skeleton |
| 2 | SQLAlchemy models + Alembic migrations |
| 3 | Auth (register/login/JWT/RBAC) |
| 4 | Interview creation & question management endpoints |
| 5 | AI question generation |
| 6 | Interview session flow |
| 7 | NLP answer evaluation engine |
| 8 | AI feedback + follow-up question generation |
| 9 | Coding interview mode + sandboxed execution |
| 10 | Voice interview (Web Speech API / Whisper) |
| 11 | Reports & analytics dashboard |
| 12 | Admin dashboard |
| 13 | Testing suite |
| 14 | Docker/deployment hardening |

---

## 11. Phase 2 — Database Models & Migrations

**What was implemented:**

- `backend/app/core/database.py` — SQLAlchemy engine (`pool_pre_ping=True`),
  `SessionLocal`, declarative `Base`, and the `get_db` FastAPI dependency.
- `backend/app/models/enums.py` — every domain enum (`UserRole`,
  `ExperienceLevel`, `DifficultyLevel`, `InterviewType`, `InterviewStatus`,
  `QuestionCategory`, `EvaluationMethod`, `ReadinessLevel`), shared later by
  Pydantic schemas so the DB constraint and the API contract can't drift.
- `backend/app/models/base.py` — `TimestampedUUIDMixin` (UUID PK +
  `created_at`/`updated_at`), mixed into every model for consistency.
- 9 ORM models, matching the ER diagram in section 3 exactly:
  `User`, `Skill`, `CandidateSkill`, `Question` (self-referencing for
  follow-ups), `InterviewSession`, `InterviewQuestion`, `Answer`,
  `Evaluation`, `InterviewResult`.
- `backend/app/models/__init__.py` — imports every model so
  `Base.metadata` is complete for Alembic autogenerate.
- Alembic wired up (`alembic.ini`, `alembic/env.py`, `script.py.mako`) —
  `env.py` reads `DATABASE_URL` from the app's own `Settings`, so
  migrations always target the same DB the app would connect to.
- `alembic/versions/0001_initial_schema.py` — hand-written, complete
  initial migration: creates all 8 Postgres enum types once each, then all
  9 tables with correct FKs, `ON DELETE` behavior, indexes, and unique
  constraints. Includes a full `downgrade()`.
- `backend/app/utils/seed_skills.py` — idempotent seed for the
  Skill taxonomy from section 4 (Java, Python, SQL, Machine Learning, etc.).

**Design decisions worth knowing:**

- **UUID primary keys**, not auto-increment ints — avoids leaking sequential
  IDs (e.g. total interview count) through the API, and makes IDs safe to
  generate client-side later if needed.
- **JSONB for variable-shaped data only**: `expected_concepts`,
  `evaluation_points`, `strengths`, `weaknesses`, `suggestions`,
  `category_scores`, `recommended_topics`, `improvement_plan`. Everything
  that's queried/aggregated directly (category scores on `Evaluation`,
  `overall_score`) stays as real typed columns — JSONB is not used as a
  dumping ground.
- **`ideal_answer` and `evaluation_points` stay DB-internal.** Nothing in
  this phase exposes them; the schema-level enforcement (separate
  `QuestionPublic`/`QuestionInternal` Pydantic models) lands in Phase 4.
- **Enum types are created explicitly, once, with `create_type=False`
  on every column** that uses them — verified below, this avoids a
  duplicate/conflicting `CREATE TYPE` when the same enum backs multiple
  columns or tables in one migration.
- `InterviewQuestion` is a real join entity (not a plain M2M table) because
  it carries its own data: `order_index`, `asked_at`, `skipped` — every
  `Answer` and `Evaluation` hangs off it, not off `Question` directly, so
  the same bank question can appear in many sessions independently.

**How this was verified (no live Postgres in this sandbox):**

```bash
# 1. All 9 models import cleanly and register on Base.metadata
python3 -c "from app.models import Base, User, Skill, CandidateSkill, Question, \
InterviewSession, InterviewQuestion, Answer, Evaluation, InterviewResult; \
print(sorted(Base.metadata.tables.keys()))"
# -> ['answers', 'candidate_skills', 'evaluations', 'interview_questions',
#     'interview_results', 'interview_sessions', 'questions', 'skills', 'users']

# 2. Migration compiles
python3 -m py_compile alembic/env.py alembic/versions/0001_initial_schema.py

# 3. Migration renders correct, non-duplicated offline SQL
alembic upgrade head --sql | grep -c "^CREATE TYPE"   # -> 8, exactly one per enum
```

**Running it for real, once you have Postgres up (`docker compose up postgres`):**

```bash
cd backend
alembic upgrade head          # creates all tables
python -m app.utils.seed_skills   # seeds the skill taxonomy
```

To create a new migration later (e.g. in Phase 3 for refresh tokens):

```bash
alembic revision --autogenerate -m "add refresh tokens"
alembic upgrade head
```

---

## 12. Initial Setup Commands

```bash
# 1. Clone / enter project
cd ai-interview-evaluator

# 2. Configure environment
cp .env.example .env
# edit .env: set JWT_SECRET_KEY, POSTGRES_PASSWORD, and ANTHROPIC_API_KEY
# (or OPENAI_API_KEY, or leave both blank to run in local-fallback mode)

# 3a. Run everything via Docker (recommended)
docker compose up --build

# Backend:  http://localhost:8000/api/health
# API docs: http://localhost:8000/api/docs
# Frontend: http://localhost:5173

# --- OR ---

# 3b. Run backend locally without Docker
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn app.main:app --reload

# 3c. Run frontend locally without Docker
cd frontend
npm install
npm run dev
```

Verify Phase 1 is working:

```bash
curl http://localhost:8000/api/health
# {"success":true,"status":"ok","environment":"development"}
```

---

**Say "PHASE 3" to proceed to authentication (register/login/JWT/RBAC).**
