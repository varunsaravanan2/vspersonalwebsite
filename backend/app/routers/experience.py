"""Experience endpoints: stage select."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Experience
from app.schemas import ExperienceOut

router = APIRouter(prefix="/experience", tags=["experience"])


@router.get("", response_model=list[ExperienceOut])
def list_experience(db: Session = Depends(get_db)):
    """
    All stages, most recent first, the same order a résumé uses.

    end_date NULL means "present", so those rows should come first.
    Postgres puts NULLs first in descending order by default, but writing
    nulls_first() makes the intent obvious to anyone reading the code.
    Then newest start date first as a tie-breaker.
    """
    stmt = select(Experience).order_by(
        Experience.end_date.desc().nulls_first(),
        Experience.start_date.desc(),
    )
    return db.scalars(stmt).all()
