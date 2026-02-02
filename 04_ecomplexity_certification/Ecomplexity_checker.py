from ecomplexity import ecomplexity
from ecomplexity import proximity

from ComplexityData import ComplexityData

import pandas as pd
import sys
import os



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

# Import trade data from CID Atlas
#data_url = "https://intl-atlas-downloads.s3.amazonaws.com/country_hsproduct2digit_year.csv.zip"
#data = pd.read_csv(data_url, compression="zip", low_memory=False)
#data = data[['year','location_code','hs_product_code','export_value']]

###################################################################################################################
HS_code_level = 1
years = [1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 
         2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013,
         2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023]
#years = [1996, 1997, 2022, 2023]

population = 1
pop_min = 1000000


trade_value_country = 1
min_trade_country = 1e6 #trade values are in 1000$, so this is 1e9


min_trade_singular = 1
min_val = 0.5 #500 $ Limit
#Ubiquity only gets filtered with HS code level 4 and 6
ubiquity = 1
relative_lower_limit = 1.5
relative_upper_limit = 0.997

global_market_share = 0
min_global_market_share = 0.0001

value_standardization = 0

reliability_check = 0

complexity_check = 0

if HS_code_level == 6:
    data = pd.read_csv(r"C:\Users\marvi\OneDrive\Semester Thesis\hs92_country_product\hs92_country_product_year_6.csv")
    print("using HS code level 6 from Atlas")
if HS_code_level == 4:
    data = pd.read_csv(r"C:\Users\marvi\OneDrive\Semester Thesis\hs92_country_product\hs92_country_product_year_4.csv")
    print("using HS code level 4 from Atlas")
if HS_code_level == 2:
    data = pd.read_csv(r"C:\Users\marvi\OneDrive\Semester Thesis\hs92_country_product\hs92_country_product_year_2.csv")
    print("using HS code level 2 from Atlas")
if HS_code_level == 1:
    data = pd.read_csv(r"C:\Users\marvi\OneDrive\Semester Thesis\hs92_country_product\hs92_country_product_year_1.csv")
    print("using HS code level 1 from Atlas")
if HS_code_level == 0:
    data = pd.read_csv(r"C:\Users\marvi\OneDrive\Semester Thesis\BACI_HS22_V202501\BACI_HS22_Y2023_V202501.csv")
    print("Using BACI HS22 data from year 2023")
    baci = data[['t','i','k','v']]

    baci.rename(columns={
        't':'year',
        'i':'location_code',
        'k':'hs_product_code',
        'v':'export_value'
    }, inplace=True)

    data_2023 = baci[baci['year'] == 2023]


