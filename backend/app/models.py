"""
Database tables, defined as Python classes (the SQLAlchemy ORM).

Each class = one table. Each `Mapped[...]` attribute = one column.
The Smash theme only lives in the frontend; tables keep plain names
(projects, not fighters) so the code stays readable to anyone.

    projects   -> shown as "fighters" on the character select screen
    skills     -> shown as "spirits" on the spirit board
    experience -> shown as "stages" on stage select
    messages   -> contact form submissions ("challenger approaching")
"""

import enum
from datetime import date, datetime

from sqlalchemy import ARRAY, DateTime, Enum, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


# ---------------------------------------------------------------------------
# Enums: columns that only allow a fixed set of values.
#
# Why enums instead of plain strings? The database itself rejects a typo like
# "atack", so bad data can't sneak in even if it bypasses the API.
# Inheriting from `str` means each value is also a normal string, so it
# serializes to JSON as "attack", not as a Python object.
# ---------------------------------------------------------------------------

class SkillType(str, enum.Enum):
    """Spirit "type" = skill category, shown as the card's type label."""
    attack = "attack"    # programming languages
    shield = "shield"    # frameworks and libraries
    grab = "grab"        # data and databases
    neutral = "neutral"  # cloud, tools, everything else


class SkillRank(str, enum.Enum):
    """Spirit "rank" = honest proficiency level, lowest to highest."""
    novice = "novice"
    advanced = "advanced"
    ace = "ace"
    legend = "legend"


class ExperienceKind(str, enum.Enum):
    """What kind of stage this is, so the UI can label or filter it."""
    school = "school"
    job = "job"
    club = "club"


# native_enum=False stores the value as plain VARCHAR plus a CHECK constraint
# instead of a Postgres ENUM type. Postgres enum types are awkward to change
# later (adding a value needs a special migration); a CHECK constraint is easy.
# create_constraint=True: SQLAlchemy leaves the CHECK off by default, so
# without this the database would accept any string.
def _enum(e: type[enum.Enum]) -> Enum:
    return Enum(e, native_enum=False, length=20, create_constraint=True)


# ---------------------------------------------------------------------------
# Tables
# ---------------------------------------------------------------------------

class Project(Base):
    """A portfolio project, displayed as a "fighter"."""

    __tablename__ = "projects"

    # Primary key: a unique auto-incrementing number for each row.
    id: Mapped[int] = mapped_column(primary_key=True)

    # The URL-friendly name, e.g. "my-project" in /projects/my-project.
    # unique=True: two projects can't share a URL.
    # index=True: lookups by slug (every fighter page) stay fast.
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True)

    name: Mapped[str] = mapped_column(String(120))
    tagline: Mapped[str] = mapped_column(String(200))

    # Postgres supports array columns, e.g. ["JavaScript", "Chrome APIs"].
    # A separate join table would be more "normalized", but a project's stack is
    # just display text, so one array column is simpler and does the job.
    stack: Mapped[list[str]] = mapped_column(ARRAY(String(50)), default=list)

    # JSONB = JSON stored in a binary format that Postgres can index and query.
    # moves: the feature list shown as special moves, e.g.
    #   [{"input": "Neutral B", "name": "Monday check", "description": "..."}]
    # stats: the stat bars, e.g. {"complexity": 60, "impact": 80}
    # Why JSONB? These shapes may change as the design evolves, and JSONB lets
    # me add a new stat without writing a database migration.
    moves: Mapped[list[dict]] = mapped_column(JSONB, default=list)
    stats: Mapped[dict] = mapped_column(JSONB, default=dict)

    # `str | None` makes the column nullable: not every project has a live demo
    # or screenshot yet.
    portrait_url: Mapped[str | None] = mapped_column(String(500))
    repo_url: Mapped[str | None] = mapped_column(String(500))
    demo_url: Mapped[str | None] = mapped_column(String(500))

    # Controls order on the character select grid (lower = earlier),
    # like a fighter number.
    sort_order: Mapped[int] = mapped_column(default=0)


class Skill(Base):
    """A skill, displayed as a "spirit" card."""

    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(60), unique=True)
    type: Mapped[SkillType] = mapped_column(_enum(SkillType))
    rank: Mapped[SkillRank] = mapped_column(_enum(SkillRank), default=SkillRank.novice)
    sort_order: Mapped[int] = mapped_column(default=0)


class Experience(Base):
    """School, a job, or a club, displayed as a "stage"."""

    __tablename__ = "experience"

    id: Mapped[int] = mapped_column(primary_key=True)
    org: Mapped[str] = mapped_column(String(120))   # e.g. the university or company name
    role: Mapped[str] = mapped_column(String(120))  # e.g. "B.S. Computer Science" or "SWE Intern"
    kind: Mapped[ExperienceKind] = mapped_column(_enum(ExperienceKind))
    start_date: Mapped[date]

    # NULL end_date means "present" (still there), so no fake far-future date.
    end_date: Mapped[date | None]

    # A few short bullet points, same idea as on a résumé.
    bullets: Mapped[list[str]] = mapped_column(ARRAY(Text), default=list)


class Message(Base):
    """A contact form submission ("challenger approaching")."""

    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(254))  # 254 = max length of a valid email address
    body: Mapped[str] = mapped_column(Text)

    # server_default=func.now(): Postgres fills in the timestamp itself on insert,
    # so the time comes from the database clock, not whichever server sent it.
    # timezone=True stores it as TIMESTAMPTZ, which avoids time zone mix-ups.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
