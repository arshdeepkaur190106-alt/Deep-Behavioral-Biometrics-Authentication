import os
import joblib
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)

MODEL_PATH = os.path.join(PROJECT_DIR, "models", "behavior_model.pkl")
SCALER_PATH = os.path.join(PROJECT_DIR, "models", "scaler.pkl")
FEATURE_NAMES_PATH = os.path.join(PROJECT_DIR, "models", "feature_names.pkl")

model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)
feature_names = joblib.load(FEATURE_NAMES_PATH)


def predict_user(features):
    if isinstance(features, dict):
        features = [features[name] for name in feature_names]

    features_df = pd.DataFrame([features], columns=feature_names)
    features_scaled = scaler.transform(features_df)

    prediction = model.predict(features_scaled)[0]
    probability = model.predict_proba(features_scaled)[0]

    confidence = max(probability) * 100

    return {
        "prediction": str(prediction),
        "confidence": round(float(confidence), 2),
        "risk_score": round(float(100 - confidence), 2)
    }


if __name__ == "__main__":
    sample_features = [
        0.1491, 0.3979, 0.2488, 0.1069, 0.1674, 0.0605,
        0.1169, 0.2212, 0.1043, 0.1417, 1.1885, 1.0468,
        0.1146, 1.6055, 1.4909, 0.1067, 0.7590, 0.6523,
        0.1016, 0.2136, 0.1120, 0.1349, 0.1484, 0.0135,
        0.0932, 0.3515, 0.2583, 0.1338, 0.3509, 0.2171,
        0.0742
    ]

    result = predict_user(sample_features)

    print("Predicted User:", result["prediction"])
    print("Confidence:", result["confidence"], "%")
    print("Risk Score:", result["risk_score"], "%")