import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

#eci_df = pd.read_csv("Results/eci_results_Energy.csv")
eci_df = pd.read_csv("Results/eci_results_Energy_yellow.csv")
#eci_df = pd.read_csv("Results/eci_results_BACI.csv")

eci_country = eci_df[["i", "t", "eci"]].drop_duplicates()
eci_country = eci_country.dropna(subset=["eci"]).reset_index(drop=True)
eci_country = eci_country.rename(columns={"i": "country_code"})
#print(eci_country.head())

# Point to the shapefile you downloaded
world = gpd.read_file("Data/ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp")

# Mapping from shapefile codes to ISO3
fix_map = {
    "US1": "USA",
    "KA1": "KAZ",
    "GB1": "GBR",
    "DN1": "DNK",
    "FR1": "FRA",
    "CU1": "CUB",
    "IS1": "ISR",
    "NL1": "NLD",
    "AU1": "AUS",
    "CH1": "CHN",
    "FI1": "FIN",
    "SDS": "SSD",   # South Sudan
    "KOS": "XKX",   # Kosovo (not ISO official, but often XKX)
    "TWN": "TWN",   # Taiwan (ISO code exists but not in UN list)
    "ATA": "ATA",   # Antarctica (no ECI, can drop)
    "CYN": "CYN",   # Northern Cyprus (non‑ISO, can drop)
    "SOL": "SOL",   # Somaliland (non‑ISO, can drop)
    "SAH": "ESH",   # Western Sahara
}

# Apply fix to shapefile codes
world["SOV_A3"] = world["SOV_A3"].replace(fix_map)
#print(world.columns)

lookup = pd.read_csv("Data/country_codes_V202501.csv")  # your mapping file
#print(lookup.head())

#print(lookup[lookup["country_name"] == "United States"])

eci_country = eci_country.merge(lookup, on="country_code")

save_path = os.path.join("Results", "eci_country_results_Energy_yellow.csv")
eci_country.to_csv(save_path, index=False)
print(f"eci_country_results_Energy_yellow saved to {save_path}")

#print(eci_country.head())

world_eci = world.merge(
    eci_country[eci_country["t"] == 2023], left_on="SOV_A3", right_on="country_iso3", how="left")

#missing = world_eci[world_eci["eci"].isna()][["ADMIN","SOV_A3"]]
#print(missing.head(50))

fig, ax = plt.subplots(1, 1, figsize=(15, 8))

# Plot with controlled color scale
world_eci.plot(
    column="eci",
    cmap="Blues",
    legend=True,
    ax=ax,
    legend_kwds={
        "label": "Economic Complexity Index (ECI)",
        "orientation": "horizontal",   # put the colorbar below the map
        "shrink": 0.6                  # adjust size
    },
    vmin=-1.8,   # set min of color scale
    vmax=2.8     # set max of color scale
)

# --- Control the colorbar ticks ---
# Get the colorbar from the current figure
cbar = ax.get_figure().get_axes()[-1]  # the last axis is the colorbar
cbar.set_xticks(np.arange(-1.5, 3.0, 0.5))  # steps: -1.5, -1.0, -0.5, ..., 2.5

ax.set_title("Economic Complexity Index by Country, 2023")

plt.tight_layout()
plt.savefig("Results/ECI_Map_Energy_yellow.png", dpi=300)
print("Saved ECI map to Results/ECI_Map_Energy_yellow.png")
plt.close(fig)