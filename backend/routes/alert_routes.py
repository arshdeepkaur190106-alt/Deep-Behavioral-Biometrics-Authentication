"""
alert_routes.py

Implements the Alerts endpoints (Requirement #5: Alerts Page).

Provides:
    - GET  /alerts        : Paginated list of the current user's alerts.
    - POST /alerts/read   : Mark one or more alerts as read.

Alerts themselves are currently only created by rule-based logic inside
auth_routes.py (e.g. repeated failed logins). This file is purely
responsible for reading and updating existing alert records — it does
not generate new alerts itself.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException, status
from bson import ObjectId
from bson.errors import InvalidId

from backend.database import alerts_collection
from backend.models.user_model import UserModel
from backend.models.alert_model import AlertModel
from backend.schemas.alert_schema import (
    AlertResponseSchema,
    AlertListResponseSchema,
    MarkAlertReadSchema,
)
from backend.routes.auth_routes import get_current_user

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get(
    "",
    response_model=AlertListResponseSchema,
    summary="Get the current user's alerts (paginated)",
)
async def get_alerts(
    current_user: UserModel = Depends(get_current_user),
    page: int = Query(1, ge=1, description="Page number, starting at 1."),
    page_size: int = Query(10, ge=1, le=100, description="Number of records per page (max 100)."),
    severity: Optional[str] = Query(
        None, description="Optional filter: 'LOW', 'MEDIUM', or 'HIGH'."
    ),
    unread_only: bool = Query(False, description="If true, return only unread alerts."),
):
    """
    Retrieves a paginated list of alerts belonging to the currently
    authenticated user, most recent first.
    """
    query_filter = {"user_id": current_user.id}

    if severity is not None:
        query_filter["severity"] = severity

    if unread_only:
        query_filter["is_read"] = False

    total = await alerts_collection.count_documents(query_filter)

    unread_count = await alerts_collection.count_documents(
        {"user_id": current_user.id, "is_read": False}
    )

    skip_count = (page - 1) * page_size

    cursor = (
        alerts_collection.find(query_filter)
        .sort("created_at", -1)
        .skip(skip_count)
        .limit(page_size)
    )

    raw_documents = await cursor.to_list(length=page_size)

    alerts = [
        AlertResponseSchema.model_validate(
            AlertModel.from_mongo_document(doc)
        )
        for doc in raw_documents
    ]

    return AlertListResponseSchema(
        total=total,
        unread_count=unread_count,
        alerts=alerts,
    )


@router.post(
    "/read",
    status_code=status.HTTP_200_OK,
    summary="Mark one or more alerts as read",
)
async def mark_alerts_as_read(
    payload: MarkAlertReadSchema,
    current_user: UserModel = Depends(get_current_user),
):
    """
    Marks the specified alerts as read (is_read = True), scoped to the
    currently authenticated user only.
    """
    object_ids = []
    for alert_id in payload.alert_ids:
        try:
            object_ids.append(ObjectId(alert_id))
        except InvalidId:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"'{alert_id}' is not a valid alert ID.",
            )

    update_result = await alerts_collection.update_many(
        {
            "_id": {"$in": object_ids},
            "user_id": current_user.id,
        },
        {"$set": {"is_read": True}},
    )

    return {
        "message": "Alerts updated successfully.",
        "matched_count": update_result.matched_count,
        "modified_count": update_result.modified_count,
    }