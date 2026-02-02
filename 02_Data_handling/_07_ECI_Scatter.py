import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
def ECI_Scatter_Population(cdata, supplementary, year, save_folder):    
    population_data = pd.read_csv("01_Data/WPP2024_Demographic_Indicators_Medium.csv")
    population_year = population_data[population_data["Time"] == year]
    population_year = population_year[["ISO3_code", "TPopulation1July"]].rename(
        columns={"ISO3_code": "country_iso3", "TPopulation1July": "population"}
    )
    population_year = population_year.dropna(subset=["country_iso3"])
    #Take correct number of people
    population_year["population"] = population_year["population"] * 1000
    eci_country = cdata[['country_iso3', 'year', 'eci']].copy().drop_duplicates()    
    eci_year = eci_country[eci_country["year"] == year].dropna(subset=["eci"])
    
    merged_df = eci_year.merge(population_year, on="country_iso3")

    missing_countries = merged_df[merged_df["population"].isna()]["country_iso3"].unique()
    if len(missing_countries) > 0:
        print("Warning: Missing population data for countries:", missing_countries)

    plt.figure(figsize=(12, 4.5))
    x = np.log10(merged_df["population"])
    y = merged_df["eci"]    
    plt.ylim(-5, 3)
    plt.scatter(x, y, alpha=0.7)
    # Label selected countries in green for visibility
    highlight_black = ["CHN", "USA", "DEU", "CHE", "POL", "TUR", "GBR", "HRV", "SWE", "KOR", "RUS", "ARE"]
    for i, row in merged_df.iterrows():
        if row["country_iso3"] in highlight_black:
            plt.text(np.log10(row["population"]), row["eci"], row["country_iso3"],
                    fontsize=9, ha='right', va='bottom', color='black')
    # Label selected countries in red for visibility
    highlight_red = []
    #highlight_red = ["GNQ", "TCD", "SDN", "RWA", "TGO", "MLI", "GIN", "KWT", "PNG", "LBR", "SLE", "LBY", "COD", "MNG", "OMN"]
    for i, row in merged_df.iterrows():
        if row["country_iso3"] in highlight_red:
            plt.text(np.log10(row["population"]), row["eci"], row["country_iso3"],
                    fontsize=9, ha='right', va='bottom', color='red')
            
    plt.xlabel(f"Population in year {year}")
    if supplementary == 1:
        plt.ylabel(f"Energy Complexity Index in year {year}")
        plt.title(f"Energy Complexity Index vs Population {year} (with supplementary Dataset)")
    else:
        plt.ylabel(f"Energy Complexity Index in year {year}")
        plt.title("Energy Complexity Index vs Population")

    ticks = np.arange(6, 10)  # log10(1 million) to log10(1 billion)
    plt.xticks(ticks, [f"$10^{int(t)}$" for t in ticks])  # format as 10^6, 10^7, ..
    
    if supplementary == 1:
        output_dir = f"{save_folder}/{year}/supplementary/"
        os.makedirs(output_dir, exist_ok=True)
        save_path = os.path.join(output_dir, f"ECI_vs_Population_Energy_supplementary_{year}.png")
        plt.savefig(save_path, dpi=300)
    else:
        output_dir = f"{save_folder}/{year}/Energy/"
        os.makedirs(output_dir, exist_ok=True)
        save_path = os.path.join(output_dir, f"ECI_vs_Population_Energy_{year}.png")
        plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"ECI vs Population Scatter Plot for year {year} saved.")

