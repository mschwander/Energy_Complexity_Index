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

    lookup = pd.read_csv("01_Data/BACI/country_codes_V202501.csv")

    eci_country['country_code'] = eci_country['country_code'].astype(str)
    eci_country = eci_country.merge(
        lookup[['country_iso3','country_name','country_iso2','country_code']], 
        left_on="country_code", right_on="country_iso3", how="left"
    )
    if supplementary:
        output_dir = f"{save_folder}/{year}/supplementary/"
        os.makedirs(output_dir, exist_ok=True)
        save_path = os.path.join(output_dir, f"eci_country_results_Energy_supplementary_{year}.csv")
        eci_country.to_csv(save_path, index=False)
        print(f"eci_country_results_Energy_supplementary_{year} saved to {save_path}")
    else:
        output_dir = f"{save_folder}/{year}/Energy/"
        os.makedirs(output_dir, exist_ok=True)
        save_path = os.path.join(output_dir, f"eci_country_results_Energy_{year}.csv")
        eci_country.to_csv(save_path, index=False)
        print(f"eci_country_results_Energy_{year} saved to {save_path}")

    world_eci = world.merge(
        eci_country[eci_country["year"] == year], left_on="SOV_A3", right_on="country_iso3", how="left")

    fig, ax = plt.subplots(1, 1, figsize=(15, 8))
    max_val = world_eci["eci"].max()
    min_val = world_eci["eci"].min()
    abs_limit = max(abs(max_val), abs(min_val))
    world_eci.plot(
        column="eci",
        cmap="RdBu",
        legend=True,
        ax=ax,
        vmin = -5,
        vmax = 5,
        legend_kwds={
            "label": "Energy Complexity Index (ECI)",
            "orientation": "horizontal",   # put the colorbar below the map
            "shrink": 0.6,                  # adjust size
            "ticks": range(-4, 5)
        },
    )

    if supplementary:
        ax.set_title(f"Energy Complexity Index by Country, {year} (with supplementary Dataset)")
    else:
        ax.set_title(f"Energy Complexity Index by Country, {year}")

    plt.tight_layout()
    if supplementary:
        output_dir = f"{save_folder}/{year}/supplementary/"
        os.makedirs(output_dir, exist_ok=True)
        save_path = os.path.join(output_dir, f"ECI_Map_Energy_supplementary_{year}.png")
        plt.savefig(save_path, dpi=300)
        print(f"Saved ECI map to {save_path}")
        plt.close(fig)
    else:
        output_dir = f"{save_folder}/{year}/Energy/"
        os.makedirs(output_dir, exist_ok=True)
        save_path = os.path.join(output_dir, f"ECI_Map_Energy_{year}.png")
        plt.savefig(save_path, dpi=300)
        print(f"Saved ECI map to {save_path}")
        plt.close(fig)

def ECI_Map_Comparison(cdata, supplementary, year1, year2, save_folder):
    col_y1 = f"eci_{year1}"
    col_y2 = f"eci_{year2}"
    
  
    if col_y1 not in cdata.columns or col_y2 not in cdata.columns:
        print(f"Error: Columns {col_y1} or {col_y2} not found in dataset.")
        return

    world = gpd.read_file("01_Data/ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp")

    fix_map = {
        "US1": "USA", "KA1": "KAZ", "GB1": "GBR", "DN1": "DNK", "FR1": "FRA",
        "CU1": "CUB", "IS1": "ISR", "NL1": "NLD", "AU1": "AUS", "CH1": "CHN",
        "FI1": "FIN", "SDS": "SSD", "KOS": "XKX", "TWN": "TWN", "ATA": "ATA",
        "CYN": "CYN", "SOL": "SOL", "SAH": "ESH"
    }
    world["SOV_A3"] = world["SOV_A3"].replace(fix_map)
    world_data = world.merge(cdata, left_on="SOV_A3", right_on="country_iso3", how="left")

    vals_y1 = world_data[col_y1].dropna().values
    vals_y2 = world_data[col_y2].dropna().values
    all_vals = np.concatenate([vals_y1, vals_y2])
    
    global_min = all_vals.min()
    global_max = all_vals.max()
    
    # Center scale at 0 (White)
    abs_limit = max(abs(global_min), abs(global_max))
    vmin = -abs_limit
    vmax = abs_limit

    fig, axes = plt.subplots(2, 1, figsize=(20, 8))
    
    mode_str = "Supplementary" if supplementary else "Core"
    folder_name = "supplementary" if supplementary else "Energy"

    world_data.plot(
        column=col_y1,   
        cmap="RdBu",
        ax=axes[0],
        vmin=-5, vmax=5,
        legend=False,
        missing_kwds={'color': 'lightgrey'}
    )
    axes[0].set_title(f"ECI {year1}", fontsize=15)
    axes[0].set_axis_off()

    world_data.plot(
        column=col_y2,
        cmap="RdBu",
        ax=axes[1],
        vmin=vmin, vmax=vmax,
        legend=True,
        legend_kwds={
            "label": "Energy Complexity Index (ECI)",
            "orientation": "horizontal",
            "shrink": 0.6
        },
        missing_kwds={'color': 'lightgrey'}
    )
    axes[1].set_title(f"ECI {year2}", fontsize=15)
    axes[1].set_axis_off()

    plt.suptitle(f"ECI Evolution: {year1} vs {year2} ({mode_str} Data)", fontsize=20)
    plt.tight_layout()

    output_dir = os.path.join(save_folder, "Comparisons", folder_name)
    os.makedirs(output_dir, exist_ok=True)
    
    filename = f"Map_Comparison_{year1}_{year2}_{folder_name}.png"
    save_path = os.path.join(output_dir, filename)
    
    plt.savefig(save_path, dpi=300)
    plt.close(fig)
    print(f"Saved Comparison Map to {save_path}")

##############################################################################################################################
##############################################################################################################################

''' Example usage '''
'''
data = pd.read_csv("03_Results/Time_series/1996-2023/ECI_time_series_Energy_supplementary_1996-2023.csv")
supplementary = 1
year1 = 1996
year2 = 2023
save_folder = "03_Results/"

ECI_Map_Comparison(data, supplementary, year1, year2, save_folder)

supplementary = 1
year = 1996
save_folder = "03_Results"
if supplementary:
    df = pd.read_csv(f"03_Results/{year}/supplementary/eci_results_Energy_supplementary_{year}.csv")
else:
    df = pd.read_csv(f"03_Results/{year}/Energy/eci_results_Energy_{year}.csv")

ECI_Map(df, supplementary, year, save_folder)
'''