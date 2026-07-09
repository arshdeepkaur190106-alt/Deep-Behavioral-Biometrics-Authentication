"""
alert_model.py

Defines the internal data representation of an "Alert" as stored in the
MongoDB `alerts` collection.

Alerts represent security-relevant notifications shown to a user (or
admin) — for example, "New login from an unrecognized device" or
"Multiple failed login attempts detected." Right now, alerts are created
using simple rule-based logic (e.g. threshold on failed login attempts),
NOT by any AI/ML model. This model includes a placeholder field so that,
once your teammates' behavioral biometrics model is integrated, it can
also generate alerts (e.g. "Unusual typing pattern detected") using the
exact same storage structure, no schema changes required.
"""

from datetime import datetime, timezone
from typing import Optional


class AlertModel:
    """
    Represents a single alert document as stored in MongoDB.

    Fields:
        id (Optional[str]): MongoDB ObjectId as a string.
        user_id (str): The '_id' (as string) of the user this alert
            belongs to.
        username (str): Denormalized username for easy display without
            an extra lookup query.
        alert_type (str): Category of alert, e.g. "MULTIPLE_FAILED_LOGINS",
            "NEW_DEVICE_LOGIN", "AI_ANOMALY_DETECTED" (reserved for future
            use by the AI model).
        message (str): Human-readable description of the alert shown in
            the frontend Alerts page.
        severity (str): One of "LOW", "MEDIUM", "HIGH" — indicates how
            serious the alert is, used for color-coding in the UI.
        is_read (bool): Whether the user has acknowledged/viewed this
            alert yet. Defaults to False (unread) when created.
        created_at (datetime): UTC timestamp of when the alert was generated.
        source (str): Indicates what generated the alert — "RULE_ENGINE"
            for the simple logic built in this project, or "AI_MODEL"
            reserved for future use by teammates. Defaults to
            "RULE_ENGINE" since no AI exists yet.
    """

    def __init__(
        self,
        user_id: str,
        username: str,
        alert_type: str,
        message: str,
        severity: str = "MEDIUM",
        id: Optional[str] = None,
        is_read: bool = False,
        created_at: Optional[datetime] = None,
        source: str = "RULE_ENGINE",
    ):
        self.id = id
        self.user_id = user_id
        self.username = username
        self.alert_type = alert_type
        self.message = message
        self.severity = severity
        self.is_read = is_read
        self.created_at = created_at or datetime.now(timezone.utc)
        self.source = source

    def to_mongo_dict(self) -> dict:
        """
        Converts this AlertModel instance into a plain dictionary suitable
        for insertion into MongoDB via Motor.

        Returns:
            dict: A MongoDB-ready representation of the alert.
        """
        return {
            "user_id": self.user_id,
            "username": self.username,
            "alert_type": self.alert_type,
            "message": self.message,
            "severity": self.severity,
            "is_read": self.is_read,
            "created_at": self.created_at,
            "source": self.source,
        }

    @staticmethod
    def from_mongo_document(document: dict) -> "AlertModel":
        """
        Reconstructs an AlertModel instance from a raw MongoDB document
        (as returned by a Motor find/find_one query).

        Args:
            document (dict): The raw document retrieved from MongoDB,
                including the '_id' field.

        Returns:
            AlertModel: A populated AlertModel instance.
        """
        return AlertModel(
            id=str(document.get("_id")),
            user_id=document.get("user_id"),
            username=document.get("username"),
            alert_type=document.get("alert_type"),
            message=document.get("message"),
            severity=document.get("severity", "MEDIUM"),
            is_read=document.get("is_read", False),
            created_at=document.get("created_at"),
            source=document.get("source", "RULE_ENGINE"),
        )