from ecomplexity import ecomplexity
from ecomplexity import proximity

from ComplexityData import ComplexityData

import pandas as pd
import os

# Import trade data from CID Atlas
#data_url = "https://intl-atlas-downloads.s3.amazonaws.com/country_hsproduct2digit_year.csv.zip"
#data = pd.read_csv(data_url, compression="zip", low_memory=False)
#data = data[['year','location_code','hs_product_code','export_value']]

###################################################################################################################
HS_code_level = 4

min_trade = 1
min_val = 100000

ubiquity = 1
lower_limit = 40
upper_limit = 220

population = 1
pop_min = 1000000

trade_value = 0
min_trade = 1000000000

global_market_share = 0
min_global_market_share = 0.0001

value_standardization = 0

reliability_check = 0

complexity_check = 0

#country_id,country_iso3_code,product_id,product_hs92_code,year,export_value,import_value,global_market_share
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
    # Keep only year, exporter, product, value
    baci = data[['t','i','k','v']]

    #Rename to Atlas conventions
    baci.rename(columns={
        't':'year',
        'i':'location_code',
        'k':'hs_product_code',
        'v':'export_value'
    }, inplace=True)

    data_2023 = baci[baci['year'] == 2023]

if HS_code_level in [1,2,4,6]:
    data.rename(columns={
        'country_iso3_code':'location_code',
        'product_hs92_code':'hs_product_code',
        'export_value':'export_value',
        'year':'year'
    }, inplace=True)

    # Keep only year, exporter, product, value, global market share, pci
    data = data[['year','location_code','hs_product_code','export_value', 'global_market_share', 'pci']]

    data_2023 = data[data['year'] == 2023]


print("Length of data before filtering:", len(data_2023))

if min_trade == 1:

    data_2023 = data_2023[data_2023['export_value'] >= min_val]
    print(f"Length of data after filtering for higher than {min_val}:", len(data_2023))

if ubiquity == 1:
    # Compute ubiquity: number of countries exporting each product
    ubiq = data_2023.groupby('hs_product_code')['location_code'].nunique()
    print("Ubiquity calculated.")
    print(ubiq.describe())
    
    # Keep products with moderate ubiquity (tune thresholds!)
    keep_products = ubiq[(ubiq >= lower_limit) & (ubiq <= upper_limit)].index
 
    # Filter data
    data_2023 = data_2023[data_2023['hs_product_code'].isin(keep_products)]
    print(f"Length of data after ubiquity filtering with {lower_limit} and {upper_limit}:", len(data_2023))

if population == 1:
    print("Amount of unique countries before filtering:", data_2023['location_code'].nunique())
    #country_iso3,population
    pop_data_2023 = pd.read_csv("01_Data/population_2023.csv")

    min_pop_countries = pop_data_2023[pop_data_2023['population'] >= pop_min]['country_iso3'].tolist()
    print(f"Countries with population over {pop_min}:", len(min_pop_countries))
    if HS_code_level == 0:
        country_codes = pd.read_csv(r"C:\Users\marvi\OneDrive\Semester Thesis\BACI_HS22_V202501\country_codes_V202501.csv")
        country_codes = country_codes[['country_code','country_iso3']]
        data_2023 = pd.merge(data_2023, country_codes, left_on='location_code', right_on='country_code', how='left')
        
        data_2023 = data_2023[data_2023['country_iso3'].isin(min_pop_countries)]
        #Check how many unique countries are left
        unique_countries = data_2023['location_code'].nunique()
        print(f"Number of unique countries after population filtering with min {pop_min}:", unique_countries)
        print(f"Length of data after population filtering with min {pop_min}:", len(data_2023))

    else:
        data_2023 = data_2023[data_2023['location_code'].isin(min_pop_countries)]
        #Check how many unique countries are left
        unique_countries = data_2023['location_code'].nunique()
        print(f"Number of unique countries after population filtering with min {pop_min}:", unique_countries)
        print(f"Length of data after population filtering with min {pop_min}:", len(data_2023))

