"""
config.py

Centralized configuration module for the Deep Behavioral Biometrics
Authentication Platform backend.

This file reads all sensitive and environment-specific values (database
URI, JWT secret, token expiry, etc.) from environment variables so that
no secrets are hardcoded into the source code. It uses python-dotenv to
load values from a local .env file during development.

Every other backend module imports the `settings` object from this file
instead of reading environment variables directly. This keeps configuration
management in a single place.
"""

import os
from dotenv import load_dotenv

# Load environment variables from a .env file (if present) into the process
# environment. In production (e.g. Docker, cloud hosting), real environment
# variables set by the platform will simply override or supply these.
load_dotenv()


class Settings:
    """
    Settings class that centralizes all configuration values used across
    the backend application.

    Attributes:
        MONGO_URI (str): Connection string for the MongoDB instance.
        DATABASE_NAME (str): Name of the MongoDB database used by this app.
        JWT_SECRET_KEY (str): Secret key used to sign JWT access tokens.
        JWT_ALGORITHM (str): Hashing algorithm used for JWT signing.
        ACCESS_TOKEN_EXPIRE_MINUTES (int): Token validity duration in minutes.
        APP_NAME (str): Human-readable name of the application.
        CORS_ORIGINS (list): List of allowed origins for CORS (frontend URLs).
    """

    # MongoDB connection URI. Defaults to local MongoDB instance for
    # development. In production this should be set via environment
    # variable (e.g. MongoDB Atlas connection string).
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")

    # Name of the database inside MongoDB where all collections
    # (users, auth_history, alerts, risk_scores) will live.
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "behavioral_biometrics_db")

    # Secret key used to sign and verify JWT tokens. MUST be overridden
    # in production via environment variable. A default is provided only
    # so the app doesn't crash during local development.
    JWT_SECRET_KEY: str = os.getenv(
        "JWT_SECRET_KEY", "dev_only_secret_key_change_this_in_production"
    )

    # Algorithm used for JWT signing. HS256 is a standard symmetric
    # signing algorithm suitable for this use case.
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")

    # How long an access token remains valid, in minutes.
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
    )

    # Human-readable application name, used in API metadata and titles.
    APP_NAME: str = os.getenv(
        "APP_NAME", "Deep Behavioral Biometrics Authentication Platform"
    )

    # List of allowed origins for Cross-Origin Resource Sharing.
    # Streamlit typically runs on localhost:8501 during development.
    CORS_ORIGINS: list = os.getenv(
        "CORS_ORIGINS", "http://localhost:8501"
    ).split(",")


# Single shared settings instance imported throughout the backend.
settings = Settings()