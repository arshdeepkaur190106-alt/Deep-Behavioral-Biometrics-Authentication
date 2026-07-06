import pandas as pd

data = pd.read_csv("dataset/behavior_dataset.csv")

print("First 5 rows:")
print(data.head())

print("\nDataset information:")
print(data.info())

print("\nMissing values:")
print(data.isnull().sum())

print("\nDuplicate rows:")
print(data.duplicated().sum())

print("\nLabel distribution:")
print(data["label"].value_counts()) 