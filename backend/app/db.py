"""
Database connection setup with SQLAlchemy.

Three pieces live here:
1. engine:       manages the actual connections to PostgreSQL
2. SessionLocal: a factory that creates a "session" (one unit of work) per request
3. get_db:       a FastAPI dependency that hands each request its own session
                 and guarantees it gets closed afterwards
"""

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

# The engine keeps a *pool* of open connections and reuses them.
# Opening a new database connection is slow (network + authentication),
# so reusing them makes every request faster.
#
# pool_pre_ping=True: before handing out a pooled connection, check it's still
# alive. Without this, a connection the database closed while idle would cause
# a random error on the next request.
engine = create_engine(settings.database_url, pool_pre_ping=True)

# sessionmaker builds Session objects pre-configured with our engine.
# A Session tracks the objects we load/change and turns them into SQL.
#
# autoflush=False: don't send pending changes to the DB until we explicitly
# commit or flush. That makes it predictable when SQL actually runs.
SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    """
    Parent class for every table model (see models.py).

    SQLAlchemy collects every class that inherits from Base into Base.metadata,
    a full description of the schema. Alembic reads that metadata to figure out
    which tables and columns to create or change.
    """


def get_db() -> Iterator[Session]:
    """
    Give one request its own database session, then always close it.

    Used in routes like:  def list_projects(db: Session = Depends(get_db))
    FastAPI calls this before the route runs (dependency injection).

    Why `yield` instead of `return`? Code after `yield` runs *after* the
    response is sent. The `finally` block means the session is closed even
    if the route raised an error, so connections never leak out of the pool.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
