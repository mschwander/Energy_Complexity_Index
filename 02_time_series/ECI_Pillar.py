import pandas as pd
import matplotlib.pyplot as plt
import os

def ECI_Pillar(cdata, supplementary, year, save_folder):
    eci_df = cdata[['country_iso3', 'year', 'eci']].copy()

    eci_country = eci_df[["country_iso3", "year", "eci"]].drop_duplicates()
    eci_country = eci_country.dropna(subset=["eci"]).reset_index(drop=True)
    #print(eci_country.head())

    # Filter for year
    eci_year = eci_country[eci_country["year"] == year].dropna(subset=["eci"])

    # Sort by ECI
    top15 = eci_year.sort_values("eci", ascending=False).head(15)

    bottom15 = eci_year.sort_values("eci", ascending=True).head(15)
    #bottom15 = bottom15.sort_values("eci", ascending=False).reset_index(drop=True)
    

    # Combine top and bottom
    combined = pd.concat([top15, bottom15])
    #print(combined.head(30))
    
    country_codes = pd.read_csv("01_Data/BACI/country_codes_V202501.csv")[["country_iso3", "country_name"]]
    combined = pd.merge(combined, country_codes, on="country_iso3", how="left")

    #print(combined.head(30))
    combined = combined.drop_duplicates(subset="country_iso3", keep="first")
    combined = combined.sort_values("eci", ascending=False).reset_index(drop=True)
    #print(combined.head(30))

    # Plot pillar diagram
    fig, ax = plt.subplots(figsize=(12, 6))

    colors = ["green" if val >= 0 else "red" for val in combined["eci"]]
    ax.bar(combined["country_name"], combined["eci"], color=colors)
    if supplementary:
        ax.set_title(f"Top 15 and Bottom 15 Countries by Energy Complexity Index in {year} (supplementary Dataset)")
    else:
        ax.set_title(f"Top 15 and Bottom 15 Countries by Energy Complexity Index in {year}")    
    ax.set_ylabel("Energy Complexity Index (ECI)")
    ax.set_xlabel("Country")

    plt.xticks(rotation=75, ha="right")

    plt.tight_layout()
    if supplementary:
        output_dir = f"{save_folder}/{year}/supplementary/"
        os.makedirs(output_dir, exist_ok=True)  # create folder if missing
        save_path = os.path.join(output_dir, f"ECI_TopBottom15_Energy_supplementary_{year}.png")
        plt.savefig(save_path, dpi=300)
        print(f"ECI Pillar Plot for year {year} (supplementary Dataset) saved.")
    else:
        output_dir = f"{save_folder}/{year}/Energy/"
        os.makedirs(output_dir, exist_ok=True)  # create folder if missing
        save_path = os.path.join(output_dir, f"ECI_TopBottom15_Energy_{year}.png")
        plt.savefig(save_path, dpi=300)
        print(f"ECI Pillar Plot for year {year} saved.")