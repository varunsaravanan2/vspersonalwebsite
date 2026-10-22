"""
App configuration, read from environment variables.

Why environment variables instead of hard-coding values?
- The same code runs on my laptop and on AWS; only the variables change.
  Locally they come from the .env file. On AWS they come from Lambda's settings.
- Secrets like the database password stay out of the source code and out of git.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Each attribute maps to an environment variable with the same name
    # (case-insensitive). If DATABASE_URL is missing, the app refuses to start
    # with a clear error instead of failing later in a confusing way.
    database_url: str

    # Where the React frontend runs during development (Vite's default port).
    # Used for CORS in main.py: browsers block cross-origin API calls unless
    # the server says that origin is allowed.
    frontend_origin: str = "http://localhost:5173"

    # Tells pydantic-settings to also read variables from a .env file.
    model_config = SettingsConfigDict(env_file=".env")


# One shared instance that the rest of the app imports.
# Created once at startup, so .env is only read once.
settings = Settings()
