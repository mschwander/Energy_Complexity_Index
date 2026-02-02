import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def ECI_Distribution(cdata, supplementary, year, save_folder):
    eci_country = cdata[['location_code', 'year', 'eci']].copy().drop_duplicates()
    eci_year = eci_country[eci_country["year"] == year].dropna(subset=["eci"])
    eci_year = eci_year.rename(columns={"location_code": "country_iso3"})

    plt.figure(figsize=(12, 6))
    plt.scatter(eci_year["country_iso3"], eci_year["eci"], alpha=0.7)
    plt.xticks(rotation=75, ha="right")
    if supplementary:
        plt.title(f"Scatter Plot of Energy Complexity Index by Country ({year}) (with supplementary Dataset)")
    else:
        plt.title(f"Scatter Plot of Energy Complexity Index by Country ({year})")
    plt.ylabel("Energy Complexity Index (ECI)")
    plt.xlabel("Country")
    plt.tight_layout()

    if supplementary:
        output_prefix = f"{save_folder}/{year}/supplementary/"
    else:
        output_prefix = f"{save_folder}/{year}/Energy/"

    os.makedirs(os.path.dirname(output_prefix), exist_ok=True)
    if supplementary:
        plt.savefig(f"{output_prefix}ECI_Scatter_Energy_supplementary_{year}.png", dpi=300)
    else:
        plt.savefig(f"{output_prefix}ECI_Scatter_Energy_{year}.png", dpi=300)
    
    plt.close()

    plt.figure(figsize=(8, 6))
    plt.hist(eci_year["eci"], bins=20, color="skyblue", edgecolor="black")
    if supplementary:
        plt.title(f"Histogram of Energy Complexity Index Values ({year}) (with supplementary Dataset)")
    else:
        plt.title(f"Histogram of Energy Complexity Index Values ({year})")
    plt.xlabel("Energy Complexity Index (ECI)")
    plt.ylabel("Frequency")
    plt.tight_layout()
    if supplementary:
        plt.savefig(f"{output_prefix}ECI_Histogram_Energy_supplementary_{year}.png", dpi=300)
    else:
        plt.savefig(f"{output_prefix}ECI_Histogram_Energy_{year}.png", dpi=300)

    plt.close()

    plt.figure(figsize=(8, 6))
    sns.kdeplot(eci_year["eci"], fill=True, color="purple", alpha=0.5)
    if supplementary:
        plt.title(f"Density Plot of Energy Complexity Index Values ({year}) (with supplementary Dataset)")
    else:
        plt.title(f"Density Plot of Energy Complexity Index Values ({year})")
    plt.xlabel("Energy Complexity Index (ECI)")
    plt.ylabel("Density")
    plt.tight_layout()
    if supplementary:
        plt.savefig(f"{output_prefix}ECI_Density_Energy_supplementary_{year}.png", dpi=300)
    else:
        plt.savefig(f"{output_prefix}ECI_Density_Energy_{year}.png", dpi=300)
    plt.close()
    print(f"Saved scatter, histogram, and density plots within folder {output_prefix}")

def ECI_Density_Comparison(cdata, supplementary, years_list, save_folder):
    df_subset = cdata[cdata['year'].isin(years_list)].copy()
    df_subset = df_subset.dropna(subset=['eci'])
    
    plt.figure(figsize=(10, 6))
    years_list.sort()
    
    for year in years_list:
        data_year = df_subset[df_subset['year'] == year]['eci']
        sns.kdeplot(
            data_year, 
            fill=True, 
            alpha=0.1, 
            label=str(year), 
            linewidth=2
        )
    plt.axvline(0, color='black', linestyle='--', linewidth=1, alpha=0.5, label='ECI value of 0')
    dataset_type = "Supplementary" if supplementary else "Core"
    plt.title(f"Evolution of ECI Density: {min(years_list)}–{max(years_list)} (with {dataset_type} Data)", fontsize=14)
    plt.xlabel("Energy Complexity Index (ECI)", fontsize=12)
    plt.ylabel("Density", fontsize=12)
    plt.legend(title="Year")
    plt.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()

    folder_name = "supplementary" if supplementary else "Energy"
    output_dir = os.path.join(save_folder, "Comparisons", folder_name)
    os.makedirs(output_dir, exist_ok=True)
    
    if len(years_list) <= 3:
        years_str = "_".join(map(str, years_list))
    else:
        years_str = f"{min(years_list)}_to_{max(years_list)}"
        
    filename = f"ECI_Density_Comparison_{years_str}_{folder_name}.png"
    save_path = os.path.join(output_dir, filename)

    plt.savefig(save_path, dpi=300)
    plt.close()
    
    print(f"Saved density comparison plot to {save_path}")

##############################################################################################################################
##############################################################################################################################

# --- Example Usage ---
'''
years_list = [1996, 2003, 2007, 2019, 2023]
supplementary = 1
save_folder = "03_Results/"


# 2. Initialize an empty list to store the dataframes
dfs = []

# 3. Loop through years and load data
for year in years_list:
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
        dfs.append(df)
    else:
        print(f"Warning: File not found: {path}")

# 4. Concatenate all into one big dataframe
if dfs:
    cdata = pd.concat(dfs, ignore_index=True)
    print(f"Successfully loaded data for years: {cdata['year'].unique()}")
    
    # 5. Run the function
    # Assuming you have defined the function 'ECI_Density_Comparison' previously
    ECI_Density_Comparison(cdata, supplementary, years_list, save_folder)
else:
    print("No data loaded. Check your paths.")
'''