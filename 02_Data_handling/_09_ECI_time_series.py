import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.cm as cm  # Import colormaps
import numpy as np
import math

def ECI_time_series(years, supplementary, population, save_folder):
    dfs = []
    first_year = years[0]
    last_year = years[-1]
    save_path = f"{save_folder}/Time_Series"
    for year in years:
        if supplementary:
            file_path = f"{save_folder}/{year}/supplementary/eci_results_Energy_supplementary_{year}.csv"
        else:
            file_path = f"{save_folder}/{year}/Energy/eci_results_Energy_{year}.csv"
        
        df = pd.read_csv(file_path)

        if population != 1:
            country_codes = pd.read_csv("01_Data/BACI/country_codes_V202501.csv")
            country_codes = country_codes[['country_code','country_iso3']]
            df = pd.merge(df, country_codes, left_on='location_code', right_on='country_code', how='left', suffixes=('', '_y'))
        
        df = df[['country_iso3', 'eci']].dropna()
        df = df.drop_duplicates(subset=['eci'])
        df = df.rename(columns={"eci": f"eci_{year}"})
        df = df[['country_iso3', f"eci_{year}"]]
        dfs.append(df)

        print(f"Loaded {file_path}, shape={df.shape}")

    merged = dfs[0]
    for df in dfs[1:]:
        merged = merged.merge(df, on="country_iso3", how="outer")

    for year in years:
        merged[f"eci_rank_{year}"] = merged[f"eci_{year}"].rank(ascending=False, method='min')
        
    merged = merged.replace(r'^\s*$', np.nan, regex=True)

    country_names = pd.read_csv("01_Data/BACI/country_codes_V202501.csv")
    country_names = country_names[['country_iso3', 'country_name']]
    merged = pd.merge(merged, country_names, on='country_iso3', how='left')
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
    ax.invert_yaxis()

    for _, row in df.iterrows():
        ranks = [row.get(f"eci_rank_{y}", np.nan) for y in years]
        if any(pd.isna(x) for x in ranks):
            continue
        plt.plot(years, ranks, marker="o", linewidth=1.5, alpha=0.7)
        plt.text(years[-1] + 0.1, ranks[-1], row["country_name"], fontsize=8, va="center")

    plt.xticks(years)
    plt.xticks(rotation=45, ha="right")

    plt.ylabel("ECI Rank")
    if supplementary:
        plt.title(f"Energy Complexity Index (ECI) Time Series {first_year}-{last_year} (with supplementary Dataset)")
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
    plt.xticks(rotation=75, ha="right")
    plt.ylim(0, 140)

    plt.ylabel("ECI Rank")
    
    if supplementary:
        plt.title(f"Top 20 Countries by ECI Rank time series {first_year}-{last_year} (with supplementary Energy Products)")
    else:
        plt.title(f"Top 20 Countries by ECI Rank time series {first_year}-{last_year}")

    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()

    output_dir = f"{save_path_2}/{first_year}-{last_year}/"
    os.makedirs(output_dir, exist_ok=True)
    if supplementary:
        if first == 1:
            save_path = os.path.join(output_dir, f"Top_20_ECI_time_series_Energy_supplementary_First_{first_year}-{last_year}.png")
        else:
            save_path = os.path.join(output_dir, f"Top_20_ECI_time_series_Energy_supplementary_Last_{first_year}-{last_year}.png")
    else:
        if first == 1:
            save_path = os.path.join(output_dir, f"Top_20_ECI_time_series_Energy_First_{first_year}-{last_year}.png")
        else:
            save_path = os.path.join(output_dir, f"Top_20_ECI_time_series_Energy_Last_{first_year}-{last_year}.png")

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
    plt.xticks(rotation=75, ha="right")
    plt.ylim(0, 140)

    plt.ylabel("ECI Rank")
    if supplementary:
        plt.title(f"Bottom 20 Countries by ECI Rank time series {first_year}-{last_year} (with supplementary Energy Products)")
    else:
        plt.title(f"Bottom 20 Countries by ECI Rank time series {first_year}-{last_year}")

    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    

    output_dir = f"{save_path_2}/{first_year}-{last_year}/"
    os.makedirs(output_dir, exist_ok=True)
    if supplementary:
        if first == 1:
            save_path = os.path.join(output_dir, f"Bottom_20_ECI_time_series_Energy_supplementary_First_{first_year}-{last_year}.png")
        else:
            save_path = os.path.join(output_dir, f"Bottom_20_ECI_time_series_Energy_supplementary_Last_{first_year}-{last_year}.png")
    else:
        if first == 1:
            save_path = os.path.join(output_dir, f"Bottom_20_ECI_time_series_Energy_First_{first_year}-{last_year}.png")
        else:
            save_path = os.path.join(output_dir, f"Bottom_20_ECI_time_series_Energy_Last_{first_year}-{last_year}.png")

    plt.savefig(save_path, dpi=300)
    plt.close()

