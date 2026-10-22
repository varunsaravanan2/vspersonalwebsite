"""Skill endpoints: the spirit board."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Skill
from app.schemas import SkillOut

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("", response_model=list[SkillOut])
def list_skills(db: Session = Depends(get_db)):
    """
    All skills in display order.

    No filtering by type on the server: there will only ever be a few dozen
    skills, so the frontend loads them all once and filters instantly in the
    browser. That avoids a network request every time a filter changes.
    """
    return db.scalars(select(Skill).order_by(Skill.sort_order, Skill.id)).all()
