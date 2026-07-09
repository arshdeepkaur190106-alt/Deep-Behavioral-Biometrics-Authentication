"""
behavior_routes.py

Receives behavioral biometric data (keystroke/mouse/scroll metrics) from
the frontend, runs it through the trained ML model, and persists the
result into risk_scores_collection so that GET /risk/latest and
GET /risk/history (risk_routes.py) return real data instead of the
"UNKNOWN" placeholder.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from ml.predict import predict_user
from backend.database import risk_scores_collection
from backend.models.user_model import UserModel
from backend.models.risk_model import RiskScoreModel
from backend.routes.auth_routes import get_current_user

router = APIRouter(prefix="/api", tags=["Behavior"])


def _risk_level_from_score(risk_score: float) -> str:
    """Converts a 0-100 risk_score into a human-readable risk level."""
    if risk_score < 33:
        return "LOW"
    elif risk_score < 66:
        return "MEDIUM"
    else:
        return "HIGH"


@router.post("/behavior")
async def receive_behavior(
    payload: dict,
    current_user: UserModel = Depends(get_current_user),
):
    """
    Receives raw behavioral feature data, runs the trained model,
    saves a real RiskScoreModel record to MongoDB, and returns the
    prediction result.
    """
    result = predict_user(payload)

    ai_prediction_label = "GENUINE_USER" if result["prediction"] == 1 else "IMPOSTER_DETECTED"
    risk_level = _risk_level_from_score(result["risk_score"])

    risk_record = RiskScoreModel(
        user_id=current_user.id,
        username=current_user.username,
        risk_score=result["risk_score"],
        risk_level=risk_level,
        ai_prediction=ai_prediction_label,
        model_version="v1",
        computed_at=datetime.now(timezone.utc),
    )

    await risk_scores_collection.insert_one(risk_record.to_mongo_dict())

    return {
        "prediction": result["prediction"],
        "confidence": result["confidence"],
        "risk_score": result["risk_score"],
        "risk_level": risk_level,
        "ai_prediction": ai_prediction_label,
    }