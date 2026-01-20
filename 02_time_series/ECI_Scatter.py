import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
def ECI_Scatter_Population(cdata, supplementary, year, save_folder):
    
    population_data = pd.read_csv("01_Data/WPP2024_Demographic_Indicators_Medium.csv")

    population_year = population_data[population_data["Time"] == year]

    # Select relevant columns and rename
    population_year = population_year[["ISO3_code", "TPopulation1July"]].rename(
        columns={"ISO3_code": "country_iso3", "TPopulation1July": "population"}
    )
    #take out the ones that don't have iso3 codes
    population_year = population_year.dropna(subset=["country_iso3"])

    population_year["population"] = population_year["population"] * 1000 # includes 'country_iso3', 'population'
    
    eci_country = cdata[['country_iso3', 'year', 'eci']].copy().drop_duplicates()
    
    eci_year = eci_country[eci_country["year"] == year].dropna(subset=["eci"])
    
    merged_df = eci_year.merge(population_year, on="country_iso3")

    #check if there are missing countries
    missing_countries = merged_df[merged_df["population"].isna()]["country_iso3"].unique()
    if len(missing_countries) > 0:
        print("Warning: Missing population data for countries:", missing_countries)

    plt.figure(figsize=(12, 6))
    x = np.log10(merged_df["population"])
    y = merged_df["eci"]

    plt.scatter(x, y, alpha=0.7)

    # Label selected countries in green for visibility
    highlight_green = ["CHN", "ESP", "GBR", "USA", "DEU", "FRA", "JPN", "ITA", "POL", "FIN", "CHE", "SWE", "AUT", "ISR"]
    for i, row in merged_df.iterrows():
        if row["country_iso3"] in highlight_green:
            plt.text(np.log10(row["population"]), row["eci"], row["country_iso3"],
                    fontsize=9, ha='right', va='bottom', color='green')
    # Label selected countries in red for visibility
    highlight_red = ["GNQ", "TCD", "SDN", "RWA", "TGO", "MLI", "GIN", "KWT", "PNG", "LBR", "SLE", "LBY", "COD", "MNG", "OMN"]
    for i, row in merged_df.iterrows():
        if row["country_iso3"] in highlight_red:
            plt.text(np.log10(row["population"]), row["eci"], row["country_iso3"],
                    fontsize=9, ha='right', va='bottom', color='red')
            
    plt.xlabel(f"Population in year {year} (log10 scale)")
    if supplementary == 1:
        plt.ylabel(f"Energy Complexity Index in year {year}")
        plt.title("Energy Complexity Index vs Population (supplementary Dataset)")
    else:
        plt.ylabel(f"Energy Complexity Index in year {year}")
        plt.title("Energy Complexity Index vs Population")

    # Set x-axis ticks at log10 scale: 10^6 to 10^9
    ticks = np.arange(6, 10)  # log10(1 million) to log10(1 billion)
    plt.xticks(ticks, [f"$10^{int(t)}$" for t in ticks])  # format as 10^6, 10^7, ..
    
    if supplementary == 1:
        output_dir = f"{save_folder}/{year}/supplementary/"
        os.makedirs(output_dir, exist_ok=True)  # create folder if missing
        save_path = os.path.join(output_dir, f"ECI_vs_Population_Energy_supplementary_{year}.png")
        plt.savefig(save_path, dpi=300)
    else:
        output_dir = f"{save_folder}/{year}/Energy/"
        os.makedirs(output_dir, exist_ok=True)  # create folder if missing
        save_path = os.path.join(output_dir, f"ECI_vs_Population_Energy_{year}.png")
        plt.savefig(save_path, dpi=300)
    plt.close()

    print(f"ECI vs Population Scatter Plot for year {year} saved.")

