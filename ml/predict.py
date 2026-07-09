import os
import joblib
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

model = joblib.load(os.path.join(BASE_DIR, "..", "models", "behavior_model.pkl"))
scaler = joblib.load(os.path.join(BASE_DIR, "..", "models", "scaler.pkl"))
feature_names = joblib.load(os.path.join(BASE_DIR, "..", "models", "feature_names.pkl"))

def predict_user(features):

    if isinstance(features, dict):
        features = [features[name] for name in feature_names]

    features_df = pd.DataFrame([features], columns=feature_names)

    features_scaled = scaler.transform(features_df)

    prediction = model.predict(features_scaled)[0]
    probability = model.predict_proba(features_scaled)[0]

    confidence = max(probability) * 100

    return {
        "prediction": int(prediction),
        "confidence": round(float(confidence), 2),
        "risk_score": round(float(100 - confidence), 2)
    }

if __name__ == "__main__":

    sample_features = {
        "sessionDuration":12000,
        "totalKeyEvents":340,
        "typingSpeed":0.52,
        "averageHoldTime":0.14,
        "averageFlightTime":0.09,
        "backspaceCount":3,
        "errorRate":0.02,
        "totalMouseEvents":210,
        "mouseClicks":15,
        "doubleClicks":2,
        "dragCount":1,
        "averageMouseSpeed":0.8,
        "averageMouseAcceleration":0.3,
        "totalScrollEvents":45,
        "totalScrollDistance":1200,
        "averageScrollSpeed":0.4,
        "maxScrollSpeed":0.9,
        "minScrollSpeed":0.1,
        "scrollUpCount":12,
        "scrollDownCount":10
    }

    result = predict_user(sample_features)

    print("Prediction:", result["prediction"])
    print("Confidence:", result["confidence"], "%")
    print("Risk Score:", result["risk_score"], "%")