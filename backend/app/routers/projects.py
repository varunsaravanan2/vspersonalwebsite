"""
Project endpoints: the character select grid and each fighter page.

Pattern used by every router in this folder:
- APIRouter groups related routes; main.py mounts it under /api.
- `db: Session = Depends(get_db)` asks FastAPI for a database session.
  FastAPI calls get_db() for each request and closes the session afterwards
  (dependency injection, see db.py).
- `response_model=` tells FastAPI which schema to convert the result into.
  It validates and filters the output and documents it at /docs.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Project
from app.schemas import ProjectDetail, ProjectSummary

# prefix: every route below starts with /projects.
# tags: groups these endpoints under a "projects" heading in the /docs page.
router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=list[ProjectSummary])
def list_projects(db: Session = Depends(get_db)):
    """All projects for the character select grid, in display order."""
    # select(Project) builds:  SELECT ... FROM projects ORDER BY sort_order, id
    # Ordering by id second makes the order stable when two sort_orders tie;
    # without it Postgres may return tied rows in any order.
    stmt = select(Project).order_by(Project.sort_order, Project.id)

    # .scalars() unwraps each result row into a Project object; .all() makes a list.
    # FastAPI then turns each Project into a ProjectSummary (only those fields).
    return db.scalars(stmt).all()


@router.get("/{slug}", response_model=ProjectDetail)
def get_project(slug: str, db: Session = Depends(get_db)):
    """One project by its URL slug, e.g. GET /api/projects/my-project."""
    # The {slug} in the path is passed in as the `slug` argument.
    # SQLAlchemy sends it as a bound parameter, never pasted into the SQL
    # string, which is what prevents SQL injection.
    project = db.scalars(select(Project).where(Project.slug == slug)).first()

    # Return a proper 404 instead of crashing on None (which would be a 500).
    # The frontend uses this to show a "fighter not found" screen.
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project
