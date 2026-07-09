"""
history_routes.py

Implements the Authentication History endpoint (Requirement #4:
Authentication History).

Provides a paginated, filterable view of a user's own login/logout
history, sourced from the auth_history collection. This is purely a
read/query endpoint — history records themselves are created elsewhere
(in auth_routes.py, at the moment of login/logout).
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query

from backend.database import auth_history_collection
from backend.models.user_model import UserModel
from backend.models.auth_history_model import AuthHistoryModel
from backend.schemas.auth_schema import (
    AuthHistoryResponseSchema,
    AuthHistoryListResponseSchema,
)
from backend.routes.auth_routes import get_current_user

router = APIRouter(prefix="/history", tags=["Authentication History"])


@router.get(
    "",
    response_model=AuthHistoryListResponseSchema,
    summary="Get the current user's authentication history (paginated)",
)
async def get_authentication_history(
    current_user: UserModel = Depends(get_current_user),
    page: int = Query(1, ge=1, description="Page number, starting at 1."),
    page_size: int = Query(10, ge=1, le=100, description="Number of records per page (max 100)."),
    event_type: Optional[str] = Query(
        None,
        description="Optional filter: 'LOGIN_SUCCESS', 'LOGIN_FAILED', or 'LOGOUT'.",
    ),
):
    """
    Retrieves a paginated list of authentication history records for the
    currently authenticated user, most recent first.

    Args:
        current_user (UserModel): The authenticated user, injected via
            the get_current_user dependency.
        page (int): 1-indexed page number for pagination.
        page_size (int): Number of records to return per page (capped at
            100 to prevent excessively large responses).
        event_type (Optional[str]): If provided, filters results to only
            this event type (e.g. only failed logins).

    Returns:
        AuthHistoryListResponseSchema: The total matching record count and
            the requested page of records.
    """
    query_filter = {"user_id": current_user.id}

    if event_type is not None:
        query_filter["event_type"] = event_type

    total = await auth_history_collection.count_documents(query_filter)

    skip_count = (page - 1) * page_size

    cursor = (
        auth_history_collection.find(query_filter)
        .sort("timestamp", -1)
        .skip(skip_count)
        .limit(page_size)
    )

    raw_documents = await cursor.to_list(length=page_size)

    records = [
        AuthHistoryResponseSchema.model_validate(
            AuthHistoryModel.from_mongo_document(doc)
        )
        for doc in raw_documents
    ]

    return AuthHistoryListResponseSchema(total=total, records=records)