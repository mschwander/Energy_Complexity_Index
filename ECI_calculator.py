import pandas as pd
from ecomplexity import ecomplexity
import pickle
import os

df = pd.read_csv("Data/baci_energy_subset.csv")
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

# Define path to your GitHub data folder
save_path = os.path.join("Data", "eci_results.pkl")

# Save the whole results object
with open(save_path, "wb") as f:
    pickle.dump(eci_results, f)

print(f"eci_results saved to {save_path}")

print(eci_results.head())
print(eci_results.columns)

'''
# Country-level complexity (ECI)
eci_df = eci_results['complexity_country']
print(eci_df.head())

# Product-level complexity (PCI)
pci_df = eci_results['complexity_product']
print(pci_df.head())

eci_2023 = eci_df[eci_df["t"] == 2023].sort_values("eci", ascending=False)
print(eci_2023.head(10))
'''