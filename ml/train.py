from preprocess import load_data
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib


X_train, X_test, y_train, y_test, scaler, feature_names = load_data()

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)

y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)

print("Accuracy:", accuracy)
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

joblib.dump(model, "models/behavior_model.pkl")
joblib.dump(scaler, "models/scaler.pkl")
joblib.dump(list(feature_names), "models/feature_names.pkl")

print("\nModel Saved Successfully!") 
