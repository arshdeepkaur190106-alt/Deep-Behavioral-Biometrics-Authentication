"""
alert_schema.py

Defines Pydantic schemas that validate data flowing IN and OUT of the API
for the Alerts feature (Requirement #5: Alerts Page).

Covers:
    - The shape of a single alert returned to the frontend.
    - A paginated list wrapper for the Alerts page table/feed.
    - The request body used when a user marks an alert as read.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict


class AlertResponseSchema(BaseModel):
    """
    Schema for a single alert returned by the API.

    Fields:
        id (str): MongoDB ObjectId as a string.
        user_id (str): The user this alert belongs to.
        username (str): Username for display purposes.
        alert_type (str): Category of alert, e.g. "MULTIPLE_FAILED_LOGINS",
            "NEW_DEVICE_LOGIN", or "AI_ANOMALY_DETECTED" (reserved).
        message (str): Human-readable alert description.
        severity (str): "LOW", "MEDIUM", or "HIGH".
        is_read (bool): Whether the user has viewed/acknowledged this alert.
        created_at (datetime): When the alert was generated (UTC).
        source (str): "RULE_ENGINE" (current) or "AI_MODEL" (reserved for
            future use by teammates).
    """

    id: str
    user_id: str
    username: str
    alert_type: str
    message: str
    severity: str
    is_read: bool
    created_at: datetime
    source: str

    model_config = ConfigDict(from_attributes=True)


class AlertListResponseSchema(BaseModel):
    """
    Schema for a paginated list of alerts, used by the Alerts Page.

    Fields:
        total (int): Total number of matching alerts for the user (before
            pagination), used for page-count calculations in the frontend.
        unread_count (int): Number of unread alerts among the total —
            displayed as a badge/counter in the Streamlit sidebar or
            Alerts page header.
        alerts (List[AlertResponseSchema]): The alert entries for the
            current page.
    """

    total: int
    unread_count: int
    alerts: List[AlertResponseSchema]


class MarkAlertReadSchema(BaseModel):
    """
    Schema for the request body when marking one or more alerts as read.

    Fields:
        alert_ids (List[str]): List of MongoDB ObjectId strings (as text)
            identifying which alerts to mark as read. Accepting a list
            (rather than one ID at a time) allows the frontend to support
            a "Mark all as read" button with a single API call.
    """

    alert_ids: List[str] = Field(..., min_length=1)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "alert_ids": ["664f1b2c9e1a2b3c4d5e6f7a", "664f1b2c9e1a2b3c4d5e6f7b"]
            }
        }
    )