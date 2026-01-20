import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

def ECI_time_series(years, supplementary, population, save_folder):
    dfs = []  # collect all yearly dataframes
    first_year = years[0]
    last_year = years[-1]
    save_path = f"{save_folder}/Time_Series"
    for year in years:
        # Build file path
        if supplementary:
            file_path = f"{save_folder}/{year}/supplementary/eci_results_Energy_supplementary_{year}.csv"
        else:
            file_path = f"{save_folder}/{year}/Energy/eci_results_Energy_{year}.csv"

        # Load CSV
        df = pd.read_csv(file_path)

        if population != 1:
            country_codes = pd.read_csv("01_Data/BACI/country_codes_V202501.csv")
            country_codes = country_codes[['country_code','country_iso3']]
            df = pd.merge(df, country_codes, left_on='location_code', right_on='country_code', how='left', suffixes=('', '_y'))
            #print("Merged country codes. Ecomplexity_df columns now:", Ecomplexity_df.columns.to_list())

        df = df[['country_iso3', 'eci']].dropna()

        #drop eci duplicates if any
        df = df.drop_duplicates(subset=['eci'])

        # Rename ECI column to include year
        df = df.rename(columns={"eci": f"eci_{year}"})
        

        # Keep only country_iso3 + renamed ECI column

        df = df[['country_iso3', f"eci_{year}"]]

        dfs.append(df)

        print(f"Loaded {file_path}, shape={df.shape}")

    # Merge all years on country_iso3
    merged = dfs[0]
    for df in dfs[1:]:
        merged = merged.merge(df, on="country_iso3", how="outer")

    #print("Final merged dataframe:")
    #print(merged.head())

    #Make a ranking per year of the ECI values
    for year in years:
        merged[f"eci_rank_{year}"] = merged[f"eci_{year}"].rank(ascending=False, method='min')
        
    #Find the places where there is no value, just "" and put in NaN
    #merged = merged.replace("", pd.NA)
    merged = merged.replace(r'^\s*$', np.nan, regex=True)

    #Add country names
    country_names = pd.read_csv("01_Data/BACI/country_codes_V202501.csv")
    country_names = country_names[['country_iso3', 'country_name']]
    merged = pd.merge(merged, country_names, on='country_iso3', how='left')
    #Reorder columns to have country_name and country_iso3 first
    cols = merged.columns.tolist()
    cols = ['country_name', 'country_iso3'] + [col for col in cols if col not in ['country_name', 'country_iso3']]
    merged = merged[cols]


    output_dir = f"{save_path}/{first_year}-{last_year}/"
    os.makedirs(output_dir, exist_ok=True)
    if supplementary:
        save_path = os.path.join(output_dir, f"ECI_time_series_Energy_supplementary_{first_year}-{last_year}.csv")
    else:
        save_path = os.path.join(output_dir, f"ECI_time_series_Energy_{first_year}-{last_year}.csv")

    merged.to_csv(save_path, index=False, na_rep="NaN")
    
    return merged

