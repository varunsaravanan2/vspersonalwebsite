"""
Pydantic schemas: the shape of data going IN to and OUT of the API.

Why separate schemas from the database models in models.py?
- Models describe how data is *stored*; schemas describe what the API *exposes*.
  They overlap, but not completely: e.g. the contact form never lets a visitor
  set `id` or `created_at`, and the projects grid doesn't need every column.
- Incoming data is validated before it touches the database. A bad email or a
  missing field gets an automatic 422 error with a clear message.
- Outgoing data is filtered: only fields listed in the schema are sent, so a
  column added to the table later can't leak out by accident.
- FastAPI reads these classes to generate the interactive docs at /docs,
  and the frontend can generate matching TypeScript types from them.

Naming: "...Out" = sent by the API (response), "...In" = received (request body).
"""

from datetime import date

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models import ExperienceKind, SkillRank, SkillType


class ORMModel(BaseModel):
    """
    Base class for every response schema.

    from_attributes=True lets Pydantic build a schema straight from a
    SQLAlchemy object by reading its attributes (project.name, project.slug...),
    instead of needing a dict. That's how a route can return a database row
    and FastAPI converts it to JSON.
    """
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Projects ("fighters")
# ---------------------------------------------------------------------------

class Move(BaseModel):
    """
    One feature in a project's "moveset", stored inside the JSONB `moves` column.

    The database stores JSONB as free-form JSON, so it won't stop a typo like
    "inptu". Declaring the shape here means the API still validates it.
    """
    input: str          # the Smash-style label, e.g. "Neutral B" or "Final Smash"
    name: str           # short feature name
    description: str


class ProjectSummary(ORMModel):
    """
    One tile on the character select grid.

    Deliberately small: the grid loads every project at once, so it skips
    the moveset and stats. Those are only fetched on the fighter page.
    Sending less data keeps the grid fast.
    """
    slug: str
    name: str
    tagline: str
    stack: list[str]
    portrait_url: str | None


class ProjectDetail(ProjectSummary):
    """
    Everything for one fighter page. Inherits all ProjectSummary fields
    and adds the rest, so the shared fields are only defined once.
    """
    moves: list[Move]
    # Stat name -> value from 0 to 100, e.g. {"complexity": 60, "impact": 80}
    stats: dict[str, int]
    repo_url: str | None
    demo_url: str | None


# ---------------------------------------------------------------------------
# Skills ("spirits") and experience ("stages")
# ---------------------------------------------------------------------------

class SkillOut(ORMModel):
    # Reusing the enums from models.py means the docs list the exact allowed
    # values, and the frontend can't receive anything outside them.
    name: str
    type: SkillType
    rank: SkillRank


class ExperienceOut(ORMModel):
    org: str
    role: str
    kind: ExperienceKind
    start_date: date
    end_date: date | None   # null = "present"
    bullets: list[str]


# ---------------------------------------------------------------------------
# Contact form ("challenger approaching")
# ---------------------------------------------------------------------------

class MessageIn(BaseModel):
    """
    What the contact form sends. Not an ORMModel: it's built from the request
    body (JSON), not from a database row.

    Field(...) adds limits that FastAPI enforces before my code even runs.
    The max lengths match the column sizes in models.py, so a too-long value
    gets a friendly 422 error instead of a database crash (500).
    """
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr                                   # rejects "not-an-email"
    body: str = Field(min_length=1, max_length=5000)  # cap so nobody can send a novel

    # Honeypot field for spam bots. The real form hides this input with CSS,
    # so humans leave it empty, but bots that auto-fill every field fill it in.
    # The route quietly drops any message where it's filled.
    website: str = ""


class MessageAck(BaseModel):
    """
    The response after submitting the form. Just a confirmation: I don't echo
    the message back or reveal its database ID, since visitors don't need either.
    """
    ok: bool = True
