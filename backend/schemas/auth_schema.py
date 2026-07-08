"""
auth_schema.py

Defines Pydantic schemas related to authentication history and risk
score API responses.

These schemas govern what the "Authentication History" page and the
"Risk Score" page in the Streamlit frontend receive from the backend.
As with user_schema.py, these are strictly API-boundary contracts,
separate from the internal MongoDB representations in models/.
"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict


class AuthHistoryResponseSchema(BaseModel):
    """
    Schema for a single authentication history entry returned by the API.

    Fields:
        id (str): MongoDB ObjectId as a string.
        user_id (str): The user this event belongs to.
        username (str): Username at the time of the event.
        event_type (str): "LOGIN_SUCCESS", "LOGIN_FAILED", or "LOGOUT".
        ip_address (Optional[str]): IP address of the request, if captured.
        device_info (Optional[str]): Device/user-agent string, if captured.
        timestamp (datetime): When the event occurred (UTC).
        risk_score (Optional[float]): Placeholder risk value for this
            specific event. Remains null until the AI model is integrated.
    """

    id: str
    user_id: str
    username: str
    event_type: str
    ip_address: Optional[str] = None
    device_info: Optional[str] = None
    timestamp: datetime
    risk_score: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class AuthHistoryListResponseSchema(BaseModel):
    """
    Schema for a paginated list of authentication history entries.

    Fields:
        total (int): Total number of matching history records for the user
            (before pagination is applied) — used by the frontend to
            display "Showing X of Y records" and to calculate page counts.
        records (List[AuthHistoryResponseSchema]): The history entries for
            the current page.
    """

    total: int
    records: List[AuthHistoryResponseSchema]


class RiskScoreResponseSchema(BaseModel):
    """
    Schema for the Risk Score / AI Prediction placeholder API response.

    Fields:
        id (str): MongoDB ObjectId as a string.
        user_id (str): The user this risk record belongs to.
        username (str): Username for display purposes.
        session_id (Optional[str]): Associated login session identifier.
        risk_score (Optional[float]): Numeric risk value (0.0–1.0),
            null until an AI model computes a real value.
        risk_level (str): "UNKNOWN", "LOW", "MEDIUM", or "HIGH".
        ai_prediction (Optional[str]): Raw AI model output, null until
            teammates integrate their model. This directly represents
            Requirement #7 (AI Prediction placeholder).
        model_version (Optional[str]): Which AI model version produced
            this score, null until an AI model exists.
        computed_at (Optional[datetime]): When the score was computed,
            null until a real computation happens.
        created_at (datetime): When this placeholder record was created.
    """

    id: str
    user_id: str
    username: str
    session_id: Optional[str] = None
    risk_score: Optional[float] = None
    risk_level: str = "UNKNOWN"
    ai_prediction: Optional[str] = None
    model_version: Optional[str] = None
    computed_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DashboardSummarySchema(BaseModel):
    """
    Schema for the aggregated summary data shown on the main Dashboard page.

    This bundles several small stats together into one response so the
    Streamlit Dashboard page can render everything with a single API
    call rather than five separate requests.

    Fields:
        username (str): The currently logged-in user's username.
        total_logins (int): Total successful logins recorded for this user.
        failed_login_attempts (int): Total failed login attempts recorded.
        total_alerts (int): Total number of alerts generated for this user.
        unread_alerts (int): Number of alerts not yet marked as read.
        last_login (Optional[datetime]): Timestamp of the most recent
            successful login, if any.
        current_risk_level (str): The user's most recently computed risk
            level ("UNKNOWN" until AI integration is complete).
        latest_ai_prediction (Optional[str]): Most recent AI prediction
            output, null until AI model is integrated.
    """

    username: str
    total_logins: int
    failed_login_attempts: int
    total_alerts: int
    unread_alerts: int
    last_login: Optional[datetime] = None
    current_risk_level: str = "UNKNOWN"
    latest_ai_prediction: Optional[str] = None