def ECI_time_line_plot(df, years, save_folder, supplementary, first):
    first_year = years[0]
    last_year = years[-1]
    save_path_2 = f"{save_folder}/Time_Series"
    plt.figure(figsize=(12, 8))
    ax = plt.gca()
    ax.invert_yaxis()  # rank 1 at the top

    for _, row in df.iterrows():
        ranks = [row.get(f"eci_rank_{y}", np.nan) for y in years]
        if any(pd.isna(x) for x in ranks):
            continue  # skip this country if any rank is NaN
        plt.plot(years, ranks, marker="o", linewidth=1.5, alpha=0.7)
        plt.text(years[-1] + 0.1, ranks[-1], row["country_name"], fontsize=8, va="center")

    plt.xticks(years)
    plt.ylabel("ECI Rank")
    if supplementary:
        plt.title(f"Energy Complexity Index (ECI) Time Series {first_year}-{last_year} (supplementary Dataset)")
    else:
        plt.title(f"Energy Complexity Index (ECI) Time Series {first_year}-{last_year}")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()

    output_dir = f"{save_path_2}/{first_year}-{last_year}/"
    os.makedirs(output_dir, exist_ok=True)
    if supplementary:
        save_path = os.path.join(output_dir, f"ECI_time_series_Energy_supplementary_{first_year}-{last_year}.png")
    else:
        save_path = os.path.join(output_dir, f"ECI_time_series_Energy_{first_year}-{last_year}.png")

    plt.savefig(save_path, dpi=300)
    plt.close()

    if first == 0:
        # Select top and bottom 20 by final year rank
        top_20 = df.nsmallest(20, f"eci_rank_{last_year}")
        bottom_20 = df.nlargest(20, f"eci_rank_{last_year}")
    else:            
        top_20 = df.nsmallest(20, f"eci_rank_{first_year}")
        bottom_20 = df.nlargest(20, f"eci_rank_{first_year}")

    # --- Top 20 Plot ---
    plt.figure(figsize=(12, 8))
    ax = plt.gca()
    ax.invert_yaxis()
    for _, row in top_20.iterrows():
        ranks = [row[f"eci_rank_{y}"] for y in years]
        if any(pd.isna(ranks)):
            continue
        plt.plot(years, ranks, marker="o", linewidth=1.5, alpha=0.8)
        plt.text(years[-1] + 0.1, ranks[-1], row["country_name"], fontsize=8, va="center")
    plt.xticks(years)
    plt.ylabel("ECI Rank")
    plt.ylim(0, 75)  # or ax.set_ylim(0, 75) if you're using subplots

    if supplementary:
        plt.title(f"Top 20 Countries by ECI Rank time series {first_year}-{last_year} (supplementary Energy Products)")
    else:
        plt.title(f"Top 20 Countries by ECI Rank time series {first_year}-{last_year}")

    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()

    output_dir = f"{save_path_2}/{first_year}-{last_year}/"
    os.makedirs(output_dir, exist_ok=True)
    if supplementary:
        save_path = os.path.join(output_dir, f"Top_20_ECI_time_series_Energy_supplementary_{first_year}-{last_year}.png")
    else:
        save_path = os.path.join(output_dir, f"Top_20_ECI_time_series_Energy_{first_year}-{last_year}.png")

    plt.savefig(save_path, dpi=300)
    plt.close()

    # --- Bottom 20 Plot ---
    plt.figure(figsize=(12, 8))
    ax = plt.gca()
    ax.invert_yaxis()
    for _, row in bottom_20.iterrows():
        ranks = [row[f"eci_rank_{y}"] for y in years]
        if any(pd.isna(ranks)):
            continue
        plt.plot(years, ranks, marker="o", linewidth=1.5, alpha=0.8)
        plt.text(years[-1] + 0.1, ranks[-1], row["country_name"], fontsize=8, va="center")
    plt.xticks(years)
    plt.ylabel("ECI Rank")
    if supplementary:
        plt.title(f"Bottom 20 Countries by ECI Rank time series {first_year}-{last_year} (supplementary Energy Products)")
    else:
        plt.title(f"Bottom 20 Countries by ECI Rank time series {first_year}-{last_year}")

    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()

    output_dir = f"{save_path_2}/{first_year}-{last_year}/"
    os.makedirs(output_dir, exist_ok=True)
    if supplementary:
        save_path = os.path.join(output_dir, f"Bottom_20_ECI_time_series_Energy_supplementary_{first_year}-{last_year}.png")
    else:
        save_path = os.path.join(output_dir, f"Bottom_20_ECI_time_series_Energy_{first_year}-{last_year}.png")

    plt.savefig(save_path, dpi=300)
    plt.close()

