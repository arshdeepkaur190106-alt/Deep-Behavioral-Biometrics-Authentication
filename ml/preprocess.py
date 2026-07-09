import pandas as pd

FEATURE_COLUMNS = [
    "sessionDuration",
    "totalKeyEvents",
    "typingSpeed",
    "averageHoldTime",
    "averageFlightTime",
    "backspaceCount",
    "errorRate",
    "totalMouseEvents",
    "mouseClicks",
    "doubleClicks",
    "dragCount",
    "averageMouseSpeed",
    "averageMouseAcceleration",
    "totalScrollEvents",
    "totalScrollDistance",
    "averageScrollSpeed",
    "maxScrollSpeed",
    "minScrollSpeed",
    "scrollUpCount",
    "scrollDownCount"
]

def load_and_preprocess(csv_path):
    df = pd.read_csv(csv_path)
    X = df[FEATURE_COLUMNS]
    y = df["label"]
    return X, y, FEATURE_COLUMNS