def ECI_time_line_singular_plot(df, country_iso3, years, save_folder, supplementary):
    first_year = years[0]
    last_year = years[-1]
    save_path_2 = f"{save_folder}/Time_Series"
  
    for iso3 in country_iso3:
        country_row = df[df['country_iso3'] == iso3]
        if country_row.empty:
            print(f"No data for country ISO3: {iso3}")
            continue
        
        plt.figure(figsize=(10, 6))
        ax = plt.gca()
        ax.invert_yaxis()

        ranks = [country_row.iloc[0].get(f"eci_rank_{y}", np.nan) for y in years]
        if pd.isna(ranks[0]):
            ranks[0] = 150

        for i in range(1, len(ranks)):
            if pd.isna(ranks[i]):
                ranks[i] = ranks[i-1]

        plt.plot(years, ranks, marker="o", linewidth=2, color='blue')
        ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        plt.xticks(years, rotation=45)
        plt.ylabel("ECI Rank")
        country_name = country_row.iloc[0]['country_name']
        if supplementary:
            plt.title(f"ECI Rank Time Series for {country_name} ({iso3}) {first_year}-{last_year} (with supplementary Dataset)")
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

        plt.figure(figsize=(10, 6))
        ax = plt.gca()
        country_name = country_row.iloc[0]['country_name']

        eci_values = [country_row.iloc[0].get(f"eci_{y}", np.nan) for y in years]
        if pd.isna(eci_values[0]):
            eci_values[0] = -5.0

        for i in range(1, len(eci_values)):
            if pd.isna(eci_values[i]):
                eci_values[i] = eci_values[i-1]

        plt.plot(years, eci_values, marker="o", linewidth=2, color='green')
        plt.xticks(years, rotation=45)
        plt.ylabel("ECI Value")
        if supplementary:
            plt.title(f"ECI Value Time Series for {country_name} ({iso3}) {first_year}-{last_year} (with supplementary Dataset)")
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
    
    if isinstance(country_iso3_list, str):
        country_iso3_list = [country_iso3_list]
    try:
        gdp_data = pd.read_csv("01_Data/GDP_World_Bank.csv", skiprows=4)
    except FileNotFoundError:
        print("Error: GDP file not found at '01_Data/GDP_World_Bank.csv'")
        return

    first_year = years[0]
    last_year = years[-1]

    for iso3 in country_iso3_list:
        country_row = df[df['country_iso3'] == iso3]
        if country_row.empty:
            print(f"Skipping {iso3}: No ECI data found in dataset.")
            continue
        
        gdp_country = gdp_data[gdp_data["Country Code"] == iso3]
        if gdp_country.empty:
            print(f"Skipping {iso3}: No GDP data found in World Bank file.")
            continue

        cols_to_keep = ["Country Code"] + [str(y) for y in years if str(y) in gdp_country.columns]
        
        if len(cols_to_keep) <= 1:
            print(f"Warning: No matching GDP years found for {iso3}")
            continue

        gdp_subset = gdp_country[cols_to_keep]
        gdp_long = gdp_subset.melt(id_vars=["Country Code"], 
                                   var_name="year", 
                                   value_name="gdp_per_capita")
        gdp_long["year"] = gdp_long["year"].astype(int)

        eci_data_list = []
        for y in years:
            col_name = f"eci_{y}"
            
            if col_name in country_row.columns:
                val = country_row[col_name].values[0]
                
                if pd.notna(val):
                    eci_data_list.append({'year': y, 'eci': val})
        
        eci_subset = pd.DataFrame(eci_data_list)

        if eci_subset.empty:
            print(f"Warning: No valid ECI values for {iso3} in selected years.")
            continue
            
        merged_df = pd.merge(eci_subset, gdp_long, on="year")
        merged_df = merged_df.sort_values("year")

        if merged_df.empty:
            print(f"Warning: No overlapping ECI and GDP data found for {iso3}")
            continue
        
        plt.figure(figsize=(10, 6))

        merged_df = merged_df[merged_df["gdp_per_capita"] > 0]
        
        x = np.log10(merged_df["gdp_per_capita"])
        y = merged_df["eci"]

        plt.plot(x, y, linestyle='-', marker='o', alpha=0.6, label=iso3)

        for i, row in merged_df.iterrows():
            is_start = (row['year'] == merged_df['year'].min())
            is_end = (row['year'] == merged_df['year'].max())
            is_interval = (row['year'] % 2 == 0)
            
            if is_start or is_end or is_interval:
                plt.text(np.log10(row["gdp_per_capita"]), row["eci"], str(int(row["year"])),
                         fontsize=9, ha='right', va='bottom', color='black')

        plt.xlabel(f"GDP per capita (Log Scale)")
        plt.ylabel(f"Energy Complexity Index")
        
        dataset_tag = " (with supplementary Dataset)" if supplementary == 1 else ""
        plt.title(f"ECI vs GDP Trajectory: {iso3} ({first_year}-{last_year}){dataset_tag}")

        ticks = np.arange(3, 6)
        plt.xticks(ticks, [f"$10^{int(t)}$" for t in ticks])
        plt.grid(True, linestyle='--', alpha=0.5)

        subdir = "supplementary" if supplementary == 1 else "Energy"
        output_dir = os.path.join(save_folder, f"Time_Series/{first_year}-{last_year}/GDP_Trajectory", subdir)
        os.makedirs(output_dir, exist_ok=True)

        filename = f"ECI_GDP_Trajectory_{iso3}_{first_year}-{last_year}.png"
        save_path = os.path.join(output_dir, filename)

        plt.savefig(save_path, dpi=300)
        plt.close()

        print(f"GDP Trajectory plot saved for {iso3}")        