def ECI_time_line_singular_plot(df, country_iso3, years, save_folder, supplementary):
    first_year = years[0]
    last_year = years[-1]
    save_path_2 = f"{save_folder}/Time_Series"
    #country_iso3 is a list of country ISO3 codes to plot, e.g., ["USA", "CHN"]
    #each country gets its own plot
    for iso3 in country_iso3:
        country_row = df[df['country_iso3'] == iso3]
        if country_row.empty:# no data for this country
            print(f"No data for country ISO3: {iso3}")
            continue
        
        plt.figure(figsize=(10, 6))
        ax = plt.gca()
        ax.invert_yaxis()

        ranks = [country_row.iloc[0].get(f"eci_rank_{y}", np.nan) for y in years]
        # --- NEW LOGIC: Handle NaNs ---
        # 1. Handle the first value (First year missing -> 150)
        if pd.isna(ranks[0]):
            ranks[0] = 150

        # 2. Handle subsequent values (Missing -> use previous year)
        for i in range(1, len(ranks)):
            if pd.isna(ranks[i]):
                ranks[i] = ranks[i-1]
        # -------------------------------

        plt.plot(years, ranks, marker="o", linewidth=2, color='blue')
        #make xticks 45 degrees
        ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        plt.xticks(years, rotation=45)
        plt.ylabel("ECI Rank")
        country_name = country_row.iloc[0]['country_name']
        if supplementary:
            plt.title(f"ECI Rank Time Series for {country_name} ({iso3}) {first_year}-{last_year} (supplementary Dataset)")
        else:
            plt.title(f"ECI Rank Time Series for {country_name} ({iso3}) {first_year}-{last_year}")
        plt.grid(True, linestyle="--", alpha=0.5)
        plt.tight_layout()

        output_dir = f"{save_path_2}/{first_year}-{last_year}/Rank_Singular_Plots/"
        os.makedirs(output_dir, exist_ok=True)
        if supplementary:
            save_path = os.path.join(output_dir, f"ECI_rank_Energy_supplementary_{iso3}_{first_year}-{last_year}.png")
        else:
            save_path = os.path.join(output_dir, f"ECI_rank_Energy_{iso3}_{first_year}-{last_year}.png")

        plt.savefig(save_path, dpi=300)
        plt.close()

        print(f"Saved ECI rank time series plot for country ISO3: {iso3}")

        #Also create a time series plot for ECI values, not ranks, but same plot as above
        #country_name,country_iso3,eci_1996,eci_1997,eci_1998,eci_1999,eci_2000,eci_2001,eci_2002,eci_2003,eci_2004,eci_2005,eci_2006,eci_2007,eci_2008,eci_2009,eci_2010,eci_2011,eci_2012,eci_2013,eci_2014,eci_2015,eci_2016,eci_2017,eci_2018,eci_2019,eci_2020,eci_2021,eci_2022,eci_2023,eci_rank_1996,eci_rank_1997,eci_rank_1998,eci_rank_1999,eci_rank_2000,eci_rank_2001,eci_rank_2002,eci_rank_2003,eci_rank_2004,eci_rank_2005,eci_rank_2006,eci_rank_2007,eci_rank_2008,eci_rank_2009,eci_rank_2010,eci_rank_2011,eci_rank_2012,eci_rank_2013,eci_rank_2014,eci_rank_2015,eci_rank_2016,eci_rank_2017,eci_rank_2018,eci_rank_2019,eci_rank_2020,eci_rank_2021,eci_rank_2022,eci_rank_2023
        #Afghanistan,AFG,NaN,NaN,NaN,NaN,NaN,NaN,NaN,NaN,NaN,NaN,NaN,NaN,NaN,NaN,NaN,NaN,NaN,NaN,NaN,NaN,NaN,NaN,NaN,-0.8869252646911143,NaN,NaN,NaN,NaN,NaN,NaN,NaN,NaN,NaN,NaN,NaN,NaN,NaN,NaN,NaN,NaN,NaN,NaN,NaN,NaN,NaN,NaN,NaN,NaN,NaN,NaN,NaN,103.0,NaN,NaN,NaN,NaN
        
        plt.figure(figsize=(10, 6))
        ax = plt.gca()
        country_name = country_row.iloc[0]['country_name']

        eci_values = [country_row.iloc[0].get(f"eci_{y}", np.nan) for y in years]
        # --- NEW LOGIC: Handle NaNs for ECI Values ---
        # 1. Handle the first value (First year missing -> -5)
        if pd.isna(eci_values[0]):
            eci_values[0] = -5.0

        # 2. Handle subsequent values (Missing -> use previous year)
        for i in range(1, len(eci_values)):
            if pd.isna(eci_values[i]):
                eci_values[i] = eci_values[i-1]
        # ---------------------------------------------

        plt.plot(years, eci_values, marker="o", linewidth=2, color='green')
        plt.xticks(years, rotation=45)
        plt.ylabel("ECI Value")
        if supplementary:
            plt.title(f"ECI Value Time Series for {country_name} ({iso3}) {first_year}-{last_year} (supplementary Dataset)")
        else:
            plt.title(f"ECI Value Time Series for {country_name} ({iso3}) {first_year}-{last_year}")
        plt.grid(True, linestyle="--", alpha=0.5)
        plt.tight_layout()
        output_dir = f"{save_path_2}/{first_year}-{last_year}/Value_Singular_Plots/"
        os.makedirs(output_dir, exist_ok=True)
        if supplementary:
            save_path = os.path.join(output_dir, f"ECI_value_Energy_supplementary_{iso3}_{first_year}-{last_year}.png")
        else:
            save_path = os.path.join(output_dir, f"ECI_value_Energy_{iso3}_{first_year}-{last_year}.png")
        plt.savefig(save_path, dpi=300)
        plt.close()
        print(f"Saved ECI value time series plot for country ISO3: {iso3}")