def ECI_Scatter_GDP(cdata, supplementary, year, save_folder):
    gdp_data = pd.read_csv("01_Data/GDP_World_Bank.csv", skiprows=4)
    gdp_year = gdp_data[["Country Name", "Country Code", f"{year}"]]
    gdp_year = gdp_year.rename(columns={"Country Code": "country_iso3", f"{year}": "gdp_per_capita"})
    
    eci_country = cdata[['country_iso3', 'year', 'eci']].copy().drop_duplicates()
    eci_year = eci_country[eci_country["year"] == year].dropna(subset=["eci"])
    
    merged_df = eci_year.merge(gdp_year, on="country_iso3")
    
    missing_countries = merged_df[merged_df["gdp_per_capita"].isna()]["country_iso3"].unique()
    if len(missing_countries) > 0:
        print("Warning: Missing GDP data for countries:", missing_countries)

    plt.figure(figsize=(12, 4.5))
    x = np.log10(merged_df["gdp_per_capita"])
    y = merged_df["eci"]
    plt.ylim(-5, 3)

    plt.scatter(x, y, alpha=0.7)

    # Label selected countries in black for visibility
    highlight_black = ["CHN", "USA", "DEU", "CHE", "POL", "TUR", "GBR", "HRV", "SWE", "KOR", "RUS", "ARE"]
    for i, row in merged_df.iterrows():
        if row["country_iso3"] in highlight_black:
                plt.text(np.log10(row["gdp_per_capita"]), row["eci"], row["country_iso3"],
                        fontsize=9, ha='right', va='bottom', color='black')
    # Label selected countries in red for visibility
    highlight_red = []
    #highlight_red = ["GNQ", "TCD", "SDN", "RWA", "TGO", "MLI", "GIN", "KWT", "PNG", "LBR", "SLE", "LBY", "COD", "MNG", "OMN"]
    for i, row in merged_df.iterrows():
        if row["country_iso3"] in highlight_red:
            plt.text(np.log10(row["gdp_per_capita"]), row["eci"], row["country_iso3"],
                    fontsize=9, ha='right', va='bottom', color='red')

    plt.xlabel(f"GDP per capita ($)")
    plt.ylabel(f"Energy Complexity Index")
    if supplementary == 1:
        plt.title(f"Energy Complexity Index vs GDP per Capita in {year} (with supplementary Dataset)")
    else:
        plt.title(f"Energy Complexity Index vs GDP per Capita in {year}")

    start_power = 2
    end_power = 5 
    ticks = np.arange(start_power, end_power + 1) 
    plt.xticks(ticks, [f"{int(10**t):,}" for t in ticks])
    plt.xlim(start_power - 0.2, end_power + 0.2)

    plt.axhline(0, color='black', linestyle='--', linewidth=1, alpha=0.5, label='ECI value of 0')

    if supplementary == 1:
        output_dir = f"{save_folder}/{year}/supplementary/"
        os.makedirs(output_dir, exist_ok=True)
        save_path = os.path.join(output_dir, f"ECI_vs_GDPperCapita_Energy_supplementary_{year}.png")
        plt.savefig(save_path, dpi=300)
    else:
        output_dir = f"{save_folder}/{year}/Energy/"
        os.makedirs(output_dir, exist_ok=True)
        save_path = os.path.join(output_dir, f"ECI_vs_GDPperCapita_Energy_{year}.png")
        plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"ECI vs GDP per Capita Scatter Plot for year {year} saved.")

def ECI_Scatter_Energy(cdata, supplementary, year, save_folder):
    Energy_data = pd.read_csv("01_Data/Energy_use_World_Bank.csv", skiprows=4)    
    Energy_year = Energy_data[["Country Name", "Country Code", f"{year}"]]
    Energy_year = Energy_year.rename(columns={"Country Code": "country_iso3", f"{year}": "energy_use_per_capita"})
    
    eci_country = cdata[['country_iso3', 'year', 'eci']].copy().drop_duplicates()
    eci_year = eci_country[eci_country["year"] == year].dropna(subset=["eci"])

    merged_df = eci_year.merge(Energy_year, on="country_iso3")
    
    missing_countries = merged_df[merged_df["energy_use_per_capita"].isna()]["country_iso3"].unique()
    if len(missing_countries) > 0:
        print("Warning: Missing Energy Use per capita data for countries:", missing_countries)

    plt.figure(figsize=(12, 4.5))
    x = np.log10(merged_df["energy_use_per_capita"])
    y = merged_df["eci"]
    plt.ylim(-5, 4)

    plt.scatter(x, y, alpha=0.7)

    # Label selected countries in black for visibility
    highlight_black = ["CHN", "USA", "DEU", "CHE", "POL", "TUR", "GBR", "HRV", "SWE", "KOR", "RUS", "ARE"]
    for i, row in merged_df.iterrows():
        if row["country_iso3"] in highlight_black:
            plt.text(np.log10(row["energy_use_per_capita"]), row["eci"], row["country_iso3"],
                    fontsize=9, ha='right', va='bottom', color='black')
    # Label selected countries in red for visibility
    #highlight_red = ["GNQ", "TCD", "SDN", "RWA", "TGO", "MLI", "GIN", "KWT", "PNG", "LBR", "SLE", "LBY", "COD", "MNG", "OMN"]
    highlight_red = []
    for i, row in merged_df.iterrows():
        if row["country_iso3"] in highlight_red:
            plt.text(np.log10(row["energy_use_per_capita"]), row["eci"], row["country_iso3"],
                    fontsize=9, ha='right', va='bottom', color='red')

    plt.xlabel(f"Energy use (kg of oil equivalent per capita)")
    plt.ylabel(f"Energy Complexity Index")
    if supplementary == 1:
        plt.title(f"Energy Complexity Index vs Energy use per Capita in {year} (with supplementary Dataset)")
    else:
        plt.title(f"Energy Complexity Index vs Energy use per Capita in {year}")


    start_power = 2
    end_power = 4 
    ticks = np.arange(start_power, end_power + 1) 
    plt.xticks(ticks, [f"{int(10**t):,}" for t in ticks])
    plt.xlim(start_power - 0.2, end_power + 0.2)

    plt.axhline(0, color='black', linestyle='--', linewidth=1, alpha=0.5, label='ECI value of 0')

    if supplementary == 1:
        output_dir = f"{save_folder}/{year}/supplementary/"
        os.makedirs(output_dir, exist_ok=True)
        save_path = os.path.join(output_dir, f"ECI_vs_EnergyperCapita_Energy_supplementary_{year}.png")
        plt.savefig(save_path, dpi=300)
    else:
        output_dir = f"{save_folder}/{year}/Energy/"
        os.makedirs(output_dir, exist_ok=True)
        save_path = os.path.join(output_dir, f"ECI_vs_EnergyperCapita_Energy_{year}.png")
        plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"ECI vs Energy use per Capita Scatter Plot for year {year} saved.")

