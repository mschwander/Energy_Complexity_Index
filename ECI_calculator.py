import pandas as pd
from ecomplexity import ecomplexity

df = pd.read_csv("Data/baci_energy_subset.csv")

#print(df.head())

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

print(eci_results.head())
print(eci_results.columns)


# Country-level complexity (ECI)
#eci_df = eci_results['complexity_country']
#print(eci_df.head())

# Product-level complexity (PCI)
#pci_df = eci_results['complexity_product']
#print(pci_df.head())

#eci_2023 = eci_df[eci_df["t"] == 2023].sort_values("eci", ascending=False)
#print(eci_2023.head(10))
###