def ECI_GDP_time_line_singular_plot(df, country_iso3_list, years, save_folder, supplementary):
    """
    Creates time-series trajectory plots (GDP vs ECI) for a list of countries.
    
    Parameters:
    - df: DataFrame containing ECI data in WIDE format (cols: 'country_iso3', 'eci_2002', etc.)
    - country_iso3_list: List of strings (e.g., ["USA", "CHN"]) or single string
    - years: List of integers representing the years to include (e.g., range(2000, 2020))
    - save_folder: String, path to the output directory
    - supplementary: Integer (1 or 0), flag for folder/title naming
    """

    # Handle case where user passes a single string instead of a list
    if isinstance(country_iso3_list, str):
        country_iso3_list = [country_iso3_list]

    # 1. Load GDP per capita data
    # Based on your snippet, the header is on row 5 (index 4), so skiprows=4 is correct
    try:
        gdp_data = pd.read_csv("01_Data/GDP_World_Bank.csv", skiprows=4)
    except FileNotFoundError:
        print("Error: GDP file not found at '01_Data/GDP_World_Bank.csv'")
        return

    first_year = years[0]
    last_year = years[-1]

    # Loop through each country in the provided list
    for iso3 in country_iso3_list:
        
        # --- Check ECI Data Availability ---
        country_row = df[df['country_iso3'] == iso3]
        if country_row.empty:
            print(f"Skipping {iso3}: No ECI data found in dataset.")
            continue

        # --- Check GDP Data Availability ---
        gdp_country = gdp_data[gdp_data["Country Code"] == iso3]
        if gdp_country.empty:
            print(f"Skipping {iso3}: No GDP data found in World Bank file.")
            continue

        # 2. Process GDP Data (Wide to Long)
        # We only keep columns that match the requested years
        cols_to_keep = ["Country Code"] + [str(y) for y in years if str(y) in gdp_country.columns]
        
        if len(cols_to_keep) <= 1:
            print(f"Warning: No matching GDP years found for {iso3}")
            continue

        gdp_subset = gdp_country[cols_to_keep]
        
        # Melt turns the year columns into rows
        gdp_long = gdp_subset.melt(id_vars=["Country Code"], 
                                   var_name="year", 
                                   value_name="gdp_per_capita")
        gdp_long["year"] = gdp_long["year"].astype(int)

        # 3. Process ECI Data (Wide to Long) - UPDATED FOR YOUR CSV STRUCTURE
        # We manually build a list of {'year': y, 'eci': val} based on columns 'eci_YYYY'
        eci_data_list = []
        for y in years:
            col_name = f"eci_{y}" # Matches your column format: eci_2002, eci_2003...
            
            if col_name in country_row.columns:
                val = country_row[col_name].values[0] # Get the value for that country/year
                
                # Only add if value is not NaN
                if pd.notna(val):
                    eci_data_list.append({'year': y, 'eci': val})
        
        # Create the long-format dataframe
        eci_subset = pd.DataFrame(eci_data_list)

        # 4. Merge ECI with GDP on 'year'
        if eci_subset.empty:
            print(f"Warning: No valid ECI values for {iso3} in selected years.")
            continue
            
        merged_df = pd.merge(eci_subset, gdp_long, on="year")
        merged_df = merged_df.sort_values("year")

        if merged_df.empty:
            print(f"Warning: No overlapping ECI and GDP data found for {iso3}")
            continue

        # 5. Plotting
        plt.figure(figsize=(10, 6))

        # Filter out non-positive GDP to avoid log errors
        merged_df = merged_df[merged_df["gdp_per_capita"] > 0]
        
        x = np.log10(merged_df["gdp_per_capita"])
        y = merged_df["eci"]

        plt.plot(x, y, linestyle='-', marker='o', alpha=0.6, label=iso3)

        # Annotate years
        for i, row in merged_df.iterrows():
            # Annotate start, end, and every second year to avoid clutter
            is_start = (row['year'] == merged_df['year'].min())
            is_end = (row['year'] == merged_df['year'].max())
            is_interval = (row['year'] % 2 == 0)
            
            if is_start or is_end or is_interval:
                plt.text(np.log10(row["gdp_per_capita"]), row["eci"], str(int(row["year"])),
                         fontsize=9, ha='right', va='bottom', color='black')

        plt.xlabel(f"GDP per capita (Log Scale)")
        plt.ylabel(f"Energy Complexity Index")
        
        dataset_tag = " (supplementary Dataset)" if supplementary == 1 else ""
        plt.title(f"ECI vs GDP Trajectory: {iso3} ({first_year}-{last_year}){dataset_tag}")

        # Set x-axis ticks
        ticks = np.arange(3, 6)  # log10(1k) to log10(100k)
        plt.xticks(ticks, [f"$10^{int(t)}$" for t in ticks])
        plt.grid(True, linestyle='--', alpha=0.5)

        # 6. Saving
        subdir = "supplementary" if supplementary == 1 else "Energy"
        output_dir = os.path.join(save_folder, f"Time_Series/GDP_Trajectory/{first_year}-{last_year}", subdir)
        os.makedirs(output_dir, exist_ok=True)

        filename = f"ECI_GDP_Trajectory_{iso3}_{first_year}-{last_year}.png"
        save_path = os.path.join(output_dir, filename)

        plt.savefig(save_path, dpi=300)
        plt.close()

        print(f"GDP Trajectory plot saved for {iso3}")        

