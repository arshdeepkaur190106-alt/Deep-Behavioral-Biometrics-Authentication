"""
hashing.py

Handles secure password hashing and verification for the Deep Behavioral
Biometrics Authentication Platform.

Uses passlib's bcrypt scheme, which is the industry-standard algorithm for
password hashing. Bcrypt automatically incorporates a random salt into
every hash, so two identical passwords will produce different hash strings,
and it is deliberately slow (configurable "work factor") to resist
brute-force attacks.

This module never stores or logs plaintext passwords anywhere. Only the
resulting hash is ever persisted to the database.
"""

from passlib.context import CryptContext

# ---------------------------------------------------------------------------
# Password hashing context
# ---------------------------------------------------------------------------
# CryptContext manages the hashing scheme(s) used across the application.
# Specifying schemes=["bcrypt"] means bcrypt is used for all new hashes.
# "deprecated=auto" tells passlib to automatically flag old/deprecated
# hash formats if the scheme list changes in the future (useful if the
# team decides to migrate hashing algorithms later).
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """
    Hashes a plaintext password using bcrypt.

    Args:
        plain_password (str): The raw password provided by the user
            during registration.

    Returns:
        str: A bcrypt hash string (includes algorithm identifier, salt,
             and hash — all encoded together in one string) that is
             safe to store in the database.
    """
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plaintext password against a previously stored bcrypt hash.

    Args:
        plain_password (str): The raw password provided by the user
            during login.
        hashed_password (str): The bcrypt hash retrieved from the
            database for that user.

    Returns:
        bool: True if the password matches the hash, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)