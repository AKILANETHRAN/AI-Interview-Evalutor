"""
One-off data seed for the `skills` table (section 15: Skill/CandidateSkill).

Run after migrations:
    python -m app.utils.seed_skills

Idempotent — safe to re-run; skips names that already exist.
"""
from app.core.database import SessionLocal
from app.models import Skill

TECHNOLOGY_SKILLS = [
    ("Java", "Language"),
    ("Python", "Language"),
    ("C++", "Language"),
    ("JavaScript", "Language"),
    ("SQL", "Language"),
    ("Machine Learning", "Concept"),
    ("Deep Learning", "Concept"),
    ("Data Structures", "Concept"),
    ("Algorithms", "Concept"),
    ("DBMS", "Concept"),
    ("Computer Networks", "Concept"),
    ("Operating Systems", "Concept"),
]


def seed_skills() -> None:
    db = SessionLocal()
    try:
        existing = {name for (name,) in db.query(Skill.name).all()}
        created = 0
        for name, category in TECHNOLOGY_SKILLS:
            if name in existing:
                continue
            db.add(Skill(name=name, category=category))
            created += 1
        db.commit()
        print(f"Seeded {created} new skill(s); {len(existing)} already present.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_skills()