def ECI_Energy_time_line_singular_plot(df, country_iso3_list, years, save_folder, supplementary):
    """
    Creates time-series trajectory plots (Energy Use vs ECI) for a list of countries.
    
    Parameters:
    - df: DataFrame containing ECI data in WIDE format (cols: 'country_iso3', 'eci_2002', etc.)
    - country_iso3_list: List of strings (e.g., ["USA", "CHN"]) or single string
    - years: List of integers representing the years to include (e.g., range(2000, 2020))
    - save_folder: String, path to the output directory
    - supplementary: Integer (1 or 0), flag for folder/title naming
    """

    # Handle case where user passes a single string instead of a list
    if isinstance(country_iso3_list, str):
        country_iso3_list = [country_iso3_list]

    # 1. Load Energy Use per capita data
    try:
        energy_data = pd.read_csv("01_Data/Energy_use_World_Bank.csv", skiprows=4)
    except FileNotFoundError:
        print("Error: Energy file not found at '01_Data/Energy_use_World_Bank.csv'")
        return

    first_year = years[0]
    last_year = years[-1]

    # Loop through each country in the provided list
    for iso3 in country_iso3_list:
        
        # --- Check ECI Data Availability ---
        country_row = df[df['country_iso3'] == iso3]
        if country_row.empty:
            print(f"Skipping {iso3}: No ECI data found in dataset.")
            continue

        # --- Check Energy Data Availability ---
        energy_country = energy_data[energy_data["Country Code"] == iso3]
        if energy_country.empty:
            print(f"Skipping {iso3}: No Energy data found in World Bank file.")
            continue

        # 2. Process Energy Data (Wide to Long)
        cols_to_keep = ["Country Code"] + [str(y) for y in years if str(y) in energy_country.columns]
        
        if len(cols_to_keep) <= 1:
            print(f"Warning: No matching Energy years found for {iso3}")
            continue

        energy_subset = energy_country[cols_to_keep]
        
        # Melt turns the year columns into rows
        energy_long = energy_subset.melt(id_vars=["Country Code"], 
                                         var_name="year", 
                                         value_name="energy_use_per_capita")
        energy_long["year"] = energy_long["year"].astype(int)

        # 3. Process ECI Data (Wide to Long)
        # We manually build a list of {'year': y, 'eci': val} based on columns 'eci_YYYY'
        eci_data_list = []
        for y in years:
            col_name = f"eci_{y}" # Matches your column format: eci_2002, eci_2003...
            
            if col_name in country_row.columns:
                val = country_row[col_name].values[0] # Get the value for that country/year
                
                # Only add if value is not NaN
                if pd.notna(val):
                    eci_data_list.append({'year': y, 'eci': val})
        
        # Create the long-format dataframe
        eci_subset = pd.DataFrame(eci_data_list)

        # 4. Merge ECI with Energy on 'year'
        if eci_subset.empty:
            print(f"Warning: No valid ECI values for {iso3} in selected years.")
            continue
            
        merged_df = pd.merge(eci_subset, energy_long, on="year")
        merged_df = merged_df.sort_values("year")

        if merged_df.empty:
            print(f"Warning: No overlapping ECI and Energy data found for {iso3}")
            continue

        # 5. Plotting
        plt.figure(figsize=(10, 6))

        # Filter out non-positive Energy values to avoid log errors
        merged_df = merged_df[merged_df["energy_use_per_capita"] > 0]
        
        if merged_df.empty:
            print(f"Skipping plot for {iso3}: No positive energy use values available.")
            plt.close()
            continue

        x = np.log10(merged_df["energy_use_per_capita"])
        y = merged_df["eci"]

        plt.plot(x, y, linestyle='-', marker='o', alpha=0.6, label=iso3)

        # Annotate years
        for i, row in merged_df.iterrows():
            # Annotate start, end, and every second year to avoid clutter
            is_start = (row['year'] == merged_df['year'].min())
            is_end = (row['year'] == merged_df['year'].max())
            is_interval = (row['year'] % 2 == 0)
            
            if is_start or is_end or is_interval:
                plt.text(np.log10(row["energy_use_per_capita"]), row["eci"], str(int(row["year"])),
                         fontsize=9, ha='right', va='bottom', color='black')

        plt.xlabel(f"Energy use (kg of oil equivalent per capita) (Log Scale)")
        plt.ylabel(f"Energy Complexity Index")
        
        dataset_tag = " (supplementary Dataset)" if supplementary == 1 else ""
        plt.title(f"ECI vs Energy Use Trajectory: {iso3} ({first_year}-{last_year}){dataset_tag}")

        # 1. Dynamic Limits: Zoom in on the specific country's range (+/- 10% padding)
        x_min, x_max = x.min(), x.max()
        if x_min == x_max: # Handle single point case
             plt.xlim(x_min * 0.9, x_max * 1.1)
        else:
             plt.xlim(x_min * 0.9, x_max * 1.1)
        

        plt.grid(True, linestyle='--', alpha=0.5)

        # 6. Saving
        subdir = "supplementary" if supplementary == 1 else "Energy"
        # Changed subfolder name to 'Energy_Trajectory' to distinguish from GDP
        output_dir = os.path.join(save_folder, f"Time_Series/Energy_Trajectory/{first_year}-{last_year}", subdir)
        os.makedirs(output_dir, exist_ok=True)

        filename = f"ECI_Energy_Trajectory_{iso3}_{first_year}-{last_year}.png"
        save_path = os.path.join(output_dir, filename)

        plt.savefig(save_path, dpi=300)
        plt.close()

        print(f"Energy Trajectory plot saved for {iso3}")

