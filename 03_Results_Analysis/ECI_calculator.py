import pandas as pd
from ecomplexity import ecomplexity
import pickle
import os

yellow = 1

if yellow:
    df = pd.read_csv("01_Data/baci_energy_subset_yellow.csv")
else:
    df = pd.read_csv("01_Data/baci_energy_subset.csv")
    #df = pd.read_csv(r"C:\Users\marvi\OneDrive\Semester Thesis\BACI_HS22_V202501\BACI_HS22_Y2023_V202501.csv")

# Run ecomplexity with column mapping
eci_results = ecomplexity(
    df,
    cols_input={
        "time": "t",        # year
        "loc": "i",         # exporter (country)
        "prod": "k",        # product code
        "val": "v"          # trade value
    }
)

# Save to CSV
if yellow:
    eci_results.to_csv("04_Results/eci_results_Energy_yellow.csv", index=False)
    print("Saved eci_results to Results/eci_results_Energy_yellow.csv")
else:
    eci_results.to_csv("04_Results/eci_results_Energy.csv", index=False)
    print("Saved eci_results to Results/eci_results_Energy.csv")

print(eci_results.head())
print(eci_results.columns)