import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

def ECI_Map(cdata, supplementary, year, save_folder):
    eci_country = cdata[['country_iso3', 'eci', 'year']].copy()
    eci_country = eci_country.dropna(subset=['eci']).reset_index(drop=True)
    
    eci_country = eci_country[["country_iso3", "year", "eci"]].drop_duplicates()
    eci_country = eci_country.dropna(subset=["eci"]).reset_index(drop=True)
    eci_country = eci_country.rename(columns={"country_iso3": "country_code"})
    #print(eci_country.head())

    # Point to the shapefile you downloaded
    world = gpd.read_file("01_Data/ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp")

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

    lookup = pd.read_csv("01_Data/BACI/country_codes_V202501.csv")  # your mapping file
    #print(lookup.head())
    #print(eci_country.head())

    # Keep ECI results as strings
    eci_country['country_code'] = eci_country['country_code'].astype(str)

    # Merge with lookup using alpha-3 codes
    eci_country = eci_country.merge(
        lookup[['country_iso3','country_name','country_iso2','country_code']], 
        left_on="country_code", right_on="country_iso3", how="left"
    )
    if supplementary:
        output_dir = f"{save_folder}/{year}/supplementary/"
        os.makedirs(output_dir, exist_ok=True)  # create folder if missing
        save_path = os.path.join(output_dir, f"eci_country_results_Energy_supplementary_{year}.csv")
        eci_country.to_csv(save_path, index=False)
        print(f"eci_country_results_Energy_supplementary_{year} saved to {save_path}")
    else:
        output_dir = f"{save_folder}/{year}/Energy/"
        os.makedirs(output_dir, exist_ok=True)  # create folder if missing
        save_path = os.path.join(output_dir, f"eci_country_results_Energy_{year}.csv")
        eci_country.to_csv(save_path, index=False)
        print(f"eci_country_results_Energy_{year} saved to {save_path}")

    world_eci = world.merge(
        eci_country[eci_country["year"] == year], left_on="SOV_A3", right_on="country_iso3", how="left")

    #missing = world_eci[world_eci["eci"].isna()][["ADMIN","SOV_A3"]]
    #print(missing.head(50))

    fig, ax = plt.subplots(1, 1, figsize=(15, 8))

    # Plot with controlled color scale
    world_eci.plot(
        column="eci",
        cmap="RdBu",
        legend=True,
        ax=ax,
        legend_kwds={
            "label": "Energy Complexity Index (ECI)",
            "orientation": "horizontal",   # put the colorbar below the map
            "shrink": 0.6                  # adjust size
        },
        #vmin=-4.0624666,   # set min of color scale
        #vmax=2.9926527     # set max of color scale
    )

    # --- Control the colorbar ticks ---
    # Get the colorbar from the current figure
    #cbar = ax.get_figure().get_axes()[-1]  # the last axis is the colorbar
    #cbar.set_xticks(np.arange(-1.5, 3.0, 0.5))  # steps: -1.5, -1.0, -0.5, ..., 2.5
    if supplementary:
        ax.set_title(f"Energy Complexity Index by Country, {year} (supplementary Dataset)")
    else:
        ax.set_title(f"Energy Complexity Index by Country, {year}")

    plt.tight_layout()
    if supplementary:
        output_dir = f"{save_folder}/{year}/supplementary/"
        os.makedirs(output_dir, exist_ok=True)  # create folder if missing
        save_path = os.path.join(output_dir, f"ECI_Map_Energy_supplementary_{year}.png")
        plt.savefig(save_path, dpi=300)
        print(f"Saved ECI map to {save_folder}/{year}/supplementary/ECI_Map_Energy_supplementary_{year}.png")
        plt.close(fig)
    else:
        output_dir = f"{save_folder}/{year}/Energy/"
        os.makedirs(output_dir, exist_ok=True)  # create folder if missing
        save_path = os.path.join(output_dir, f"ECI_Map_Energy_{year}.png")
        plt.savefig(save_path, dpi=300)
        print(f"Saved ECI map to {save_folder}/{year}/Energy/ECI_Map_Energy_{year}.png")
        plt.close(fig)

''' Example usage '''
'''
supplementary = 0
year = 2023

df = pd.read_csv(f"04_Results/{year}/Energy/eci_results_Energy_{year}.csv")

ECI_Map(df, supplementary, year)
'''