''' Example usage '''
'''
#years = [2018, 2019, 2020, 2021, 2022, 2023]
#years = [1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 
#         2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013,
#         2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023]
years = [2002, 2003, 2004, 2005, 2006]

supplementary = 1  # 1 for supplementary energy products, 0 for all energy products
population = 1  # 1 to include population data, 0 otherwise
first = 1  # 1 to use first year for top/bottom 20, 0 for last year
#df = ECI_time_series(years, supplementary, population)

df = pd.read_csv("04_Results_02_06_all_Filters_relative/Time_Series/2002-2006/ECI_time_series_Energy_supplementary_2002-2006.csv")

#df = pd.read_csv("04_Results_All_Filters_251211/Time_Series/1996-2023/ECI_time_series_Energy_1996-2023.csv")
#Netherlands, Spain, China, Denmark, United Kingdom, Japan, Israel, Germany, Italy, Poland, USA, Switzerland, France, Singapore, Austria, Australia, Finland, India, Sweden, Ireland, Rep. of Korea, Sweden, Latvia, Estonia, Belgium, Canada, Slovakia, Slovenia, Hungary, Portugal, New Zealand, Norway, Turkey, Russia, Romania, South Africa, Brazil, Mexico, Czechia, Greece, Bulgaria, Croatia, Lithuania, Ukraine, Argentina, Chile, Colombia, Peru, Venezuela, Ecuador, Costa Rica, Panama, Uruguay
#country_iso3_list = ["NLD", "ESP", "CHN", "DNK", "GBR", "JPN", "ISR", "DEU", "ITA", "POL", "USA", "CHE", "FRA", "SGP", "AUT", "AUS", "FIN", "IND", "SWE", "IRL", "KOR", "LVA", "EST", "BEL", "CAN", "SVK", "SVN", "HUN", "PRT", "NZL", "NOR", "TUR", "RUS", "ROU", "ZAF", "BRA", "MEX", "CZE", "GRC", "BGR", "HRV", "LTU", "UKR", "ARG", "CHL", "COL", "PER", "VEN", "ECU", "CRI", "PAN", "URY"] 
#save_folder = "07_Time_series/Selected_Countries"
#Take all iso3 codes from the dataframe
country_iso3_list = pd.read_csv("01_Data/country_codes_V202501.csv")['country_iso3'].tolist()
save_folder = "04_Results_02_06_all_Filters_relative"

#ECI_time_line_plot(df, years, save_folder, supplementary, first)

#ECI_time_line_singular_plot(df, country_iso3_list, years, save_folder, supplementary)


ECI_GDP_time_line_singular_plot(df, country_iso3_list, years, save_folder, supplementary)

ECI_Energy_time_line_singular_plot(df, country_iso3_list, years, save_folder, supplementary)

'''