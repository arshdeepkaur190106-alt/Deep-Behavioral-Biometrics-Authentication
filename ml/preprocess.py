import pandas as pd
from sklearn.preprocessing import StandardScaler


def load_data():
    data = pd.read_csv("dataset/behavior_dataset.csv")

    data = data.dropna()
    data = data.drop_duplicates()

    X = data.drop("label", axis=1)
    y = data["label"]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    return X_scaled, y, scaler