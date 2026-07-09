from fastapi import APIRouter
from ml.predict import predict_user

router = APIRouter(prefix="/api", tags=["Behavior"])

@router.post("/behavior")
async def receive_behavior(payload: dict):
    result = predict_user(payload)
    return result