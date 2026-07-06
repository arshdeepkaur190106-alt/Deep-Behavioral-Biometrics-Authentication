"""
user_model.py

Defines the internal data representation of a "User" as it is stored in
the MongoDB `users` collection.

This is distinct from the request/response schemas (in schemas/user_schema.py)
which validate what comes IN and OUT of the API. This model represents the
"shape of the data at rest" in the database, including internal fields like
the hashed password and timestamps that should never be exposed directly
to API consumers.

MongoDB is schema-less, so this class does not enforce anything at the
database engine level — it exists purely as a Python-side contract so
every part of the codebase agrees on what a "user document" looks like,
and to provide helper methods for converting between MongoDB documents
and Python dictionaries.
"""

from datetime import datetime, timezone
from typing import Optional


class UserModel:
    """
    Represents a single user document as stored in MongoDB.

    Fields:
        id (Optional[str]): MongoDB ObjectId as a string. None until the
            document has been inserted and MongoDB has assigned an _id.
        username (str): Unique username chosen at registration.
        email (str): Unique email address.
        full_name (str): Display name of the user.
        hashed_password (str): Bcrypt hash of the user's password. The
            plaintext password is NEVER stored anywhere.
        created_at (datetime): UTC timestamp of when the account was created.
        is_active (bool): Whether the account is active (allows disabling
            an account without deleting it, e.g. for suspicious activity
            flagged in the future by the AI risk engine).
    """

    def __init__(
        self,
        username: str,
        email: str,
        full_name: str,
        hashed_password: str,
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        is_active: bool = True,
    ):
        self.id = id
        self.username = username
        self.email = email
        self.full_name = full_name
        self.hashed_password = hashed_password
        self.created_at = created_at or datetime.now(timezone.utc)
        self.is_active = is_active

    def to_mongo_dict(self) -> dict:
        """
        Converts this UserModel instance into a plain dictionary suitable
        for insertion into MongoDB via Motor.

        Note: Does NOT include 'id' — MongoDB generates the '_id' field
        automatically upon insertion, so we never pass it in manually
        when creating a new document.

        Returns:
            dict: A MongoDB-ready representation of the user.
        """
        return {
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "hashed_password": self.hashed_password,
            "created_at": self.created_at,
            "is_active": self.is_active,
        }

    @staticmethod
    def from_mongo_document(document: dict) -> "UserModel":
        """
        Reconstructs a UserModel instance from a raw MongoDB document
        (as returned by a Motor find/find_one query).

        Args:
            document (dict): The raw document retrieved from MongoDB,
                including the '_id' field.

        Returns:
            UserModel: A populated UserModel instance.
        """
        return UserModel(
            id=str(document.get("_id")),
            username=document.get("username"),
            email=document.get("email"),
            full_name=document.get("full_name"),
            hashed_password=document.get("hashed_password"),
            created_at=document.get("created_at"),
            is_active=document.get("is_active", True),
        )