import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def ECI_Distribution(cdata, yellow, year, save_folder):
    eci_country = cdata[['location_code', 'year', 'eci']].copy().drop_duplicates()
    eci_year = eci_country[eci_country["year"] == year].dropna(subset=["eci"])
    eci_year = eci_year.rename(columns={"location_code": "country_iso3"})

    # --- Scatter plot ---
    plt.figure(figsize=(12, 6))
    plt.scatter(eci_year["country_iso3"], eci_year["eci"], alpha=0.7)
    plt.xticks(rotation=75, ha="right")
    if yellow:
        plt.title(f"Scatter Plot of Energy Complexity Index by Country ({year}) (Yellow Dataset)")
    else:
        plt.title(f"Scatter Plot of Energy Complexity Index by Country ({year})")
    plt.ylabel("Energy Complexity Index (ECI)")
    plt.xlabel("Country")
    plt.tight_layout()

    if yellow:
        output_prefix = f"{save_folder}/{year}/Yellow/"
    else:
        output_prefix = f"{save_folder}/{year}/Energy/"

    # Ensure the parent directory exists
    os.makedirs(os.path.dirname(output_prefix), exist_ok=True)
    if yellow:
        plt.savefig(f"{output_prefix}ECI_Scatter_Energy_Yellow_{year}.png", dpi=300)
    else:
        plt.savefig(f"{output_prefix}ECI_Scatter_Energy_{year}.png", dpi=300)
    
    plt.close()

    # --- Histogram ---
    plt.figure(figsize=(8, 6))
    plt.hist(eci_year["eci"], bins=20, color="skyblue", edgecolor="black")
    if yellow:
        plt.title(f"Histogram of Energy Complexity Index Values ({year}) (Yellow Dataset)")
    else:
        plt.title(f"Histogram of Energy Complexity Index Values ({year})")
    plt.xlabel("Energy Complexity Index (ECI)")
    plt.ylabel("Frequency")
    plt.tight_layout()
    if yellow:
        plt.savefig(f"{output_prefix}ECI_Histogram_Energy_Yellow_{year}.png", dpi=300)
    else:
        plt.savefig(f"{output_prefix}ECI_Histogram_Energy_{year}.png", dpi=300)

    plt.close()

    # --- Density plot ---
    plt.figure(figsize=(8, 6))
    sns.kdeplot(eci_year["eci"], fill=True, color="purple", alpha=0.5)
    if yellow:
        plt.title(f"Density Plot of Energy Complexity Index Values ({year}) (Yellow Dataset)")
    else:
        plt.title(f"Density Plot of Energy Complexity Index Values ({year})")
    plt.xlabel("Energy Complexity Index (ECI)")
    plt.ylabel("Density")
    plt.tight_layout()
    if yellow:
        plt.savefig(f"{output_prefix}ECI_Density_Energy_Yellow_{year}.png", dpi=300)
    else:
        plt.savefig(f"{output_prefix}ECI_Density_Energy_{year}.png", dpi=300)

    plt.close()

    print(f"Saved scatter, histogram, and density plots within folder {output_prefix}")