if trade_value == 1:
    print("Amount of unique countries before trade value filtering:", data_2023['location_code'].nunique())
    #sum trade value by country
    total_trade = data_2023.groupby('location_code')['export_value'].sum()
    total_trade = total_trade.sort_values(ascending=False)
    save_path = os.path.join("04_Results", "total_trade_by_country_2023.csv")
    total_trade.to_csv(save_path, header=['total_export_value'])

    print(f"Saved total trade by country to {save_path}")
    high_trade_countries = total_trade[total_trade >= min_trade].index.tolist()
    data_2023 = data_2023[data_2023['location_code'].isin(high_trade_countries)]
    print("Amount of unique countries after trade value filtering:", data_2023['location_code'].nunique())
    print(f"Length of data after trade value filtering with min {min_trade}:", len(data_2023))

if global_market_share == 1:
    # Keep products with at least 0.01% global share
    data_2023 = data_2023[data_2023['global_market_share'] >= min_global_market_share]
    print(f"Length of data after global market share filtering with min {min_global_market_share}:", len(data_2023))

if value_standardization == 1:
    # Convert CIF to FOB using estimated freight factor (e.g., 1.1)
    data_2023['export_value'] = data_2023['export_value'] / 1.1

if reliability_check == 1:
    # Merge export and import reports
    merged = data.merge(data['export_value'], data['import_value'], on=['year', 'location_code', 'hs_product_code'])

    # Compute reliability score (e.g., ratio stability)
    merged['ratio'] = merged['export_value'] / merged['import_value']
    reliability = merged.groupby('location_code')['ratio'].std().reset_index(name='reliability_score')
    # Normalize reliability scores (lower = more reliable)
    reliability['weight'] = 1 / (1 + reliability['reliability_score'])

    # Merge weights back into trade data
    merged = pd.merge(merged, reliability[['location_code', 'weight']], on='location_code')

    # Weighted average of export and import values
    merged['estimated_trade_value'] = (
        merged['export_value'] * merged['weight'] +
        merged['import_value'] * (1 - merged['weight'])
    )

if complexity_check == 1:
    # Rename to match ComplexityData expectations
    data.rename(columns={
        'year': 'time',
        'location_code': 'loc',
        'hs_product_code': 'prod',
        'export_value': 'val'
    }, inplace=True)

    print(data.columns.tolist())

    col = {'time':'time', 'loc':'loc', 'prod':'prod', 'val':'val'}

    cd = ComplexityData(data, col, val_errors_flag="coerce")

    print(cd.data.columns.tolist())


    cd.create_full_df(t=2023)
    cd.calculate_rca()
    cd.calculate_mcp(rca_mcp_threshold_input=1.0, rpop_mcp_threshold_input=None, presence_test="rca", pop=None, t=2023)

    sparsity = 1 - (cd.data_t.val.astype(bool).sum() / cd.data_t.size)
    print(f"Sparsity: {sparsity:.2%}")

    # Access binary matrix
    mcp_matrix = cd.mcp_t

    rca_matrix = cd.rca_t
    rca_df = cd.data_t.reset_index().copy()   # bring loc/prod back as columns
    rca_df['rca'] = rca_matrix.flatten()

    # Keep only loc, prod, val (time is already fixed at 2023)
    filtered_df = rca_df[rca_df['rca'] >= 1][['loc','prod','val']].copy()
    filtered_df['time'] = 2023   # add back time column explicitly

    print("Filtered data shape:", filtered_df.shape)
    print("Filtered columns:", filtered_df.columns.tolist())

# Calculate complexity

