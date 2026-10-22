"""
Alembic's entry point: runs every time you call an `alembic` command.

Its two jobs:
1. Know what the tables *should* look like  -> target_metadata (from models.py)
2. Know which database to change            -> the URL from app/config.py

Common commands (run from backend/):
    alembic revision --autogenerate -m "describe change"   # create a migration
    alembic upgrade head                                   # apply all migrations
    alembic downgrade -1                                   # undo the last one

Why migrations instead of just Base.metadata.create_all()?
create_all() can only create missing tables; it never alters existing ones.
Migrations are versioned scripts, so adding a column later is a reviewed,
repeatable, reversible change that runs the same on my laptop and on AWS.
"""

from logging.config import fileConfig

from sqlalchemy import create_engine, pool

from alembic import context

# Importing app.models registers every table class on Base.metadata.
# Without this import, Alembic would think there are no tables at all.
import app.models  # noqa: F401  (imported for its side effect)
from app.config import settings
from app.db import Base

# Alembic's config object, built from alembic.ini.
config = context.config

# Set up logging from the [loggers] section of alembic.ini,
# so you can see which migrations run.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# The "desired state" of the schema. `--autogenerate` compares this against
# the real database and writes a migration for the differences.
target_metadata = Base.metadata

# One source of truth for the database URL: the same .env value the app uses,
# instead of duplicating it (and the password) in alembic.ini.
DATABASE_URL = settings.database_url


def run_migrations_offline() -> None:
    """
    "Offline" mode: don't connect, just print the SQL (`alembic upgrade head --sql`).
    Useful for reviewing exactly what a migration will do before running it.
    """
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    "Online" mode (the normal one): connect to the database and apply changes.

    NullPool: a migration is a one-off script, so open a single connection and
    close it when done instead of keeping a pool around like the web app does.
    """
    connectable = create_engine(DATABASE_URL, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        # Each migration runs inside a transaction: if any step fails,
        # Postgres rolls the whole thing back instead of leaving a half-changed schema.
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
