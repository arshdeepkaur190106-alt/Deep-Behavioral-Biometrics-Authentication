import pandas as pd

data = pd.read_csv("dataset/DSL-StrongPasswordData.csv")

print("First 5 rows:")
print(data.head())

print("\nShape:")
print(data.shape)

print("\nColumns:")
print(data.columns)

print("\nMissing values:")
print(data.isnull().sum())

print("\nUsers:")
print(data["subject"].value_counts())