def ECI_Energy_time_line_singular_plot(df, country_iso3_list, years, save_folder, supplementary):
    if isinstance(country_iso3_list, str):
        country_iso3_list = [country_iso3_list]

    try:
        energy_data = pd.read_csv("01_Data/Energy_use_World_Bank.csv", skiprows=4)
    except FileNotFoundError:
        print("Error: Energy file not found at '01_Data/Energy_use_World_Bank.csv'")
        return

    first_year = years[0]
    last_year = years[-1]

    for iso3 in country_iso3_list:    
        country_row = df[df['country_iso3'] == iso3]
        if country_row.empty:
            print(f"Skipping {iso3}: No ECI data found in dataset.")
            continue

        energy_country = energy_data[energy_data["Country Code"] == iso3]
        if energy_country.empty:
            print(f"Skipping {iso3}: No Energy data found in World Bank file.")
            continue
        cols_to_keep = ["Country Code"] + [str(y) for y in years if str(y) in energy_country.columns]
        
        if len(cols_to_keep) <= 1:
            print(f"Warning: No matching Energy years found for {iso3}")
            continue

        energy_subset = energy_country[cols_to_keep]
        energy_long = energy_subset.melt(id_vars=["Country Code"], 
                                         var_name="year", 
                                         value_name="energy_use_per_capita")
        energy_long["year"] = energy_long["year"].astype(int)
        eci_data_list = []
        for y in years:
            col_name = f"eci_{y}" 

            if col_name in country_row.columns:
                val = country_row[col_name].values[0] 
                if pd.notna(val):
                    eci_data_list.append({'year': y, 'eci': val})
        
        eci_subset = pd.DataFrame(eci_data_list)

        if eci_subset.empty:
            print(f"Warning: No valid ECI values for {iso3} in selected years.")
            continue
            
        merged_df = pd.merge(eci_subset, energy_long, on="year")
        merged_df = merged_df.sort_values("year")

        if merged_df.empty:
            print(f"Warning: No overlapping ECI and Energy data found for {iso3}")
            continue

        plt.figure(figsize=(10, 6))
        merged_df = merged_df[merged_df["energy_use_per_capita"] > 0]
        
        if merged_df.empty:
            print(f"Skipping plot for {iso3}: No positive energy use values available.")
            plt.close()
            continue

        x = np.log10(merged_df["energy_use_per_capita"])
        y = merged_df["eci"]

        plt.plot(x, y, linestyle='-', marker='o', alpha=0.6, label=iso3)

        for i, row in merged_df.iterrows():
            is_start = (row['year'] == merged_df['year'].min())
            is_end = (row['year'] == merged_df['year'].max())
            is_interval = (row['year'] % 2 == 0)
            
            if is_start or is_end or is_interval:
                plt.text(np.log10(row["energy_use_per_capita"]), row["eci"], str(int(row["year"])),
                         fontsize=9, ha='right', va='bottom', color='black')

        plt.xlabel(f"Energy use (kg of oil equivalent per capita) (Log Scale)")
        plt.ylabel(f"Energy Complexity Index")
        
        dataset_tag = " (with supplementary Dataset)" if supplementary == 1 else ""
        plt.title(f"ECI vs Energy Use Trajectory: {iso3} ({first_year}-{last_year}){dataset_tag}")

        x_min, x_max = x.min(), x.max()
        if x_min == x_max:
             plt.xlim(x_min * 0.9, x_max * 1.1)
        else:
             plt.xlim(x_min * 0.9, x_max * 1.1)
    
        plt.grid(True, linestyle='--', alpha=0.5)

        subdir = "supplementary" if supplementary == 1 else "Energy"
        output_dir = os.path.join(save_folder, f"Time_Series/{first_year}-{last_year}/Energy_Trajectory", subdir)
        os.makedirs(output_dir, exist_ok=True)

        filename = f"ECI_Energy_Trajectory_{iso3}_{first_year}-{last_year}.png"
        save_path = os.path.join(output_dir, filename)

        plt.savefig(save_path, dpi=300)
        plt.close()

        print(f"Energy Trajectory plot saved for {iso3}")

