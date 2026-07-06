"""
FastAPI application entrypoint.

This file's only job: create the FastAPI app, make sure DB tables exist,
and mount the routes defined in routes.py. Keep this file thin — actual
endpoint logic lives in routes.py, not here.
"""

from fastapi import FastAPI
from app.database.database import Base, engine
from app.database import models  # noqa: F401 -- import so Base knows about these tables
from app.backend import routes

# Creates all tables defined in models.py if they don't already exist.
# Safe to call every startup -- it's a no-op for tables that already exist.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Autonomous Drone Mission Planner",
    description="Converts natural language inspection requests into structured drone mission pipelines.",
    version="1.0.0",
)

app.include_router(routes.router)


@app.get("/")
def health_check():
    """Simple endpoint to confirm the API is alive."""
    return {"status": "ok", "service": "drone-mission-planner"}