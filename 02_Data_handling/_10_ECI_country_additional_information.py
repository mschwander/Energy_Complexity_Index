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

data_path = "03_Results_test"
supplementary = 1
#years = [2002, 2003, 2004, 2005, 2006]
#years = [2007, 2008, 2009, 2010, 2011, 2012]
#years = [2013, 2014, 2015, 2016, 2017, 2018]
years = [2019, 2020, 2021, 2022, 2023]

countries = {728: "South Sudan",
             36: "Australia",
             757: "Switzerland",
             276: "Germany",
             842: "USA",
             156: "China",
             784: "United Arab Emirates",
             643: "Russia",
             #191: "Croatia",
             #826: "United Kingdom",
             #616: "Poland",
             #792: "Turkey",
             }

def analyze_country_complexity(years, countries, data_path, supplementary):
    save_folder = f"{data_path}/ECI_country_additional_information/{years[0]}-{years[-1]}/" 
    for country_code, country_name in countries.items():
        if supplementary: 
            dir_path = f"{save_folder}/supplementary"
            log_path = os.path.join(dir_path, f"Additional_information_{country_name}_supplementary_{years[0]}-{years[-1]}.log")
        else: 
            dir_path = f"{save_folder}/Energy"
            log_path = os.path.join(dir_path, f"Additional_information_{country_name}_{years[0]}-{years[-1]}.log")
        
        os.makedirs(dir_path, exist_ok=True)

        logfile = open(log_path, "w")
        tee = Tee(sys.stdout, logfile)
        sys.stdout = tee
        sys.stderr = tee

        for year in years:
            if supplementary:
                df = pd.read_csv(f"{data_path}/{year}/supplementary/eci_results_Energy_supplementary_{year}.csv")
            else:
                df = pd.read_csv(f"{data_path}/{year}/Energy/eci_results_Energy_{year}.csv")

            df['export_value'] = pd.to_numeric(df['export_value'], errors='coerce').fillna(0)
            total_export = df['export_value'].sum()
            total_export = 1000 * total_export

            global_product_stats = df.groupby('hs_product_code')['export_value'].sum().reset_index()
            global_product_stats['export_value'] = 1000 * global_product_stats['export_value']  # Convert to dollars
            global_product_stats.rename(columns={'export_value': 'global_product_total'}, inplace=True)

            country_df = df[df['location_code'] == country_code].copy()
            
            if country_df.empty:
                print("Country not found in this year, skipping to next country.")
            else:
                total_export_country = country_df['export_value'].sum()
                total_export_country = 1000 * total_export_country
                valid_eci_values = country_df['eci'].dropna()

                if valid_eci_values.empty:
                    current_eci = None 
                else:
                    current_eci = valid_eci_values.iloc[0]
              
                diversity_count = country_df[country_df['mcp'] == 1].shape[0] # Count products they are good at
                #from this, find out how many have positive pci and how many negative pci
                positive_pci_count = country_df[(country_df['mcp'] == 1) & (country_df['pci'] > 0)].shape[0]
                negative_pci_count = country_df[(country_df['mcp'] == 1) & (country_df['pci'] < 0)].shape[0]
                #calculate average of positive pci and negative pci
                avg_positive_pci = country_df[(country_df['mcp'] == 1) & (country_df['pci'] > 0)]['pci'].mean()
                avg_negative_pci = country_df[(country_df['mcp'] == 1) & (country_df['pci'] < 0)]['pci'].mean()
                
                # Calculate sum of exports only where RCA >= 1 (mcp == 1)
                export_value_rca1 = country_df[country_df['mcp'] == 1]['export_value'].sum()
                export_value_rca1 = 1000 * export_value_rca1 # Convert to dollars
                share_rca_1_total = export_value_rca1/total_export_country

                print(f"--- Analysis for Country in year {year}: {country_name} ---")
                print(f"Total Export Value of Energy products: ${total_export_country:,.0f}")
                print(f"Total Export Value (All Countries, Energy products): ${total_export:,.0f}")
                print(f"Market Share in Energy products: {total_export_country/total_export:.4%}")
                print(f"Current ECI Score: {current_eci}")
                print(f"Diversity (Products with RCA>1): {diversity_count}")
                print(f"Number of Products with Positive PCI: {positive_pci_count}")
                print(f"Average Positive PCI of Products with RCA>1: {avg_positive_pci:.4f}")
                print(f"Number of Products with Negative PCI: {negative_pci_count}")
                print(f"Average Negative PCI of Products with RCA>1: {avg_negative_pci:.4f}")
                print(f"Total Export Value (Products with RCA > 1): ${export_value_rca1:,.0f}")
                print(f"Share of products with RCA > 1 of total trade value of country: ${share_rca_1_total:.4%}")


                product_codes = pd.read_csv("01_Data/product_codes_HS96_V202501.csv")
                product_codes.rename(columns={'description': 'product_name', 'code': 'hs_product_code'}, inplace=True)
                product_codes['hs_product_code'] = pd.to_numeric(product_codes['hs_product_code'], errors='coerce').fillna(0).astype('int64')

                if int(year) >= 2017:
                    product_codes_17 = pd.read_csv("01_Data/product_codes_HS17_V202501.csv")
                    product_codes_17.rename(columns={'description': 'product_name', 'code': 'hs_product_code'}, inplace=True)
                    product_codes_17['hs_product_code'] = pd.to_numeric(product_codes_17['hs_product_code'], errors='coerce').fillna(0).astype('int64')

                    mask_17 = product_codes_17['hs_product_code'].astype(str).str.startswith('87')
                    mask_96 = product_codes['hs_product_code'].astype(str).str.startswith('87')
                    hs17_vehicles = product_codes_17[mask_17].copy()
                    product_codes = product_codes[~mask_96].copy()
                    product_codes = pd.concat([product_codes, hs17_vehicles], ignore_index=True)
                
                # --- 1. Top Drivers (Pushing ECI UP) ---
                top_drivers = country_df[country_df['mcp'] == 1].sort_values(by='pci', ascending=False).head(15)
                top_drivers['export_value'] = 1000 * top_drivers['export_value']  # Convert to dollars
                top_drivers = top_drivers.merge(global_product_stats, on='hs_product_code', how='left')
                # Calculate the percentage (Country Export / Global Export)
                top_drivers['market_share'] = top_drivers['export_value'] / top_drivers['global_product_total']
            
                # Format for display (optional: creates a string column 'share_str')
                top_drivers['share_str'] = top_drivers['market_share'].apply(lambda x: f"{x:.2%}")
                
                top_drivers = top_drivers.merge(product_codes[['hs_product_code', 'product_name']], on='hs_product_code', how='left')
                # Truncate product_name to max 30 chars + ".."
                top_drivers['product_name'] = top_drivers['product_name'].apply(lambda x: str(x)[:30] + '..' if len(str(x)) > 30 else x)


                print(f"\nTop Products Boosting ECI in (High Complexity Products we export) year {year}:")
                print(top_drivers[['product_name', 'pci', 'export_value', 'global_product_total', 'share_str']].to_string(index=False))

                # --- 2. Bottom Drivers (Dragging ECI DOWN) ---
                bottom_drivers = country_df[country_df['mcp'] == 1].sort_values(by='pci', ascending=True).head(15)
                bottom_drivers['export_value'] = 1000 * bottom_drivers['export_value']  # Convert to dollars
                bottom_drivers = bottom_drivers.merge(global_product_stats, on='hs_product_code', how='left')
                # Calculate the percentage (Country Export / Global Export)
                bottom_drivers['market_share'] = bottom_drivers['export_value'] / bottom_drivers['global_product_total']
                # Format for display
                bottom_drivers['share_str'] = bottom_drivers['market_share'].apply(lambda x: f"{x:.4%}")
                bottom_drivers = bottom_drivers.merge(product_codes[['hs_product_code', 'product_name']], on='hs_product_code', how='left')
                #Truncate product_name to max 30 chars + ".."
                bottom_drivers['product_name'] = bottom_drivers['product_name'].apply(lambda x: str(x)[:30] + '..' if len(str(x)) > 30 else x)

                print(f"\nLowest Complexity Products (Commodities causing the 'Drag') in year {year}:")
                print(bottom_drivers[['product_name', 'pci', 'export_value', 'global_product_total', 'share_str']].to_string(index=False))

                #Add some spacing after each year
                print("\n" + "="*60 + "\n")

        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        logfile.close()

##############################################################################################################################
##############################################################################################################################

'''Example Usage'''
'''
analyze_country_complexity(years, countries, data_path, supplementary)
'''