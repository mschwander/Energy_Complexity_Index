import pandas as pd
import matplotlib.pyplot as plt

yellow = 1

if yellow:
    eci_df = pd.read_csv("04_Results/eci_results_Energy_yellow.csv")
else:
    eci_df = pd.read_csv("04_Results/eci_results_Energy.csv")
    #eci_df = pd.read_csv("04_Results/eci_results_BACI.csv")


eci_country = eci_df[["i", "t", "eci"]].drop_duplicates()
eci_country = eci_country.dropna(subset=["eci"]).reset_index(drop=True)
eci_country = eci_country.rename(columns={"i": "country_code"})
#print(eci_country.head())

# Filter for year 2023
eci_2023 = eci_country[eci_country["t"] == 2023].dropna(subset=["eci"])

# Sort by ECI
top15 = eci_2023.sort_values("eci", ascending=False).head(15)
bottom15 = eci_2023.sort_values("eci", ascending=True).head(15)
bottom15 = bottom15.sort_values("eci", ascending=False).reset_index(drop=True)

# Combine top and bottom
combined = pd.concat([top15, bottom15])

combined = pd.merge(combined, pd.read_csv("01_Data/country_codes_V202501.csv")[["country_code", "country_name"]], on="country_code", how="left")

#print(combined.head(30))

# Plot pillar diagram
fig, ax = plt.subplots(figsize=(12, 6))

colors = ["green"] * len(top15) + ["red"] * len(bottom15)

ax.bar(combined["country_name"], combined["eci"], color=colors)

ax.set_title("Top 15 and Bottom 15 Countries by ECI (2023)")
ax.set_ylabel("Economic Complexity Index (ECI)")
ax.set_xlabel("Country")
plt.xticks(rotation=75, ha="right")

plt.tight_layout()
if yellow:
    plt.savefig("04_Results/ECI_TopBottom15_yellow.png", dpi=300)
else:
    plt.savefig("04_Results/ECI_TopBottom15_Energy.png", dpi=300)
#plt.show()