if complexity_check == 1:  
    trade_cols = {'time':'time', 'loc':'loc', 'prod':'prod', 'val':'val'}
    cdata = ecomplexity(filtered_df, trade_cols)
    print(cdata.columns.tolist())

    pci_computed = cdata[['prod', 'pci']].copy()
    pci_computed.rename(columns={'pci': 'pci_computed', 'prod': 'hs_product_code'}, inplace=True)
    pci_atlas = data_2023[['hs_product_code', 'pci']].drop_duplicates()

    pci_compare = pd.merge(pci_computed, pci_atlas, on='hs_product_code', how='inner')
    pci_compare.rename(columns={'pci': 'pci_atlas'}, inplace=True)
    save_path = os.path.join("04_Results", f"pci_comparison_hs92_{HS_code_level}.csv")
    pci_compare.to_csv(save_path, index=False)
    print(f"Saved PCI comparison to {save_path}")

    correlation = pci_compare[['pci_computed', 'pci_atlas']].corr().iloc[0, 1]
    print(f"PCI correlation (ecomplexity vs Atlas): {correlation:.4f}")
else:
    trade_cols = {'time':'year', 'loc':'location_code', 'prod':'hs_product_code', 'val':'export_value'}
    cdata = ecomplexity(data_2023, trade_cols)
    print("columns in cdata:")
    print(cdata.columns.tolist())

    if HS_code_level == 0:
        pci_computed = cdata[['hs_product_code', 'pci']].copy()
        pci_computed.rename(columns={'pci': 'pci_computed'}, inplace=True)
        data_atlas = pd.read_csv(r"C:\Users\marvi\OneDrive\Semester Thesis\hs92_country_product\hs92_country_product_year_4.csv")
        #keep only year 2023
        data_atlas.rename(columns={
        'country_iso3_code':'location_code',
        'product_hs92_code':'hs_product_code',
        'export_value':'export_value',
        'year':'year'
        }, inplace=True)
        data_atlas_2023 = data_atlas[data_atlas['year'] == 2023]
        pci_atlas = data_atlas_2023[['hs_product_code', 'pci']].drop_duplicates()

        pci_compare = pd.merge(pci_computed, pci_atlas, on='hs_product_code', how='inner')
        
        pci_compare.rename(columns={'pci': 'pci_atlas'}, inplace=True)
        #checking HS92 to HS22, might be a probl
        save_path = os.path.join("04_Results", f"pci_comparison_hs92_{HS_code_level}.csv")
        pci_compare.to_csv(save_path, index=False)
        print(f"Saved PCI comparison to {save_path}")

        correlation = pci_compare[['pci_computed', 'pci_atlas']].corr().iloc[0, 1]
        print(f"PCI correlation (ecomplexity vs Atlas): {correlation:.4f}")
    else:
        pci_computed = cdata[['hs_product_code', 'pci_x']].copy()
        pci_computed.rename(columns={'pci_x': 'pci_computed'}, inplace=True)
        pci_atlas = data_2023[['hs_product_code', 'pci']].drop_duplicates()

        pci_compare = pd.merge(pci_computed, pci_atlas, on='hs_product_code', how='inner')
        pci_compare.rename(columns={'pci': 'pci_atlas'}, inplace=True)
        save_path = os.path.join("04_Results", f"pci_comparison_hs92_{HS_code_level}.csv")
        pci_compare.to_csv(save_path, index=False)
        print(f"Saved PCI comparison to {save_path}")

        correlation = pci_compare[['pci_computed', 'pci_atlas']].corr().iloc[0, 1]
        print(f"PCI correlation (ecomplexity vs Atlas): {correlation:.4f}")

pci_compare['rank_computed'] = pci_compare['pci_computed'].rank(ascending=False, method='dense')
pci_compare['rank_atlas'] = pci_compare['pci_atlas'].rank(ascending=False, method='dense')
pci_compare['rank_diff'] = pci_compare['rank_computed'] - pci_compare['rank_atlas']

