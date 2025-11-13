import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

yellow = 0

if yellow:
    eci_country = pd.read_csv("04_Results/eci_country_results_Energy_yellow.csv")
    output_prefix = "04_Results/ECI_Energy_yellow"
else:
    #eci_country = pd.read_csv("04_Results/eci_country_results_Energy.csv")
    eci_country = pd.read_csv("04_Results/eci_country_results_BACI.csv")
    output_prefix = "04_Results/ECI_Energy_BACI"


eci_2023 = eci_country[eci_country["t"] == 2023].dropna(subset=["eci"])

stats_df = pd.read_csv("01_Data/population_2023.csv")  # includes 'country_iso3', 'population'
eci_2023 = eci_country[eci_country["t"] == 2023].dropna(subset=["eci"])

merged_df = eci_2023.merge(stats_df, on="country_iso3")

#check if there are missing countries
missing_countries = merged_df[merged_df["population"].isna()]["country_iso3"].unique()
if len(missing_countries) > 0:
    print("Warning: Missing population data for countries:", missing_countries)

plt.figure(figsize=(12, 6))
x = np.log10(merged_df["population"])
y = merged_df["eci"]

plt.scatter(x, y, alpha=0.7)

# Label selected countries
highlight = ["USA", "DEU", "JPN", "CHN", "IND", "BRA", "NOR", "SAU", "RU"]
for i, row in merged_df.iterrows():
    if row["country_iso3"] in highlight:
        plt.text(np.log10(row["population"]), row["eci"], row["country_iso3"],
                 fontsize=9, ha='right', va='bottom')

plt.xlabel("Population")
plt.ylabel("ECI")
plt.title("ECI vs Population")

# Set x-axis ticks at log10 scale: 10^6 to 10^9
ticks = np.arange(6, 10)  # log10(1 million) to log10(1 billion)
plt.xticks(ticks, [f"$10^{int(t)}$" for t in ticks])  # format as 10^6, 10^7, ..

if yellow == 1:
    plt.savefig(f"{output_prefix}_vs_Population.png", dpi=300)
else:
    plt.savefig(f"{output_prefix}_vs_Population.png", dpi=300)
plt.close()