for year in years:
    dir_path = f"05_Checkups/HS_code_level_{HS_code_level}/years/{year}"
    log_path = os.path.join(dir_path, f"Terminal_output_Energy_{year}.log")

    os.makedirs(dir_path, exist_ok=True)

    logfile = open(log_path, "w")
    
    tee = Tee(sys.stdout, logfile)
    sys.stdout = tee
    sys.stderr = tee

    if HS_code_level in [1,2,4]:
        data.rename(columns={
            'country_iso3_code':'location_code',
            'product_hs92_code':'hs_product_code',
            'export_value':'export_value',
            'year':'year'
        }, inplace=True)
    
        data = data[['year','location_code','hs_product_code','export_value', 'global_market_share', 'pci']]
        data_year = data[data['year'] == year]

    if HS_code_level == 6:
        data.rename(columns={
            'country_iso3_code':'location_code',
            'product_hs92_code':'hs_product_code',
            'export_value':'export_value',
            'year':'year'
        }, inplace=True)

        data = data[['year','location_code','hs_product_code','export_value', 'global_market_share']]
        data_year = data[data['year'] == year]


    print(f"Length of data of {year} before filtering:", len(data_year))
    if len(data_year) == 0:
        print(f"No data found for year {year}. Skipping...")
        continue

    if population == 1:
        print("Amount of unique countries before filtering:", data_year['location_code'].nunique())
        population_data = pd.read_csv("01_Data/WPP2024_Demographic_Indicators_Medium.csv")
        momentary_data = len(data_year)

        population_year = population_data[population_data["Time"] == year]
        population_year = population_year[["ISO3_code", "TPopulation1July"]].rename(
            columns={"ISO3_code": "country_iso3", "TPopulation1July": "population"})
        population_year = population_year.dropna(subset=["country_iso3"])
        population_year["population"] = population_year["population"] * 1000 # includes 'country_iso3', 'population'

        pop_data = population_year

        min_pop_countries = pop_data[pop_data['population'] >= pop_min]['country_iso3'].tolist()
        print(f"Countries with population over {pop_min}:", len(min_pop_countries))
        if HS_code_level == 0:
            country_codes = pd.read_csv(r"C:\Users\marvi\OneDrive\Semester Thesis\BACI_HS22_V202501\country_codes_V202501.csv")
            country_codes = country_codes[['country_code','country_iso3']]
            data_year = pd.merge(data_year, country_codes, left_on='location_code', right_on='country_code', how='left')
            
            data_year = data_year[data_year['country_iso3'].isin(min_pop_countries)]
            unique_countries = data_year['location_code'].nunique()
            print(f"Number of unique countries after population filtering with min {pop_min}:", unique_countries)
            print(f"Length of data after population filtering with min {pop_min}:", len(data_year))

        else:
            data_year = data_year[data_year['location_code'].isin(min_pop_countries)]
            unique_countries = data_year['location_code'].nunique()
            print(f"Number of unique countries after population filtering with min {pop_min}:", unique_countries)
            print(f"Length of data after population filtering with min {pop_min}:", len(data_year))

    if trade_value_country == 1:
        print("Amount of unique countries before trade value filtering:", data_year['location_code'].nunique())
        total_trade = data_year.groupby('location_code')['export_value'].sum()
        total_trade = total_trade.sort_values(ascending=False)
        save_path = os.path.join(f"05_Checkups/HS_code_level_{HS_code_level}/years/{year}", f"total_trade_by_country_{year}.csv")
        total_trade.to_csv(save_path, header=['total_export_value'])

        print(f"Saved total trade by country to {save_path}")
        high_trade_countries = total_trade[total_trade >= min_trade_country].index.tolist()
        data_year = data_year[data_year['location_code'].isin(high_trade_countries)]
        print("Amount of unique countries after trade value filtering:", data_year['location_code'].nunique())
        print(f"Length of data after trade value filtering with min {min_trade_country}:", len(data_year))

    if min_trade_singular == 1:

        data_year = data_year[data_year['export_value'] >= min_val]
        print(f"Length of data after filtering for higher than {min_val}:", len(data_year))

    if ubiquity == 1 and HS_code_level >= 4:
        ubiq = data_year.groupby('hs_product_code')['location_code'].nunique()
        print("Ubiquity calculated.")
        print(ubiq.describe())
        
        if ubiq.min() <= 10:
            lower_threshold = 10 
            relative_ll_ubiquity = relative_lower_limit
        else: 
            relative_ll_ubiquity = relative_lower_limit
            lower_threshold = relative_ll_ubiquity * ubiq.min()
        if HS_code_level < 4:
            relative_ul_ubiquity = 1.1
            upper_threshold = relative_ul_ubiquity * ubiq.max()

        else:
            relative_ul_ubiquity = relative_upper_limit
            upper_threshold = relative_ul_ubiquity * ubiq.max()

        keep_products = ubiq[(ubiq >= lower_threshold) & (ubiq <= upper_threshold)].index    
        data_year = data_year[data_year['hs_product_code'].isin(keep_products)]
        print(f"Amount of data after relative ubiquity filtering with {lower_threshold} ({relative_ll_ubiquity}) and {upper_threshold} ({relative_ul_ubiquity}):", len(data_year))
    
    if global_market_share == 1:
        data_year = data_year[data_year['global_market_share'] >= min_global_market_share]
        print(f"Length of data after global market share filtering with min {min_global_market_share}:", len(data_year))

    if value_standardization == 1:
        data_year['export_value'] = data_year['export_value'] / 1.1

    if reliability_check == 1:
        merged = data_year.merge(data_year['export_value'], data_year['import_value'], on=['year', 'location_code', 'hs_product_code'])
        merged['ratio'] = merged['export_value'] / merged['import_value']
        reliability = merged.groupby('location_code')['ratio'].std().reset_index(name='reliability_score')
        reliability['weight'] = 1 / (1 + reliability['reliability_score'])

        merged = pd.merge(merged, reliability[['location_code', 'weight']], on='location_code')

        # Weighted average of export and import values
        merged['estimated_trade_value'] = (
            merged['export_value'] * merged['weight'] +
            merged['import_value'] * (1 - merged['weight'])
        )

    if complexity_check == 1:
        data_year.rename(columns={
            'year': 'time',
            'location_code': 'loc',
            'hs_product_code': 'prod',
            'export_value': 'val'
        }, inplace=True)

        print(data_year.columns.tolist())

        col = {'time':'time', 'loc':'loc', 'prod':'prod', 'val':'val'}
        cd = ComplexityData(data_year, col, val_errors_flag="coerce")
        #print(cd.data_year.columns.tolist())
        cd.create_full_df(t=year)
        cd.calculate_rca()
        cd.calculate_mcp(rca_mcp_threshold_input=1.0, rpop_mcp_threshold_input=None, presence_test="rca", pop=None, t=year)

        sparsity = 1 - (cd.data_year_t.val.astype(bool).sum() / cd.data_year_t.size)
        print(f"Sparsity: {sparsity:.2%}")

        # Access binary matrix
        mcp_matrix = cd.mcp_t
        rca_matrix = cd.rca_t
        rca_df = cd.data_year_t.reset_index().copy()   # bring loc/prod back as columns
        rca_df['rca'] = rca_matrix.flatten()

        filtered_df = rca_df[rca_df['rca'] >= 1][['loc','prod','val']].copy()
        filtered_df['time'] = year

        print("Filtered data shape:", filtered_df.shape)
        print("Filtered columns:", filtered_df.columns.tolist())

    if complexity_check == 1:  
        trade_cols = {'time':'time', 'loc':'loc', 'prod':'prod', 'val':'val'}
        cdata = ecomplexity(filtered_df, trade_cols)
        print(cdata.columns.tolist())

        pci_computed = cdata[['prod', 'pci']].copy()
        pci_computed.rename(columns={'pci': 'pci_computed', 'prod': 'hs_product_code'}, inplace=True)
        pci_atlas = data_year[['hs_product_code', 'pci']].drop_duplicates()

        pci_compare = pd.merge(pci_computed, pci_atlas, on='hs_product_code', how='inner')
        pci_compare.rename(columns={'pci': 'pci_atlas'}, inplace=True)
        save_path = os.path.join(f"05_Checkups/HS_code_level_{HS_code_level}/years/{year}", f"pci_comparison_hs92_{HS_code_level}.csv")
        pci_compare.to_csv(save_path, index=False)
        print(f"Saved PCI comparison to {save_path}")

        correlation = pci_compare[['pci_computed', 'pci_atlas']].corr().iloc[0, 1]
        print(f"PCI correlation (ecomplexity vs Atlas): {correlation:.4f}")
    else:
        trade_cols = {'time':'year', 'loc':'location_code', 'prod':'hs_product_code', 'val':'export_value'}
        cdata = ecomplexity(data_year, trade_cols)
        print("columns in cdata:")
        print(cdata.columns.tolist())

        if HS_code_level == 0:
            pci_computed = cdata[['hs_product_code', 'pci']].drop_duplicates(subset=['hs_product_code'])
            pci_computed.rename(columns={'pci': 'pci_computed'}, inplace=True)
            data_atlas = pd.read_csv(r"C:\Users\marvi\OneDrive\Semester Thesis\hs92_country_product\hs92_country_product_year_4.csv")

            data_atlas.rename(columns={
            'country_iso3_code':'location_code',
            'product_hs92_code':'hs_product_code',
            'export_value':'export_value',
            'year':'year'
            }, inplace=True)
            data_atlas = data_atlas[data_atlas['year'] == year]
            pci_atlas = data_atlas[['hs_product_code', 'pci']].drop_duplicates()

            pci_compare = pd.merge(pci_computed, pci_atlas, on='hs_product_code', how='inner')            
            pci_compare.rename(columns={'pci': 'pci_atlas'}, inplace=True)
            save_path = os.path.join(f"05_Checkups/HS_code_level_{HS_code_level}/years/{year}", f"pci_comparison_hs92_{HS_code_level}.csv")
            pci_compare.to_csv(save_path, index=False)
            print(f"Saved PCI comparison to {save_path}")

            correlation = pci_compare[['pci_computed', 'pci_atlas']].corr().iloc[0, 1]
            print(f"PCI correlation in {year} (ecomplexity vs Atlas): {correlation:.4f}")

        if HS_code_level == 6:
            print("no PCI correlation available")
        else:
            pci_computed = cdata[['hs_product_code', 'pci_x']].drop_duplicates(subset=['hs_product_code'])
            pci_computed.rename(columns={'pci_x': 'pci_computed'}, inplace=True)
            pci_atlas = data_year[['hs_product_code', 'pci']].drop_duplicates()

            pci_compare = pd.merge(pci_computed, pci_atlas, on='hs_product_code', how='inner')
            pci_compare.rename(columns={'pci': 'pci_atlas'}, inplace=True)
            save_path = os.path.join(f"05_Checkups/HS_code_level_{HS_code_level}/years/{year}", f"pci_comparison_hs92_{HS_code_level}.csv")
            pci_compare.to_csv(save_path, index=False)
            print(f"Saved PCI comparison to {save_path}")

            correlation = pci_compare[['pci_computed', 'pci_atlas']].corr().iloc[0, 1]
            print(f"PCI correlation  in {year} (ecomplexity vs Atlas): {correlation:.4f}")
    if HS_code_level != 6:
        pci_compare['rank_computed'] = pci_compare['pci_computed'].rank(ascending=False, method='dense')
        pci_compare['rank_atlas'] = pci_compare['pci_atlas'].rank(ascending=False, method='dense')
        pci_compare['rank_diff'] = pci_compare['rank_computed'] - pci_compare['rank_atlas']

        rank_mismatch = pci_compare.sort_values(by='rank_diff', key=abs, ascending=False).head(10)
        print(f"Top 10 PCI rank mismatches in {year}:")
        print(rank_mismatch[['hs_product_code','pci_computed','pci_atlas','rank_computed','rank_atlas','rank_diff']])

        if HS_code_level == 6:
            if (min_trade_singular == 0) and (ubiquity == 0):
                cdata.to_csv(f"05_Checkups/HS_code_level_{HS_code_level}/years/{year}/eci_results_Atlas_hs92_6.csv", index=False)
                print(f"Saved eci_results to 05_Checkups/HS_code_level_{HS_code_level}/years/{year}/eci_results_Atlas_hs92_6.csv")
            else:
                cdata.to_csv(f"05_Checkups/HS_code_level_{HS_code_level}/years/{year}/eci_results_Atlas_hs92_6_filtered.csv", index=False)
                print(f"Saved eci_results to 05_Checkups/HS_code_level_{HS_code_level}/years/{year}/eci_results_Atlas_hs92_6_filtered.csv")

        if HS_code_level == 4:
            if (min_trade_singular == 0) and (ubiquity == 0):
                cdata.to_csv(f"05_Checkups/HS_code_level_{HS_code_level}/years/{year}/eci_results_Atlas_hs92_4.csv", index=False)
                print(f"Saved eci_results to 05_Checkups/HS_code_level_{HS_code_level}/years/{year}/eci_results_Atlas_hs92_4.csv")
            else:
                cdata.to_csv(f"05_Checkups/HS_code_level_{HS_code_level}/years/{year}/eci_results_Atlas_hs92_4_filtered.csv", index=False)
                print(f"Saved eci_results to 05_Checkups/HS_code_level_{HS_code_level}/years/{year}/eci_results_Atlas_hs92_4_filtered.csv")

    if complexity_check == 1:
        eci_country = cdata[["loc", "time", "eci"]].drop_duplicates()
        eci_country = eci_country.rename(columns={"loc": "country_code"})

    else:
        eci_country = cdata[["location_code", "year", "eci"]].drop_duplicates()
        eci_country = eci_country.rename(columns={"location_code": "country_code"})
    eci_country = eci_country.dropna(subset=["eci"]).reset_index(drop=True)
    eci_country = eci_country[['country_code', 'eci']]

    eci_Atlas = pd.read_csv("01_Data/growth_proj_eci_rankings.csv")
    eci_Atlas = eci_Atlas[eci_Atlas['year'] == year]
    eci_Atlas = eci_Atlas[['country_iso3_code', 'eci_hs92']]

    if HS_code_level == 0:
        country_codes = pd.read_csv(r"C:\Users\marvi\OneDrive\Semester Thesis\BACI_HS22_V202501\country_codes_V202501.csv")
        country_codes = country_codes[['country_code','country_iso3']]
        eci_country = pd.merge(eci_country, country_codes, on='country_code', how='left')
        eci_country = eci_country.drop(columns='country_code')
        eci_country.rename(columns={'country_iso3': 'country_code'}, inplace=True)
        eci_country = eci_country[['country_code', 'eci']]
        
    eci_compare = pd.merge(eci_country, eci_Atlas, left_on='country_code', right_on='country_iso3_code', how='inner')
    eci_compare = eci_compare.sort_values(by='eci_hs92', ascending=False).reset_index(drop=True)

    correlation_eci = eci_compare[['eci', 'eci_hs92']].corr().iloc[0, 1]
    print(f"ECI correlation in {year} (ecomplexity vs Atlas): {correlation_eci:.4f}")

    eci_compare['rank_computed'] = eci_compare['eci'].rank(ascending=False, method='dense')
    eci_compare['rank_atlas'] = eci_compare['eci_hs92'].rank(ascending=False, method='dense')
    eci_compare['rank_diff'] = eci_compare['rank_computed'] - eci_compare['rank_atlas']

    rank_mismatch = eci_compare.sort_values(by='rank_diff', key=abs, ascending=False).head(10)
    print(f"Top 10 ECI rank mismatches in {year}:")
    print(rank_mismatch[['country_code','eci','eci_hs92','rank_computed','rank_atlas','rank_diff']])

    save_path = os.path.join(f"05_Checkups/HS_code_level_{HS_code_level}/years/{year}", f"eci_comparison_hs92_{HS_code_level}.csv")
    eci_compare.to_csv(save_path, index=False)
    print(f"Saved ECI comparison to {save_path}")

    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__
    logfile.close()