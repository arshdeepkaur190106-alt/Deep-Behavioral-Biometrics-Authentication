"""
dashboard_routes.py

Implements the Dashboard summary endpoint (Requirement #3: Dashboard).

Aggregates several statistics about the currently authenticated user into
a single response, so the Streamlit Dashboard page can render everything
(login counts, alert counts, last login time, current risk level, latest
AI prediction) with one API call instead of many.

No AI/ML computation happens here. "current_risk_level" and
"latest_ai_prediction" are read directly from the risk_scores collection
as placeholders — they simply reflect whatever (if anything) has been
stored there, which will be nothing until teammates integrate their model.
"""

from fastapi import APIRouter, Depends

from backend.database import (
    auth_history_collection,
    alerts_collection,
    risk_scores_collection,
)

from backend.models.user_model import UserModel
from backend.models.schemas.auth_schema import DashboardSummarySchema
from backend.models.schemas.routes.auth_routes import (
    get_current_user,
    EVENT_LOGIN_SUCCESS,
    EVENT_LOGIN_FAILED,
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "",
    response_model=DashboardSummarySchema,
    summary="Get aggregated dashboard summary for the current user",
)
async def get_dashboard_summary(current_user: UserModel = Depends(get_current_user)):
    """
    Returns an aggregated summary of the current user's account activity.

    Computes, via MongoDB queries scoped to this user only:
        - Total successful logins.
        - Total failed login attempts.
        - Total alerts generated.
        - Number of unread alerts.
        - Timestamp of the most recent successful login.
        - Most recently computed risk level (placeholder, "UNKNOWN" until
          AI integration).
        - Most recent AI prediction (placeholder, null until AI integration).

    Args:
        current_user (UserModel): Injected by the get_current_user
            dependency; represents the authenticated user making the
            request (extracted from their JWT).

    Returns:
        DashboardSummarySchema: The aggregated dashboard data.
    """
    user_id = current_user.id

    # --- Login statistics ---
    total_logins = await auth_history_collection.count_documents(
        {"user_id": user_id, "event_type": EVENT_LOGIN_SUCCESS}
    )
    failed_login_attempts = await auth_history_collection.count_documents(
        {"user_id": user_id, "event_type": EVENT_LOGIN_FAILED}
    )

    # --- Most recent successful login timestamp ---
    last_login_document = await auth_history_collection.find_one(
        {"user_id": user_id, "event_type": EVENT_LOGIN_SUCCESS},
        sort=[("timestamp", -1)],
    )
    last_login = last_login_document["timestamp"] if last_login_document else None

    # --- Alert statistics ---
    total_alerts = await alerts_collection.count_documents({"user_id": user_id})
    unread_alerts = await alerts_collection.count_documents(
        {"user_id": user_id, "is_read": False}
    )

    # --- Risk / AI Prediction placeholders ---
    # Fetch the most recently created risk score record for this user, if
    # any exists. Until the AI model is integrated, no such records will
    # exist, so these will simply remain at their default "unknown" state.
    latest_risk_document = await risk_scores_collection.find_one(
        {"user_id": user_id},
        sort=[("created_at", -1)],
    )

    if latest_risk_document is not None:
        current_risk_level = latest_risk_document.get("risk_level", "UNKNOWN")
        latest_ai_prediction = latest_risk_document.get("ai_prediction")
    else:
        current_risk_level = "UNKNOWN"
        latest_ai_prediction = None

    return DashboardSummarySchema(
        username=current_user.username,
        total_logins=total_logins,
        failed_login_attempts=failed_login_attempts,
        total_alerts=total_alerts,
        unread_alerts=unread_alerts,
        last_login=last_login,
        current_risk_level=current_risk_level,
        latest_ai_prediction=latest_ai_prediction,
    )