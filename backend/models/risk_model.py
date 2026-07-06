"""
risk_model.py

Defines the internal data representation of a "Risk Score" record as
stored in the MongoDB `risk_scores` collection.

IMPORTANT: This file does NOT contain any AI, machine learning, CNN, or
LSTM logic. It is purely a data storage structure — a placeholder — that
your teammates will populate once their behavioral biometrics model is
ready. Right now, risk score values default to None/placeholder status,
and nothing in this codebase computes a real score.

The purpose of defining this structure now (rather than waiting for the
AI model) is so the frontend (Dashboard, Risk Score page, Graphs) has a
stable, well-defined data contract to build against today. When the AI
model is integrated, it only needs to INSERT/UPDATE documents matching
this exact structure — no frontend or API contract changes required.
"""

from datetime import datetime, timezone
from typing import Optional


class RiskScoreModel:
    """
    Represents a single risk score record as stored in MongoDB.

    Fields:
        id (Optional[str]): MongoDB ObjectId as a string.
        user_id (str): The '_id' (as string) of the user this risk score
            belongs to.
        username (str): Denormalized username for easy display.
        session_id (Optional[str]): Identifier linking this risk score to
            a specific login session, if applicable.
        risk_score (Optional[float]): Numeric risk value, typically
            expected to range from 0.0 (no risk) to 1.0 (high risk) once
            the AI model is integrated. Defaults to None to explicitly
            represent "not yet computed."
        risk_level (str): Human-readable category derived from risk_score,
            e.g. "UNKNOWN", "LOW", "MEDIUM", "HIGH". Defaults to
            "UNKNOWN" since no model exists yet to compute a real value.
        ai_prediction (Optional[str]): Placeholder field reserved for the
            AI model's raw prediction/output (e.g. "GENUINE_USER" or
            "IMPOSTER_DETECTED"). Defaults to None — Requirement #7
            (AI Prediction placeholder) is represented directly by this
            field remaining empty until teammates implement the model.
        model_version (Optional[str]): Placeholder to record which
            version of the AI model produced this score, useful for
            tracking model performance/changes over time once it exists.
        computed_at (Optional[datetime]): Timestamp of when the score was
            computed. None until an actual computation happens.
        created_at (datetime): UTC timestamp of when this placeholder
            record was created.
    """

    def __init__(
        self,
        user_id: str,
        username: str,
        id: Optional[str] = None,
        session_id: Optional[str] = None,
        risk_score: Optional[float] = None,
        risk_level: str = "UNKNOWN",
        ai_prediction: Optional[str] = None,
        model_version: Optional[str] = None,
        computed_at: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
    ):
        self.id = id
        self.user_id = user_id
        self.username = username
        self.session_id = session_id
        self.risk_score = risk_score
        self.risk_level = risk_level
        self.ai_prediction = ai_prediction
        self.model_version = model_version
        self.computed_at = computed_at
        self.created_at = created_at or datetime.now(timezone.utc)

    def to_mongo_dict(self) -> dict:
        """
        Converts this RiskScoreModel instance into a plain dictionary
        suitable for insertion into MongoDB via Motor.

        Returns:
            dict: A MongoDB-ready representation of the risk score record.
        """
        return {
            "user_id": self.user_id,
            "username": self.username,
            "session_id": self.session_id,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "ai_prediction": self.ai_prediction,
            "model_version": self.model_version,
            "computed_at": self.computed_at,
            "created_at": self.created_at,
        }

    @staticmethod
    def from_mongo_document(document: dict) -> "RiskScoreModel":
        """
        Reconstructs a RiskScoreModel instance from a raw MongoDB
        document (as returned by a Motor find/find_one query).

        Args:
            document (dict): The raw document retrieved from MongoDB,
                including the '_id' field.

        Returns:
            RiskScoreModel: A populated RiskScoreModel instance.
        """
        return RiskScoreModel(
            id=str(document.get("_id")),
            user_id=document.get("user_id"),
            username=document.get("username"),
            session_id=document.get("session_id"),
            risk_score=document.get("risk_score"),
            risk_level=document.get("risk_level", "UNKNOWN"),
            ai_prediction=document.get("ai_prediction"),
            model_version=document.get("model_version"),
            computed_at=document.get("computed_at"),
            created_at=document.get("created_at"),
        )