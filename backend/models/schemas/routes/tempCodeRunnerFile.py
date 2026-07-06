"""
risk_routes.py

Implements the Risk Score and AI Prediction placeholder endpoints
(Requirement #6: Risk Score placeholder, Requirement #7: AI Prediction
placeholder).

*** THIS FILE IS THE PRIMARY AI INTEGRATION POINT FOR YOUR TEAMMATES. ***

Currently, this file:
    - Does NOT contain any CNN, LSTM, TensorFlow, PyTorch, or any
      prediction/inference logic whatsoever.
    - Only reads/writes placeholder records in the risk_scores collection,
      which default to risk_score=None, risk_level="UNKNOWN", and
      ai_prediction=None.
    - Exposes a GET endpoint so the frontend's Risk Score page and Graphs
      (Requirement #8) have a stable, real API to call against today,
      even though the underlying values are placeholders.

WHEN THE AI MODEL IS READY, your teammates will likely:
    1. Add a new function (e.g. `compute_behavioral_risk_score(...)`)
       that runs their CNN/LSTM model on session data and returns a
       real risk_score, risk_level, and ai_prediction.
    2. Call that function from a new POST endpoint here (e.g.
       POST /risk/compute) or from a background task triggered at login.
    3. Insert/update RiskScoreModel records with real values using the
       exact same `risk_scores_collection` and `RiskScoreModel` structure
       already defined in this codebase.

No changes to the frontend or to this file's GET endpoint will be
required for that integration to "just work" — the frontend already
renders whatever is in the database, placeholder or real.
"""

from typing import Optional, List

from fastapi import APIRouter, Depends, Query

from backend.database import risk_scores_collection
from backend.models.user_model import UserModel
from backend.models.risk_model import RiskScoreModel
from backend.schemas.auth_schema import RiskScoreResponseSchema
from backend.routes.auth_routes import get_current_user

router = APIRouter(prefix="/risk", tags=["Risk Score & AI Prediction (Placeholder)"])


@router.get(
    "/latest",
    response_model=RiskScoreResponseSchema,
    summary="Get the current user's most recent risk score / AI prediction",
)
async def get_latest_risk_score(current_user: UserModel = Depends(get_current_user)):
    """
    Retrieves the most recently created risk score record for the
    currently authenticated user.

    If no risk score record exists yet for this user (which will always
    be true until the AI model is integrated and starts writing records),
    a fully-formed placeholder record is returned instead, with
    risk_score=None, risk_level="UNKNOWN", and ai_prediction=None. This
    record is NOT saved to the database — it exists only in the response,
    so the frontend always has something well-formed to render even
    before any real record exists.

    Args:
        current_user (UserModel): The authenticated user.

    Returns:
        RiskScoreResponseSchema: The latest risk score record, or a
            transient placeholder if none exists yet.
    """
    latest_document = await risk_scores_collection.find_one(
        {"user_id": current_user.id},
        sort=[("created_at", -1)],
    )

    if latest_document is not None:
        risk_record = RiskScoreModel.from_mongo_document(latest_document)
        return RiskScoreResponseSchema.model_validate(risk_record)

    # No record exists in the database yet — construct a transient,
    # in-memory placeholder so the API contract remains stable and the
    # frontend never has to special-case a "404 / no data" response.
    placeholder = RiskScoreModel(
        user_id=current_user.id,
        username=current_user.username,
        id="placeholder",
        risk_score=None,
        risk_level="UNKNOWN",
        ai_prediction=None,
        model_version=None,
        computed_at=None,
    )
    return RiskScoreResponseSchema.model_validate(placeholder)


@router.get(
    "/history",
    response_model=List[RiskScoreResponseSchema],
    summary="Get risk score history for graphing (Requirement #8: Graphs)",
)
async def get_risk_score_history(
    current_user: UserModel = Depends(get_current_user),
    limit: int = Query(30, ge=1, le=200, description="Max number of records to return."),
):
    """
    Retrieves a chronological list of the current user's risk score
    records, intended to feed the Graphs page (Requirement #8) — e.g.
    plotting risk score trend over time.

    Returns an empty list until the AI model begins writing real
    records into risk_scores_collection. The frontend's graph component
    should handle an empty list gracefully (e.g. showing a "No data yet"
    message instead of an empty/broken chart).

    Args:
        current_user (UserModel): The authenticated user.
        limit (int): Maximum number of most-recent records to return.

    Returns:
        List[RiskScoreResponseSchema]: Risk score records ordered from
            oldest to newest (ready to plot directly on a time-series chart).
    """
    cursor = (
        risk_scores_collection.find({"user_id": current_user.id})
        .sort("created_at", -1)
        .limit(limit)
    )

    raw_documents = await cursor.to_list(length=limit)

    # Reverse so the list is oldest -> newest, which is the natural order
    # expected by time-series charting libraries (e.g. Plotly/Matplotlib
    # x-axis should read left-to-right as time progresses).
    raw_documents.reverse()

    records = [
        RiskScoreResponseSchema.model_validate(
            RiskScoreModel.from_mongo_document(doc)
        )
        for doc in raw_documents
    ]

    return records