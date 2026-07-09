import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from preprocess import load_and_preprocess

X, y, feature_names = load_and_preprocess("../dataset/behavior_data.csv")

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X_train_scaled, y_train)

accuracy = model.score(X_test_scaled, y_test)

print("Test accuracy:", accuracy)

joblib.dump(model, "../models/behavior_model.pkl")
joblib.dump(scaler, "../models/scaler.pkl")
joblib.dump(feature_names, "../models/feature_names.pkl")

print("Model, scaler, and feature names saved.")