def ECI_Scatter_Emissions(cdata, year, save_folder, supplementary=0):
    emissions_data = pd.read_csv("01_Data/CO2_Emissions_World_Bank.csv", skiprows=4)
    year_col = str(year)
    em_year = emissions_data[["Country Code", year_col]].copy()
    em_year = em_year.rename(columns={"Country Code": "country_iso3", year_col: "emissions_pc"})    
    # Convert emissions to numeric (handles cases where data might be missing/strings)
    em_year["emissions_pc"] = pd.to_numeric(em_year["emissions_pc"], errors='coerce')

    eci_country = cdata[['country_iso3', 'year', 'eci']].copy().drop_duplicates()
    eci_year = eci_country[eci_country["year"] == year].dropna(subset=["eci"])

    merged_df = eci_year.merge(em_year, on="country_iso3")
    merged_df = merged_df.dropna(subset=["emissions_pc"]) # Remove countries with no emission data

    plt.figure(figsize=(12, 5))
    x = np.log10(merged_df["emissions_pc"])
    y = merged_df["eci"]    
    plt.scatter(x, y, alpha=0.6, edgecolors='w', s=60)

    # Label selected countries
    highlight_black = ["CHN", "USA", "DEU", "CHE", "POL", "TUR", "GBR", "SWE", "KOR", "RUS", "ARE"]
    for i, row in merged_df.iterrows():
        if row["country_iso3"] in highlight_black:
            plt.text(np.log10(row["emissions_pc"]), row["eci"], row["country_iso3"],
                     fontsize=9, ha='left', va='bottom', fontweight='bold')

    plt.axhline(0, color='black', linestyle='--', linewidth=0.8, alpha=0.5)
    plt.ylabel("Energy Complexity Index (ECI)")
    plt.xlabel("CO2 Emissions per capita (t CO2e, Log Scale)")
    
    start_pow, end_pow = -2, 2
    ticks = np.arange(start_pow, end_pow + 1)
    plt.xticks(ticks, [f"{10.0**t}" for t in ticks])
    plt.xlim(start_pow - 0.1, end_pow + 0.1)
    plt.ylim(-4, 3)

    title_suffix = " (with supplementary Dataset)" if supplementary == 1 else ""
    plt.title(f"ECI vs. CO2 Emissions per Capita in {year}{title_suffix}")
    plt.grid(True, which="both", ls="-", alpha=0.2)

    sub_folder = "supplementary" if supplementary == 1 else "Energy"
    output_dir = os.path.join(save_folder, str(year), sub_folder)
    os.makedirs(output_dir, exist_ok=True)
    
    save_path = os.path.join(output_dir, f"ECI_vs_Emissions_{year}.png")
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()

##############################################################################################################################
##############################################################################################################################

'''Example Usage'''
'''
years = [1996, 2003, 2007, 2013, 2019, 2022, 2023]
supplementary = 1
save_folder = "03_Results"

for year in years:
    # 2. Initialize an empty list to store the dataframes
    df = []
    if supplementary:
        # Path for Supplementary Data
        path = f"{save_folder}/{year}/supplementary/eci_country_results_Energy_supplementary_{year}.csv"
    else:
        # Path for Core Energy Data (Check if filename is correct in your folder!)
        # Usually it follows the pattern: eci_country_results_Energy_{year}.csv
        path = f"{save_folder}/{year}/Energy/eci_country_results_Energy_{year}.csv"

    if os.path.exists(path):
        df = pd.read_csv(path)
        # Ensure the 'year' column exists (good practice for merging later)
        df['year'] = year 
    else:
        print(f"Warning: File not found: {path}")

    ECI_Scatter_Population(df, supplementary, year, save_folder)

    #ECI_Scatter_GDP(df, supplementary, year, save_folder)

    #ECI_Scatter_Energy(df, supplementary, year, save_folder)

    #ECI_Scatter_Emissions(df, year, save_folder, supplementary)

'''