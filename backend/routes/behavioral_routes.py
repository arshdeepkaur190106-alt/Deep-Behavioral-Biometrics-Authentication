from fastapi import APIRouter
# from ml.predict import predict_user  # adjust import path once ml/ is merged in

router = APIRouter(prefix="/api", tags=["Behavior"])

# Exact order must match feature_names.pkl — we'll fill this in after Step 1
FEATURE_ORDER = [
    # populated after we see feature_names.pkl output
]

@router.post("/behavior")
async def receive_behavior(payload: dict):
    # Separate metadata from ML features
    session_id = payload.get("sessionId")
    timestamp = payload.get("timestamp")

    # Build ordered feature list for the model
    features = [payload.get(name, 0) for name in FEATURE_ORDER]

    result = {
    "risk": "LOW",
    "score": 0.0,
    "message": "Dummy prediction until ML module is merged"
}

    # TODO: also save session_id, timestamp, result to MongoDB via risk_model.py

    return result