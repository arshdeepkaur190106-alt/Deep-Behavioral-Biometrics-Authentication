import numpy as np
import pandas as pd

np.random.seed(42)

def generate_samples(n, label, base):
    return pd.DataFrame({
        "sessionDuration": np.random.normal(base["sessionDuration"], 2000, n),
        "totalKeyEvents": np.random.normal(base["totalKeyEvents"], 50, n),
        "typingSpeed": np.random.normal(base["typingSpeed"], 0.1, n),
        "averageHoldTime": np.random.normal(base["averageHoldTime"], 0.03, n),
        "averageFlightTime": np.random.normal(base["averageFlightTime"], 0.02, n),
        "backspaceCount": np.random.normal(base["backspaceCount"], 2, n),
        "errorRate": np.random.normal(base["errorRate"], 0.02, n),
        "totalMouseEvents": np.random.normal(base["totalMouseEvents"], 30, n),
        "mouseClicks": np.random.normal(base["mouseClicks"], 5, n),
        "doubleClicks": np.random.normal(base["doubleClicks"], 1, n),
        "dragCount": np.random.normal(base["dragCount"], 1, n),
        "averageMouseSpeed": np.random.normal(base["averageMouseSpeed"], 0.2, n),
        "averageMouseAcceleration": np.random.normal(base["averageMouseAcceleration"], 0.1, n),
        "totalScrollEvents": np.random.normal(base["totalScrollEvents"], 10, n),
        "totalScrollDistance": np.random.normal(base["totalScrollDistance"], 200, n),
        "averageScrollSpeed": np.random.normal(base["averageScrollSpeed"], 0.1, n),
        "maxScrollSpeed": np.random.normal(base["maxScrollSpeed"], 0.2, n),
        "minScrollSpeed": np.random.normal(base["minScrollSpeed"], 0.05, n),
        "scrollUpCount": np.random.normal(base["scrollUpCount"], 3, n),
        "scrollDownCount": np.random.normal(base["scrollDownCount"], 3, n),
        "label": label
    })

genuine_base = {
    "sessionDuration": 12000,
    "totalKeyEvents": 340,
    "typingSpeed": 0.52,
    "averageHoldTime": 0.14,
    "averageFlightTime": 0.09,
    "backspaceCount": 3,
    "errorRate": 0.02,
    "totalMouseEvents": 210,
    "mouseClicks": 15,
    "doubleClicks": 2,
    "dragCount": 1,
    "averageMouseSpeed": 0.8,
    "averageMouseAcceleration": 0.3,
    "totalScrollEvents": 45,
    "totalScrollDistance": 1200,
    "averageScrollSpeed": 0.4,
    "maxScrollSpeed": 0.9,
    "minScrollSpeed": 0.1,
    "scrollUpCount": 12,
    "scrollDownCount": 10
}

impostor_base = {
    "sessionDuration": 8000,
    "totalKeyEvents": 500,
    "typingSpeed": 0.85,
    "averageHoldTime": 0.22,
    "averageFlightTime": 0.15,
    "backspaceCount": 9,
    "errorRate": 0.09,
    "totalMouseEvents": 350,
    "mouseClicks": 30,
    "doubleClicks": 6,
    "dragCount": 4,
    "averageMouseSpeed": 1.6,
    "averageMouseAcceleration": 0.7,
    "totalScrollEvents": 80,
    "totalScrollDistance": 2500,
    "averageScrollSpeed": 0.9,
    "maxScrollSpeed": 1.8,
    "minScrollSpeed": 0.3,
    "scrollUpCount": 25,
    "scrollDownCount": 22
}

genuine = generate_samples(300, 1, genuine_base)
impostor = generate_samples(300, 0, impostor_base)

data = pd.concat([genuine, impostor], ignore_index=True)
data = data.sample(frac=1, random_state=42).reset_index(drop=True)

data.to_csv("../dataset/behavior_data.csv", index=False)

print("Saved", len(data), "rows to dataset/behavior_data.csv")