# Sort by biggest mismatch
rank_mismatch = pci_compare.sort_values(by='rank_diff', key=abs, ascending=False).head(10)
print("Top 10 PCI rank mismatches:")
print(rank_mismatch[['hs_product_code','pci_computed','pci_atlas','rank_computed','rank_atlas','rank_diff']])

if HS_code_level == 6:
    if (min_trade == 0) and (ubiquity == 0):
        cdata.to_csv("04_Results/eci_results_Atlas_hs92_6.csv", index=False)
        print("Saved eci_results to Results/eci_results_Atlas_hs92_6.csv")
    else:
        cdata.to_csv("04_Results/eci_results_Atlas_hs92_6_filtered.csv", index=False)
        print("Saved eci_results to Results/eci_results_Atlas_hs92_6_filtered.csv")

if HS_code_level == 4:
    if (min_trade == 0) and (ubiquity == 0):
        cdata.to_csv("04_Results/eci_results_Atlas_hs92_4.csv", index=False)
        print("Saved eci_results to Results/eci_results_Atlas_hs92_4.csv")
    else:
        cdata.to_csv("04_Results/eci_results_Atlas_hs92_4_filtered.csv", index=False)
        print("Saved eci_results to Results/eci_results_Atlas_hs92_4_filtered.csv")

if complexity_check == 1:
    eci_country = cdata[["loc", "time", "eci"]].drop_duplicates()
    eci_country = eci_country.rename(columns={"loc": "country_code"})

else:
    eci_country = cdata[["location_code", "year", "eci"]].drop_duplicates()
    eci_country = eci_country.rename(columns={"location_code": "country_code"})
eci_country = eci_country.dropna(subset=["eci"]).reset_index(drop=True)

#print(eci_country.head())

eci_country = eci_country[['country_code', 'eci']]

eci_Atlas = pd.read_csv("01_Data/growth_proj_eci_rankings.csv")
eci_Atlas = eci_Atlas[eci_Atlas['year'] == 2023]
#print(eci_Atlas.head())

eci_Atlas = eci_Atlas[['country_iso3_code', 'eci_hs92']]

if HS_code_level == 0:
    country_codes = pd.read_csv(r"C:\Users\marvi\OneDrive\Semester Thesis\BACI_HS22_V202501\country_codes_V202501.csv")
    country_codes = country_codes[['country_code','country_iso3']]
    eci_country = pd.merge(eci_country, country_codes, on='country_code', how='left')
    eci_country = eci_country.drop(columns='country_code')  # drop numeric
    eci_country.rename(columns={'country_iso3': 'country_code'}, inplace=True)
    eci_country = eci_country[['country_code', 'eci']]
    

eci_compare = pd.merge(eci_country, eci_Atlas, left_on='country_code', right_on='country_iso3_code', how='inner')
eci_compare = eci_compare.sort_values(by='eci_hs92', ascending=False).reset_index(drop=True)


#look at correlation
correlation_eci = eci_compare[['eci', 'eci_hs92']].corr().iloc[0, 1]
print(f"ECI correlation (ecomplexity vs Atlas): {correlation_eci:.4f}")

# --- Rank diagnostics ---
eci_compare['rank_computed'] = eci_compare['eci'].rank(ascending=False, method='dense')
eci_compare['rank_atlas'] = eci_compare['eci_hs92'].rank(ascending=False, method='dense')
eci_compare['rank_diff'] = eci_compare['rank_computed'] - eci_compare['rank_atlas']

# Sort by biggest mismatch
rank_mismatch = eci_compare.sort_values(by='rank_diff', key=abs, ascending=False).head(10)
print("Top 10 ECI rank mismatches:")
print(rank_mismatch[['country_code','eci','eci_hs92','rank_computed','rank_atlas','rank_diff']])

save_path = os.path.join("04_Results", f"eci_comparison_hs92_{HS_code_level}.csv")
eci_compare.to_csv(save_path, index=False)
print(f"Saved ECI comparison to {save_path}")