def ECI_time_line_plot_selected(df, years, selected_countries, save_folder, supplementary):   
    first_year = years[0]
    last_year = years[-1]
    save_path_2 = f"{save_folder}/Time_Series"
    
    subset = df[df['country_name'].isin(selected_countries)].copy()
    
    if subset.empty:
        print("Warning: No matching countries found in the provided list.")
        return
    
    subset['country_name'] = subset['country_name'].replace({
        "TÃ¼rkiye": "Turkey", 
        "Türkiye": "Turkey"
    })

    # Drop duplicates to fix the "Germany appearing twice" issue
    # This keeps the first occurrence of "Germany" and drops any subsequent rows with the same name
    subset = subset.drop_duplicates(subset=['country_name'], keep='first')
    subset = subset.sort_values(by='country_name')

    num_countries = len(subset)
    
    if num_countries <= 10:
        # Standard distinct colors
        colors = plt.cm.tab10(np.linspace(0, 1, num_countries))
    elif num_countries <= 20:
        # Extended distinct palette (20 colors)
        colors = plt.cm.tab20(np.linspace(0, 1, num_countries))
    else:
        colors = plt.cm.nipy_spectral(np.linspace(0, 1, num_countries))

    plt.figure(figsize=(12, 8))
    ax = plt.gca()
    ax.invert_yaxis()

    for i, (_, row) in enumerate(subset.iterrows()):
        ranks = [row.get(f"eci_rank_{y}", np.nan) for y in years]
        
        if all(pd.isna(x) for x in ranks):
            continue

        label_name = row['country_name']
        plt.plot(years, ranks, marker="o", linewidth=2, alpha=0.8, 
                 label=label_name, color=colors[i])

    plt.xticks(years)
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("ECI Rank")
    
    data_type = "Supplementary" if supplementary else "Core"
    plt.title(f"ECI Rank Evolution: {first_year}–{last_year} (with {data_type} Data)")
    
    plt.grid(True, linestyle="--", alpha=0.5)
    
    n_items = len(subset)
    n_cols = math.ceil(n_items / 2) if n_items > 0 else 1

    plt.legend(
        loc='upper left',              # Anchor point of the legend box
        bbox_to_anchor=(0, -0.15, 1, 0), # (x, y, width, height) relative to axes
        mode="expand",                 # Expand legend to fill the width defined in bbox
        borderaxespad=0,               # No padding between axes and legend
        ncol=n_cols,                   # Dynamic columns for 2 rows
        fontsize='small',
        title="Countries"
    )

    plt.tight_layout()
    plt.subplots_adjust(bottom=0.2)
    
    plt.tight_layout()

    output_dir = f"{save_path_2}/Selected_Comparison/"
    os.makedirs(output_dir, exist_ok=True)
    
    if len(selected_countries) <= 3:
        names_str = "_".join(selected_countries).replace(" ", "")
    else:
        names_str = "Selected_Countries"

    folder_tag = "Energy_supplementary" if supplementary else "Energy"
    filename = f"ECI_Time_Series_{folder_tag}_{names_str}_{first_year}-{last_year}.png"
    save_path = os.path.join(output_dir, filename)

    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"Saved selected time series to {save_path}")

