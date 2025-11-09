import pickle
import pandas as pd

# Load the pickle file
with open("data/eci_results.pkl", "rb") as f:
    eci_results = pickle.load(f)

# Check what type of object it is
print("Type of eci_results:", type(eci_results))

# If it's a dict, list the keys
if isinstance(eci_results, dict):
    print("Keys in eci_results:", eci_results.keys())
    # Peek into each DataFrame
    for key, df in eci_results.items():
        print(f"\n--- {key} ---")
        print(df.head())
        print(df.columns)

# If it's a DataFrame, just inspect directly
elif isinstance(eci_results, pd.DataFrame):
    print("eci_results is a DataFrame")
    print(eci_results.head())
    print(eci_results.columns)


# Load the pickle file
with open("data/eci_results.pkl", "rb") as f:
    eci_results = pickle.load(f)

# Confirm it's a DataFrame
print("Type:", type(eci_results))

# Save to CSV
eci_results.to_csv("Data/eci_results.csv", index=False)
print("Saved eci_results to Data/eci_results.csv")