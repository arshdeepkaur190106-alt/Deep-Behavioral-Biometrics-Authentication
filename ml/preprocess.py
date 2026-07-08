import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split


def load_data():
    data = pd.read_csv("dataset/DSL-StrongPasswordData.csv")

    data = data.dropna()
    data = data.drop_duplicates()

    X = data.drop(["subject", "sessionIndex", "rep"], axis=1)
    y = data["subject"]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    return X_train, X_test, y_train, y_test, scaler, X.columns