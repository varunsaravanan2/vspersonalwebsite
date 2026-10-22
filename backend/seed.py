"""
Seed script: fills the database with my real portfolio content.

Run from backend/ (with the database running and migrations applied):
    .venv/bin/python seed.py

Why a seed script instead of typing rows into the database by hand?
- The content lives in version control, so I can see what changed and when.
- Any fresh database (a teammate's laptop, a new AWS database) gets the same
  content with one command.
- Until the admin page exists, this file IS the admin page: edit the lists
  below, run the script again, and the site updates.

It's safe to run repeatedly (idempotent): each run replaces the content
tables with exactly what's listed here, so nothing gets duplicated.
The `messages` table is never touched, so real contact messages are kept.

Anything marked TODO is a placeholder to replace with real info.
"""

from datetime import date

from sqlalchemy import delete

from app.db import SessionLocal
from app.models import (
    Experience,
    ExperienceKind,
    Project,
    Skill,
    SkillRank,
    SkillType,
)

# ---------------------------------------------------------------------------
# Projects ("fighters"). Locked "?" slots on the grid are added by the
# frontend, so only real projects go here.
# ---------------------------------------------------------------------------
PROJECTS = [
    Project(
        slug="smash-portfolio",
        name="Smash Portfolio",
        tagline="This site: a portfolio styled after Smash Ultimate's menus.",
        stack=["React", "TypeScript", "Python", "FastAPI", "PostgreSQL", "AWS"],
        # Each move = one feature. "input" is the Smash-style label shown on the
        # fighter page; "Final Smash" is reserved for the most impressive part.
        moves=[
            {
                "input": "Neutral B",
                "name": "Live content API",
                "description": "Projects, skills, and experience load from a "
                "FastAPI backend backed by PostgreSQL.",
            },
            {
                "input": "Side B",
                "name": "Spam-proof contact form",
                "description": "Validated with Pydantic and filtered with a "
                "hidden honeypot field that catches bots.",
            },
            {
                "input": "Up B",
                "name": "Versioned database",
                "description": "Every schema change is an Alembic migration, "
                "reviewed and reversible.",
            },
            {
                "input": "Final Smash",
                "name": "Deployed on AWS",
                "description": "React on S3 + CloudFront, the API on Lambda, "
                "Postgres on RDS.",  # TODO: true once deployed
            },
        ],
        # Values from 0-100, drawn as stat bars. They're my own rough
        # self-assessment, not measurements.
        stats={"complexity": 60, "polish": 50, "fun": 90},
        repo_url=None,  # TODO: GitHub link once the repo is pushed
        demo_url=None,  # TODO: the live URL once deployed
        sort_order=1,
    ),
    # TODO: add more projects here, copying the shape above.
]

# ---------------------------------------------------------------------------
# Skills ("spirits"). Ranks are honest: everything starts at novice and gets
# bumped up as I actually use it more.
# type: attack = languages, shield = frameworks, grab = data, neutral = tools
# ---------------------------------------------------------------------------
SKILLS = [
    Skill(name="Python", type=SkillType.attack, rank=SkillRank.novice, sort_order=1),
    Skill(name="TypeScript", type=SkillType.attack, rank=SkillRank.novice, sort_order=2),
    Skill(name="React", type=SkillType.shield, rank=SkillRank.novice, sort_order=3),
    Skill(name="SQL", type=SkillType.grab, rank=SkillRank.novice, sort_order=4),
]

# ---------------------------------------------------------------------------
# Experience ("stages"). School is the first stage; jobs and clubs get
# added here as they happen.
# ---------------------------------------------------------------------------
EXPERIENCE = [
    Experience(
        org="TODO: Your University",
        role="TODO: Your major",
        kind=ExperienceKind.school,
        start_date=date(2024, 8, 1),  # TODO: real start date
        end_date=None,                # None = "present"
        bullets=[],                   # TODO: relevant courses, clubs, honors
    ),
]


def seed() -> None:
    # `with SessionLocal() as db` closes the session automatically at the end.
    # `with db.begin()` wraps everything in ONE transaction: if any insert
    # fails, every delete is rolled back too, so the site is never left half-empty.
    with SessionLocal() as db, db.begin():
        # Clear the content tables first so re-running doesn't create duplicates.
        for model in (Project, Skill, Experience):
            db.execute(delete(model))

        db.add_all(PROJECTS + SKILLS + EXPERIENCE)

    print(
        f"Seeded {len(PROJECTS)} project(s), {len(SKILLS)} skill(s), "
        f"{len(EXPERIENCE)} experience entr{'y' if len(EXPERIENCE) == 1 else 'ies'}."
    )


# Only runs when executed directly (python seed.py), not when imported.
if __name__ == "__main__":
    seed()
