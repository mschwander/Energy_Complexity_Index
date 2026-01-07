import pandas as pd
import os
from ecomplexity import ecomplexity

def ECI_ecomplexity(df, year, yellow, min_trade, min_val, ubiquity, ll_ubiquity, ul_ubiquity,
                    population, pop_min, trade_value, min_trade_value, global_market_share,
                    min_global_market_share, save_folder):
    # Filter data for year 2023
    data = df[df['year'] == year].copy()
    print("Amount of data before filtering:", len(data))

    if population == 1:
        population_data = pd.read_csv("01_Data/WPP2024_Demographic_Indicators_Medium.csv")

        population_year = population_data[population_data["Time"] == year]

        # Select relevant columns and rename
        population_year = population_year[["ISO3_code", "TPopulation1July"]].rename(
            columns={"ISO3_code": "country_iso3", "TPopulation1July": "population"}
        )
        #take out the ones that don't have iso3 codes
        population_year = population_year.dropna(subset=["country_iso3"])

        population_year["population"] = population_year["population"] * 1000 # includes 'country_iso3', 'population'

        min_pop_countries = population_year[population_year['population'] >= pop_min]['country_iso3'].tolist()
        country_codes = pd.read_csv("01_Data/BACI/country_codes_V202501.csv")
        country_codes = country_codes[['country_code','country_iso3']]
        data = pd.merge(data, country_codes, left_on='location_code', right_on='country_code', how='left')

        data = data[data['country_iso3'].isin(min_pop_countries)]
        #Check how many unique countries are left
        unique_countries = data['location_code'].nunique()
        print(f"Number of unique countries after population filtering with min {pop_min}:", unique_countries)
        print(f"Amount of data after population filtering with minimum 1 Million people:", len(data))

    if trade_value == 1:
        total_trade = data.groupby('location_code')['export_value'].sum()
        total_trade = total_trade.sort_values(ascending=False)
        #save_path = os.path.join("04_Results", "total_trade_by_country_2023.csv")
        #total_trade.to_csv(save_path, header=['total_export_value'])
        #print(f"Saved total trade by country to {save_path}")
        high_trade_countries = total_trade[total_trade >= min_trade_value[year]].index.tolist()
        print("Amount of unique countries before trade value filtering:", data['location_code'].nunique())
        #include only countries with high trade value
        data = data[data['location_code'].isin(high_trade_countries)]
        min_trade_dollar = min_trade_value[year]*1000  # Convert to actual dollar value
        print("Amount of unique countries after trade value filtering:", data['location_code'].nunique())
        print(f"Amount of data after trade value filtering with min {min_trade_dollar} $:", len(data))   
        
    if min_trade[year] == 1:
        data = data[data['export_value'] >= min_val[year]]
        dollar_value = min_val[year]*1000  # Convert to actual dollar value
        print(f"Amount of data after filtering for higher than {dollar_value} $ value per trade:", len(data))

    if ubiquity[year] == 1:
        # Compute ubiquity: number of countries exporting each product
        ubiq = data.groupby('hs_product_code')['location_code'].nunique()
        print("Ubiquity calculated.")
        print(ubiq.describe())
        
        keep_products = ubiq[(ubiq >= ll_ubiquity[year]) & (ubiq <= ul_ubiquity[year])].index    
        data = data[data['hs_product_code'].isin(keep_products)]
        print(f"Amount of data after ubiquity filtering with {ll_ubiquity[year]} and {ul_ubiquity[year]}:", len(data))

    if global_market_share[year] == 1:
        total_world_trade = data['export_value'].sum()
        data['global_market_share'] = data['export_value'] / total_world_trade
        # Keep products with at least a percentage of global share
        data = data[data['global_market_share'] >= min_global_market_share[year]]
        print(f"Amount of data after global market share filtering with min {min_global_market_share[year]}:", len(data))

    # Calculate complexity
    trade_cols = {'time':'year', 'loc':'location_code', 'prod':'hs_product_code', 'val':'export_value'}
    cdata = ecomplexity(data, trade_cols)

    # ['location_code', 'hs_product_code', 'export_value', 'year', 'diversity', 'ubiquity', 'mcp', 'eci', 'pci_x', 'density', 'coi', 'cog', 'rca', 'global_market_share', 'pci_y']
    if yellow == 1:
        output_dir = f"{save_folder}/{year}/Yellow/"
        os.makedirs(output_dir, exist_ok=True)  # create folder if missing
        save_path = os.path.join(output_dir, f"eci_results_Energy_yellow_{year}.csv")
        cdata.to_csv(save_path, index=False)
        print(f"Saved eci_results to {save_folder}/{year}/Yellow/eci_results_Energy_yellow_{year}.csv")
    else:
        output_dir = f"{save_folder}/{year}/Energy/"
        os.makedirs(output_dir, exist_ok=True)  # create folder if missing
        save_path = os.path.join(output_dir, f"eci_results_Energy_{year}.csv")
        cdata.to_csv(save_path, index=False)
        print(f"Saved eci_results to {save_folder}/{year}/Energy/eci_results_Energy_{year}.csv")
        
    return cdata