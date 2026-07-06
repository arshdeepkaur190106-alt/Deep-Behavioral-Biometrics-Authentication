"""
auth_history_model.py

Defines the internal data representation of an "Authentication History"
entry as stored in the MongoDB `auth_history` collection.

Every login attempt (successful or failed) creates one document in this
collection. This becomes the audit trail that the "Authentication History"
page in the frontend will display, and is also the raw data your
teammates' AI model will eventually consume as input features for
behavioral analysis (e.g., typing patterns, login time patterns, device
fingerprints) — though no such analysis happens in this file.
"""

from datetime import datetime, timezone
from typing import Optional


class AuthHistoryModel:
    """
    Represents a single authentication event document as stored in MongoDB.

    Fields:
        id (Optional[str]): MongoDB ObjectId as a string.
        user_id (str): The '_id' (as string) of the user this event
            belongs to. Links this record back to the users collection.
        username (str): Denormalized copy of the username at the time of
            the event, so history can be displayed without an extra join
            query back to the users collection.
        event_type (str): The type of event, e.g. "LOGIN_SUCCESS",
            "LOGIN_FAILED", "LOGOUT".
        ip_address (Optional[str]): IP address the request originated
            from, if available.
        device_info (Optional[str]): User-agent / device string, if
            available. Placeholder field for future behavioral biometrics
            features (e.g. device fingerprinting).
        timestamp (datetime): UTC timestamp of when the event occurred.
        risk_score (Optional[float]): Placeholder field for the AI risk
            score associated with this specific authentication event.
            Remains None until the AI model is integrated by teammates.
    """

    def __init__(
        self,
        user_id: str,
        username: str,
        event_type: str,
        id: Optional[str] = None,
        ip_address: Optional[str] = None,
        device_info: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        risk_score: Optional[float] = None,
    ):
        self.id = id
        self.user_id = user_id
        self.username = username
        self.event_type = event_type
        self.ip_address = ip_address
        self.device_info = device_info
        self.timestamp = timestamp or datetime.now(timezone.utc)
        self.risk_score = risk_score

    def to_mongo_dict(self) -> dict:
        """
        Converts this AuthHistoryModel instance into a plain dictionary
        suitable for insertion into MongoDB via Motor.

        Returns:
            dict: A MongoDB-ready representation of the authentication event.
        """
        return {
            "user_id": self.user_id,
            "username": self.username,
            "event_type": self.event_type,
            "ip_address": self.ip_address,
            "device_info": self.device_info,
            "timestamp": self.timestamp,
            "risk_score": self.risk_score,
        }

    @staticmethod
    def from_mongo_document(document: dict) -> "AuthHistoryModel":
        """
        Reconstructs an AuthHistoryModel instance from a raw MongoDB
        document (as returned by a Motor find/find_one query).

        Args:
            document (dict): The raw document retrieved from MongoDB,
                including the '_id' field.

        Returns:
            AuthHistoryModel: A populated AuthHistoryModel instance.
        """
        return AuthHistoryModel(
            id=str(document.get("_id")),
            user_id=document.get("user_id"),
            username=document.get("username"),
            event_type=document.get("event_type"),
            ip_address=document.get("ip_address"),
            device_info=document.get("device_info"),
            timestamp=document.get("timestamp"),
            risk_score=document.get("risk_score"),
        )