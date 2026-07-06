import joblib
import numpy as np


model = joblib.load("models/behavior_model.pkl")
scaler = joblib.load("models/scaler.pkl")


def predict_user(features):
    features = np.array(features).reshape(1, -1)
    features_scaled = scaler.transform(features)

    prediction = model.predict(features_scaled)[0]
    probability = model.predict_proba(features_scaled)[0]

    confidence = max(probability) * 100

    if prediction == 0:
        result = "Legitimate User"
        risk_score = 100 - confidence
    else:
        result = "Suspicious User"
        risk_score = confidence

    return {
        "prediction": result,
        "confidence": round(confidence, 2),
        "risk_score": round(risk_score, 2)
    }


sample_features = [5.4, 0.10, 0.08, 720, 530, 18]

result = predict_user(sample_features)

print("Prediction:", result["prediction"])
print("Confidence:", result["confidence"], "%")
print("Risk Score:", result["risk_score"], "%")