def ECI_Scatter_GDP(cdata, supplementary, year, save_folder):
    # Load GDP per capita data (replace with your actual file)
    gdp_data = pd.read_csv("01_Data/GDP_World_Bank.csv", skiprows=4)
    
    gdp_year = gdp_data[["Country Name", "Country Code", f"{year}"]]

    gdp_year = gdp_year.rename(columns={"Country Code": "country_iso3", f"{year}": "gdp_per_capita"})
    
    # Prepare ECI data
    eci_country = cdata[['country_iso3', 'year', 'eci']].copy().drop_duplicates()
    eci_year = eci_country[eci_country["year"] == year].dropna(subset=["eci"])

    # Merge ECI with GDP per capita
    merged_df = eci_year.merge(gdp_year, on="country_iso3")
    
    # Check for missing countries
    missing_countries = merged_df[merged_df["gdp_per_capita"].isna()]["country_iso3"].unique()
    if len(missing_countries) > 0:
        print("Warning: Missing GDP data for countries:", missing_countries)

    # Scatter plot
    plt.figure(figsize=(12, 6))
    x = np.log10(merged_df["gdp_per_capita"])
    y = merged_df["eci"]

    plt.scatter(x, y, alpha=0.7)

        # Label selected countries in green for visibility
    highlight_green = ["CHN", "ESP", "GBR", "USA", "DEU", "FRA", "JPN", "ITA", "POL", "FIN", "CHE", "SWE", "AUT", "ISR"]
    for i, row in merged_df.iterrows():
        if row["country_iso3"] in highlight_green:
            plt.text(np.log10(row["gdp_per_capita"]), row["eci"], row["country_iso3"],
                    fontsize=9, ha='right', va='bottom', color='green')
    # Label selected countries in red for visibility
    highlight_red = ["GNQ", "TCD", "SDN", "RWA", "TGO", "MLI", "GIN", "KWT", "PNG", "LBR", "SLE", "LBY", "COD", "MNG", "OMN"]
    for i, row in merged_df.iterrows():
        if row["country_iso3"] in highlight_red:
            plt.text(np.log10(row["gdp_per_capita"]), row["eci"], row["country_iso3"],
                    fontsize=9, ha='right', va='bottom', color='red')

    plt.xlabel(f"GDP per capita")
    plt.ylabel(f"Energy Complexity Index")
    if supplementary == 1:
        plt.title(f"Energy Complexity Index vs GDP per Capita in {year} (supplementary Dataset)")
    else:
        plt.title(f"Energy Complexity Index vs GDP per Capita in {year}")

    # Set x-axis ticks (e.g. $10^3$ to $10^5$ for GDP per capita in USD)
    ticks = np.arange(3, 6)  # log10(1k) to log10(100k)
    plt.xticks(ticks, [f"$10^{int(t)}$" for t in ticks])

    # Save figure
    if supplementary == 1:
        output_dir = f"{save_folder}/{year}/supplementary/"
        os.makedirs(output_dir, exist_ok=True)  # create folder if missing
        save_path = os.path.join(output_dir, f"ECI_vs_GDPperCapita_Energy_supplementary_{year}.png")
        plt.savefig(save_path, dpi=300)
    else:
        output_dir = f"{save_folder}/{year}/Energy/"
        os.makedirs(output_dir, exist_ok=True)  # create folder if missing
        save_path = os.path.join(output_dir, f"ECI_vs_GDPperCapita_Energy_{year}.png")
        plt.savefig(save_path, dpi=300)
    plt.close()

    print(f"ECI vs GDP per Capita Scatter Plot for year {year} saved.")

def ECI_Scatter_Energy(cdata, supplementary, year, save_folder):
    # Load GDP per capita data (replace with your actual file)
    Energy_data = pd.read_csv("01_Data/Energy_use_World_Bank.csv", skiprows=4)
    
    Energy_year = Energy_data[["Country Name", "Country Code", f"{year}"]]

    Energy_year = Energy_year.rename(columns={"Country Code": "country_iso3", f"{year}": "energy_use_per_capita"})
    
    # Prepare ECI data
    eci_country = cdata[['country_iso3', 'year', 'eci']].copy().drop_duplicates()
    eci_year = eci_country[eci_country["year"] == year].dropna(subset=["eci"])

    # Merge ECI with GDP per capita
    merged_df = eci_year.merge(Energy_year, on="country_iso3")
    
    # Check for missing countries
    missing_countries = merged_df[merged_df["energy_use_per_capita"].isna()]["country_iso3"].unique()
    if len(missing_countries) > 0:
        print("Warning: Missing Energy Use per capita data for countries:", missing_countries)

    # Scatter plot
    plt.figure(figsize=(12, 6))
    x = np.log10(merged_df["energy_use_per_capita"])
    y = merged_df["eci"]

    plt.scatter(x, y, alpha=0.7)

        # Label selected countries in green for visibility
    highlight_green = ["CHN", "ESP", "GBR", "USA", "DEU", "FRA", "JPN", "ITA", "POL", "FIN", "CHE", "SWE", "AUT", "ISR"]
    for i, row in merged_df.iterrows():
        if row["country_iso3"] in highlight_green:
            plt.text(np.log10(row["energy_use_per_capita"]), row["eci"], row["country_iso3"],
                    fontsize=9, ha='right', va='bottom', color='green')
    # Label selected countries in red for visibility
    highlight_red = ["GNQ", "TCD", "SDN", "RWA", "TGO", "MLI", "GIN", "KWT", "PNG", "LBR", "SLE", "LBY", "COD", "MNG", "OMN"]
    for i, row in merged_df.iterrows():
        if row["country_iso3"] in highlight_red:
            plt.text(np.log10(row["energy_use_per_capita"]), row["eci"], row["country_iso3"],
                    fontsize=9, ha='right', va='bottom', color='red')

    plt.xlabel(f"Energy use per capita")
    plt.ylabel(f"Energy Complexity Index")
    if supplementary == 1:
        plt.title(f"Energy Complexity Index vs Energy use per Capita in {year} (supplementary Dataset)")
    else:
        plt.title(f"Energy Complexity Index vs Energy use per Capita in {year}")

    # Set x-axis ticks for energy use per capita
    ticks = np.arange(1, 4)  # log10(10) to log10(1000)
    plt.xticks(ticks, [f"$10^{int(t)}$" for t in ticks])

    # Save figure
    if supplementary == 1:
        output_dir = f"{save_folder}/{year}/supplementary/"
        os.makedirs(output_dir, exist_ok=True)  # create folder if missing
        save_path = os.path.join(output_dir, f"ECI_vs_EnergyperCapita_Energy_supplementary_{year}.png")
        plt.savefig(save_path, dpi=300)
    else:
        output_dir = f"{save_folder}/{year}/Energy/"
        os.makedirs(output_dir, exist_ok=True)  # create folder if missing
        save_path = os.path.join(output_dir, f"ECI_vs_EnergyperCapita_Energy_{year}.png")
        plt.savefig(save_path, dpi=300)

    plt.close()

    print(f"ECI vs Energy use per Capita Scatter Plot for year {year} saved.")