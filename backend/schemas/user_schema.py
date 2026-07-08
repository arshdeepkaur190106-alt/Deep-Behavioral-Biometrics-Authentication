"""
user_schema.py

Defines Pydantic schemas that validate data flowing IN and OUT of the
API for user-related operations (registration, login, and user info
responses).

These are distinct from `models/user_model.py`. That file describes how
a user is stored in MongoDB. These schemas describe the "contract" the
API exposes to clients (the Streamlit frontend, or any future client) —
what fields are required in a request body, what types they must be,
and what fields are safe to return in a response (notably, NEVER the
hashed password).

Pydantic automatically validates incoming JSON against these schemas and
returns clean, descriptive 422 errors if the data doesn't match — this
removes the need to write manual validation checks in every route.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserRegisterSchema(BaseModel):
    """
    Schema for incoming registration requests (POST /auth/register).

    Fields:
        username (str): Desired unique username. Length-constrained to
            prevent empty or excessively long values.
        email (EmailStr): Must be a syntactically valid email address.
            Pydantic's EmailStr type performs this validation automatically.
        full_name (str): Display name of the user.
        password (str): Plaintext password submitted by the user. This is
            hashed immediately in the route handler and NEVER stored or
            logged in plaintext form.
    """

    username: str = Field(..., min_length=3, max_length=30)
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=6, max_length=128)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "john_doe",
                "email": "john.doe@example.com",
                "full_name": "John Doe",
                "password": "SecurePass123",
            }
        }
    )


class UserLoginSchema(BaseModel):
    """
    Schema for incoming login requests (POST /auth/login).

    Fields:
        username (str): Username of the account attempting to log in.
        password (str): Plaintext password to verify against the stored hash.
    """

    username: str = Field(..., min_length=3, max_length=30)
    password: str = Field(..., min_length=6, max_length=128)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "john_doe",
                "password": "SecurePass123",
            }
        }
    )


class UserResponseSchema(BaseModel):
    """
    Schema for outgoing user data in API responses.

    Deliberately EXCLUDES 'hashed_password' — this schema defines the
    "safe to expose publicly" view of a user. No route should ever
    manually return a raw dict from the database; always convert through
    this schema first.

    Fields:
        id (str): MongoDB ObjectId as a string.
        username (str): The user's username.
        email (EmailStr): The user's email.
        full_name (str): The user's display name.
        created_at (datetime): When the account was created.
        is_active (bool): Whether the account is currently active.
    """

    id: str
    username: str
    email: EmailStr
    full_name: str
    created_at: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class TokenResponseSchema(BaseModel):
    """
    Schema for the response returned after a successful login.

    Fields:
        access_token (str): The signed JWT the client must include in
            the Authorization header of subsequent requests.
        token_type (str): Always "bearer" — the standard OAuth2/JWT
            convention indicating how the token should be used.
        user (UserResponseSchema): The logged-in user's public profile
            information, returned alongside the token so the frontend
            doesn't need a second request just to display the username.
    """

    access_token: str
    token_type: str = "bearer"
    user: UserResponseSchema