##############################################################################################################################
##############################################################################################################################


''' Example usage '''
'''
#years = [2018, 2019, 2020, 2021, 2022, 2023]
years = [1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 
         2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013,
         2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023]
#years = [2002, 2003, 2004, 2005, 2006]

supplementary = 1  # 1 for supplementary energy products, 0 for all energy products
population = 1  # 1 to include population data, 0 otherwise
first = 1  # 1 to use first year for top/bottom 20, 0 for last year
country_iso3_list = pd.read_csv("01_Data/country_codes_V202501.csv")['country_iso3'].tolist()
save_folder = "03_Results"

# --- Example Usage ---
#countries = ["CHN", "USA", "DEU", "CHE", "POL", "TUR", "GBR", "HRV", "SWE", "KOR", "RUS", "ARE"]
countries = ["China", "United Arab Emirates", "Switzerland", "Germany", "United Kingdom", "Croatia", "Rep. of Korea", "Poland", "Russian Federation", "Sweden", "USA", "TÃ¼rkiye"]

#df = ECI_time_series(years, supplementary, population, save_folder)
if supplementary == 1:
    df = pd.read_csv("03_Results/Time_Series/1996-2023/ECI_time_series_Energy_supplementary_1996-2023.csv")
else:
    df = pd.read_csv("03_Results/Time_Series/1996-2023/ECI_time_series_Energy_1996-2023.csv")
#Netherlands, Spain, China, Denmark, United Kingdom, Japan, Israel, Germany, Italy, Poland, USA, Switzerland, France, Singapore, Austria, Australia, Finland, India, Sweden, Ireland, Rep. of Korea, Sweden, Latvia, Estonia, Belgium, Canada, Slovakia, Slovenia, Hungary, Portugal, New Zealand, Norway, Turkey, Russia, Romania, South Africa, Brazil, Mexico, Czechia, Greece, Bulgaria, Croatia, Lithuania, Ukraine, Argentina, Chile, Colombia, Peru, Venezuela, Ecuador, Costa Rica, Panama, Uruguay
#country_iso3_list = ["NLD", "ESP", "CHN", "DNK", "GBR", "JPN", "ISR", "DEU", "ITA", "POL", "USA", "CHE", "FRA", "SGP", "AUT", "AUS", "FIN", "IND", "SWE", "IRL", "KOR", "LVA", "EST", "BEL", "CAN", "SVK", "SVN", "HUN", "PRT", "NZL", "NOR", "TUR", "RUS", "ROU", "ZAF", "BRA", "MEX", "CZE", "GRC", "BGR", "HRV", "LTU", "UKR", "ARG", "CHL", "COL", "PER", "VEN", "ECU", "CRI", "PAN", "URY"] 
#save_folder = "07_Time_series/Selected_Countries"
#Take all iso3 codes from the dataframe

#ECI_time_line_plot_selected(df, years, countries, save_folder, supplementary)


ECI_time_line_plot(df, years, save_folder, supplementary, first)

#ECI_time_line_singular_plot(df, country_iso3_list, years, save_folder, supplementary)

#ECI_GDP_time_line_singular_plot(df, country_iso3_list, years, save_folder, supplementary)

#ECI_Energy_time_line_singular_plot(df, country_iso3_list, years, save_folder, supplementary)

'''