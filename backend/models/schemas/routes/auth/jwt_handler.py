"""

jwt_handler.py

Handles creation and verification of JSON Web Tokens (JWT) used for
authenticating API requests in the Deep Behavioral Biometrics
Authentication Platform.

After a user successfully logs in, the backend issues a signed JWT access
token. The Streamlit frontend stores this token (in session state) and
sends it with every subsequent request in the Authorization header. This
module is responsible for both creating that token and validating it on
protected routes.

Uses python-jose, a widely used JWT library compatible with FastAPI's
recommended security patterns.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt

from backend.config import settings


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a signed JWT access token embedding the given payload data.

    Args:
        data (dict): The payload to encode into the token. Typically
            contains at least the user's unique identifier, e.g.
            {"sub": user_id, "username": username}.
        expires_delta (Optional[timedelta]): Custom expiry duration. If
            not provided, falls back to settings.ACCESS_TOKEN_EXPIRE_MINUTES.

    Returns:
        str: An encoded JWT string ready to be sent to the client.
    """
    to_encode = data.copy()

    # Determine token expiration time. Using timezone-aware UTC datetimes
    # avoids subtle bugs related to local server timezones.
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    # Standard JWT claims: "exp" (expiration) and "iat" (issued at) are
    # both included so the token's lifetime is fully self-describing.
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decodes and validates a JWT access token.

    Args:
        token (str): The encoded JWT string received from the client.

    Returns:
        Optional[dict]: The decoded payload dictionary if the token is
            valid and not expired. Returns None if the token is invalid,
            malformed, or expired.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError:
        # Covers expired tokens, invalid signatures, and malformed tokens.
        return None