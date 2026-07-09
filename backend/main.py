"""
main.py

Entry point for the Deep Behavioral Biometrics Authentication Platform
backend. This file creates the FastAPI application instance, configures
CORS so the Streamlit frontend can communicate with it, registers all
feature routers (auth, dashboard, history, alerts, risk), and wires up
MongoDB connection lifecycle events.

Run this application with:
    uvicorn backend.main:app --reload

The interactive API documentation will then be available at:
    http://localhost:8000/docs
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.database import connect_to_mongo, close_mongo_connection, create_indexes

from backend.routes import auth_routes
from backend.routes import dashboard_routes
from backend.routes import history_routes
from backend.routes import alert_routes
from backend.routes import risk_routes
from backend.routes import behavior_routes

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages application startup and shutdown events using FastAPI's
    recommended 'lifespan' context manager pattern (replaces the older
    @app.on_event("startup") / @app.on_event("shutdown") decorators).

    On startup:
        - Verifies the MongoDB connection is reachable.
        - Ensures required indexes exist (unique username/email,
          compound indexes for history/alerts queries).

    On shutdown:
        - Cleanly closes the MongoDB client connection.
    """
    # --- Startup ---
    await connect_to_mongo()
    await create_indexes()

    yield  # Application runs while suspended here

    # --- Shutdown ---
    await close_mongo_connection()


# ---------------------------------------------------------------------------
# FastAPI application instance
# ---------------------------------------------------------------------------
app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Backend infrastructure for the Deep Behavioral Biometrics "
        "Authentication Platform. Provides user registration, login "
        "authentication, authentication history, alerts, and placeholder "
        "endpoints for risk scoring and AI-driven behavioral prediction "
        "(to be integrated separately by the AI/ML team)."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS configuration
# ---------------------------------------------------------------------------
# Allows the Streamlit frontend (running on a different origin/port) to
# make requests to this API. Without this, browsers would block the
# frontend's requests due to the same-origin policy.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Router registration
# ---------------------------------------------------------------------------
# Each router already defines its own prefix (e.g. "/auth", "/dashboard")
# and tags (used to group endpoints in the /docs UI), so we only need to
# include them here.
app.include_router(auth_routes.router)
app.include_router(dashboard_routes.router)
app.include_router(history_routes.router)
app.include_router(alert_routes.router)
app.include_router(risk_routes.router)
app.include_router(behavior_routes.router)
# ---------------------------------------------------------------------------
# Root / health-check endpoint
# ---------------------------------------------------------------------------
@app.get("/", tags=["Health Check"], summary="API health check")
async def root():
    """
    Simple health-check endpoint confirming the API is running.

    Useful for:
        - Quickly verifying the backend started correctly during development.
        - The Streamlit frontend to check backend availability before
          attempting authenticated requests.
        - Deployment platforms (e.g. Docker healthchecks, uptime monitors)
          to verify the service is alive.

    Returns:
        dict: A simple status message and the application name.
    """
    return {
        "status": "online",
        "application": settings.APP_NAME,
        "message": "Deep Behavioral Biometrics Authentication Platform API is running.",
    }