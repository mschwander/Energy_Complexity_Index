import pandas as pd
import os
import sys

class Tee(object):
    def __init__(self, *files):
        self.files = files
    def write(self, obj):
        for f in self.files:
            f.write(obj)
            f.flush()
    def flush(self):
        for f in self.files:
            f.flush()

years = [1996, 1998, 2001, 2002, 2014, 2023]

countries = {348: "Hungary"}

"""

countries = {
            260: "Fr. South Antarctic Lands",
            296: "Kiribati",
            276: "Germany",
            162: "Christmas Islands",
            666: "Saint Pierre and Miquelon",
            184: "Cocos (Keeling) Islands",}


countries = {124: "Canada",
             528: "Netherlands",
             276: "Germany",}


countries = {162: "Christmas Islands",
            490: "Other Asia, nes",
            398: "Kazakhstan",
            96: "Brunei Darussalam",
            795: "Turkmenistan"}


countries = {251: "France",
             757: "Switzerland",
             152: "Chile",
             40: "Austria",
             156: "China",
             757: "Switzerland",
             705: "Slovenia",
             842: "USA",}
"""

data_path = "04_Results_96_23_09_pop_trade_value_filtering"
yellow = 1

# -----------------------------------------------------------------------

def analyze_country_complexity(years, countries, data_path, yellow):
    #create save_folder in data_path with name ECI_country_additional_information
    save_folder = f"{data_path}/ECI_country_additional_information" 
    for country_code, country_name in countries.items():
        if yellow: 
            dir_path = f"{save_folder}/Yellow"
            log_path = os.path.join(dir_path, f"Additional_information_{country_name}.log")
        else: 
            dir_path = f"{save_folder}/Energy"
            log_path = os.path.join(dir_path, f"Additional_information_{country_name}.log")
        

            # make sure directory exists
        os.makedirs(dir_path, exist_ok=True)

        # open logfile
        logfile = open(log_path, "w")

        # tee stdout/stderr
        tee = Tee(sys.stdout, logfile)
        sys.stdout = tee
        sys.stderr = tee

        for year in years:
            if yellow:
                df = pd.read_csv(f"{data_path}/{year}/Yellow/eci_results_Energy_yellow_{year}.csv")
            else:
                df = pd.read_csv(f"{data_path}/{year}/Energy/eci_results_Energy_{year}.csv")

            #sum together total export values of whole csv
            df['export_value'] = pd.to_numeric(df['export_value'], errors='coerce').fillna(0)
            total_export = df['export_value'].sum()
            total_export = 1000 * total_export  # Convert to dollars

            # We group the full dataframe by product code to get the world total for each item
            global_product_stats = df.groupby('hs_product_code')['export_value'].sum().reset_index()
            global_product_stats['export_value'] = 1000 * global_product_stats['export_value']  # Convert to dollars
            global_product_stats.rename(columns={'export_value': 'global_product_total'}, inplace=True)


            # 1. Filter for the specific country and the latest year (if multiple years exist)
            country_df = df[df['location_code'] == country_code].copy()
            
            if country_df.empty:
                print("Country not found in this year, skipping to next country.")
            else:
                # 2. Basic Stats
                total_export_country = country_df['export_value'].sum()
                total_export_country = 1000 * total_export_country  # Convert to dollars
                # Get all valid ECI values
                valid_eci_values = country_df['eci'].dropna()

                if valid_eci_values.empty:
                    current_eci = None  # Or 0, or "N/A"
                else:
                    current_eci = valid_eci_values.iloc[0] # Grab the very first valid one

                diversity_count = country_df[country_df['mcp'] == 1].shape[0] # Count products they are good at

                print(f"--- Analysis for Country in year {year}: {country_name} ---")
                print(f"Total Export Value of Energy products: ${total_export_country:,.0f}")
                print(f"Total Export Value (All Countries, Energy products): ${total_export:,.0f}")
                print(f"Market Share in Energy products: {total_export_country/total_export:.4%}")
                print(f"Current ECI Score: {current_eci}")
                print(f"Diversity (Products with RCA>1): {diversity_count}")
                # Load product names with columns code and description
                product_codes = pd.read_csv("01_Data/product_codes_HS96_V202501.csv")
                product_codes.rename(columns={'description': 'product_name'}, inplace=True)
                product_codes.rename(columns={'code': 'hs_product_code'}, inplace=True)
                product_codes['hs_product_code'] = pd.to_numeric(product_codes['hs_product_code'], errors='coerce').fillna(0).astype('int64')


                # --- 1. Top Drivers (Pushing ECI UP) ---

                top_drivers = country_df[country_df['mcp'] == 1].sort_values(by='pci', ascending=False).head(10)
                top_drivers['export_value'] = 1000 * top_drivers['export_value']  # Convert to dollars
                # FIX: You must merge the names here, from product codes on code, from top_drivers on hs_product_code
                # Merge the global stats we calculated earlier
                top_drivers = top_drivers.merge(global_product_stats, on='hs_product_code', how='left')
                # Calculate the percentage (Country Export / Global Export)
                top_drivers['market_share'] = top_drivers['export_value'] / top_drivers['global_product_total']
            
                # Format for display (optional: creates a string column 'share_str')
                top_drivers['share_str'] = top_drivers['market_share'].apply(lambda x: f"{x:.2%}")
                
                top_drivers = top_drivers.merge(product_codes[['hs_product_code', 'product_name']], on='hs_product_code', how='left')
                #For each single top product, summarise their total export value of df in dollars


                print(f"\nTop Products Boosting ECI in (High Complexity Products we export) year {year}:")
                print(top_drivers[['product_name', 'pci', 'export_value', 'global_product_total', 'share_str']].to_string(index=False))

                # --- 2. Bottom Drivers (Dragging ECI DOWN) ---
                # YES: We keep mcp=1. We want to see the SIMPLE products we possess.
                bottom_drivers = country_df[country_df['mcp'] == 1].sort_values(by='pci', ascending=True).head(10)
                bottom_drivers['export_value'] = 1000 * bottom_drivers['export_value']  # Convert to dollars
                # FIX: You must merge the global stats here too
                bottom_drivers = bottom_drivers.merge(global_product_stats, on='hs_product_code', how='left')
                # Calculate the percentage (Country Export / Global Export)
                bottom_drivers['market_share'] = bottom_drivers['export_value'] / bottom_drivers['global_product_total']
                # Format for display (optional: creates a string column 'share_str')
                bottom_drivers['share_str'] = bottom_drivers['market_share'].apply(lambda x: f"{x:.4%}")


                # FIX: You must merge the names here too!
                bottom_drivers = bottom_drivers.merge(product_codes[['hs_product_code', 'product_name']], on='hs_product_code', how='left')

                print(f"\nLowest Complexity Products (Commodities causing the 'Drag') in year {year}:")
                print(bottom_drivers[['product_name', 'pci', 'export_value', 'global_product_total', 'share_str']].to_string(index=False))

                #Add some spacing after each year
                print("\n" + "="*60 + "\n")

        # restore stdout/stderr and close file
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        logfile.close()

# Redirect stdout to log file
# Example usage for Country 12
analyze_country_complexity(years, countries, data_path, yellow)

# If you had USA data in there:
# analyze_country_complexity(df, 840)