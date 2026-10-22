"""
The FastAPI application: where everything is wired together.

Run locally (from backend/):
    .venv/bin/uvicorn app.main:app --reload
Then open http://localhost:8000/docs for interactive API docs.

"app.main:app" means: in the module app/main.py, use the variable named `app`.
--reload restarts the server automatically whenever a file is saved.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from app.config import settings
from app.routers import experience, messages, projects, skills

app = FastAPI(
    title="Smash Portfolio API",
    description="Backend for my Smash Ultimate-themed portfolio.",
    version="0.1.0",
)

# --- CORS (Cross-Origin Resource Sharing) ---------------------------------
# During development the React app runs on localhost:5173 and this API on
# localhost:8000. Different ports count as different "origins", and browsers
# block a page from reading responses from another origin unless the server
# explicitly allows it. This middleware adds the headers that allow it.
#
# Only the frontend's origin is allowed (not "*"), so random other websites
# can't call this API from their visitors' browsers.
# In production CloudFront serves the site and /api from the same domain,
# so CORS isn't even needed there.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# --- Routes ----------------------------------------------------------------
# Every router is mounted under /api. In production CloudFront forwards
# /api/* to this app and everything else to the React files in S3,
# so the prefix is what separates the two.
for router in (projects.router, skills.router, experience.router, messages.router):
    app.include_router(router, prefix="/api")


@app.get("/api/health", tags=["health"])
def health():
    """
    A tiny endpoint that just says the app is up. Used to quickly confirm a
    deploy worked, and by monitoring tools that ping the site. It deliberately
    doesn't touch the database, so it stays fast and cheap.
    """
    return {"status": "ok"}


# --- AWS Lambda entry point -------------------------------------------------
# Lambda doesn't run a web server like uvicorn; it calls a function with an
# event (a dict describing the HTTP request). Mangum translates that event into
# a normal request for FastAPI, then translates FastAPI's response back.
# Locally this line does nothing; on Lambda the handler is set to "app.main.handler".
#
# lifespan="off": this app has no startup/shutdown hooks, so skip that step
# for a slightly faster cold start (the first request after Lambda spins up).
handler = Mangum(app, lifespan="off")
