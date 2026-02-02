import econci
import pandas as pd
import os
import numpy as np


###################################################################################################################

#data = pd.read_csv(r"C:\Users\marvi\OneDrive\Semester Thesis\BACI_HS22_V202501\BACI_HS22_Y2023_V202501.csv")

# Keep only year, exporter, product, value
#baci = data[['t','i','k','v']]

# Rename to Atlas conventions
#baci.rename(columns={
#    't':'year',
#    'i':'location_code',
#    'k':'hs_product_code',
#    'v':'export_value'
#}, inplace=True)

#data_2023 = baci[baci['year'] == 2023]


#######################################################################################################################

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

if HS_code_level in [1,2,4,6]:
    data.rename(columns={
        'country_iso3_code':'location_code',
        'product_hs92_code':'hs_product_code',
        'export_value':'export_value',
        'year':'year'
    }, inplace=True)

    data = data[['year','location_code','hs_product_code','export_value', 'global_market_share', 'pci']]
    data_2023 = data[data['year'] == 2023]

print(data_2023.columns.tolist())
print("Length of data before filtering:", len(data_2023))

if min_trade == 1:
    data_2023 = data_2023[data_2023['export_value'] >= min_val]
    print(f"Length of data after filtering for higher than {min_val}:", len(data_2023))

if ubiquity == 1:
    ubiq = data_2023.groupby('hs_product_code')['location_code'].nunique()
    print("Ubiquity calculated.")
    print(ubiq.describe())
    keep_products = ubiq[(ubiq >= lower_limit) & (ubiq <= upper_limit)].index
 
    data_2023 = data_2023[data_2023['hs_product_code'].isin(keep_products)]
    print(f"Length of data after ubiquity filtering with {lower_limit} and {upper_limit}:", len(data_2023))

if population == 1:
    print("Amount of unique countries before filtering:", data_2023['location_code'].nunique())
    pop_data_2023 = pd.read_csv("01_Data/population_2023.csv")
    min_pop_countries = pop_data_2023[pop_data_2023['population'] >= pop_min]['country_iso3'].tolist()
    print(f"Countries with population over {pop_min}:", len(min_pop_countries))
    if HS_code_level == 0:
        country_codes = pd.read_csv(r"C:\Users\marvi\OneDrive\Semester Thesis\BACI_HS22_V202501\country_codes_V202501.csv")
        country_codes = country_codes[['country_code','country_iso3']]
        data_2023 = pd.merge(data_2023, country_codes, left_on='location_code', right_on='country_code', how='left')
        print(data_2023.head())

        data_2023 = data_2023[data_2023['country_iso3'].isin(min_pop_countries)]
        #Check how many countries are left
        unique_countries = data_2023['location_code'].nunique()
        print(f"Number of unique countries after population filtering with min {pop_min}:", unique_countries)
        print(f"Length of data after population filtering with min {pop_min}:", len(data_2023))
    else:
        data_2023 = data_2023[data_2023['location_code'].isin(min_pop_countries)]
        #Check how many countries are left
        unique_countries = data_2023['location_code'].nunique()
        print(f"Number of unique countries after population filtering with min {pop_min}:", unique_countries)
        print(f"Length of data after population filtering with min {pop_min}:", len(data_2023))

if trade_value == 1:
    print("Amount of unique countries before trade value filtering:", data_2023['location_code'].nunique())
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
    data_2023 = data_2023[data_2023['global_market_share'] >= min_global_market_share]
    print(f"Length of data after global market share filtering with min {min_global_market_share}:", len(data_2023))

if value_standardization == 1:
    data_2023['export_value'] = data_2023['export_value'] / 1.1

if reliability_check == 1:
    merged = data.merge(data['export_value'], data['import_value'], on=['year', 'location_code', 'hs_product_code'])

    merged['ratio'] = merged['export_value'] / merged['import_value']
    reliability = merged.groupby('location_code')['ratio'].std().reset_index(name='reliability_score')
    # Normalize reliability scores (lower = more reliable)
    reliability['weight'] = 1 / (1 + reliability['reliability_score'])

    merged = pd.merge(merged, reliability[['location_code', 'weight']], on='location_code')

    # Weighted average of export and import values
    merged['estimated_trade_value'] = (
        merged['export_value'] * merged['weight'] +
        merged['import_value'] * (1 - merged['weight'])
    )

comp = econci.Complexity(data_2023, c='location_code', p='hs_product_code', values='export_value')

print(comp)

print("Any NaNs?", data_2023.isna().sum())
print("Any infs?", np.isinf(data_2023['export_value']).sum())
print("Countries:", data_2023['location_code'].nunique())
print("Products:", data_2023['hs_product_code'].nunique())

comp.calculate_indexes()
eci = comp.eci
pci = comp.pci

data_atlas = pd.read_csv(r"C:\Users\marvi\OneDrive\Semester Thesis\hs92_country_product\hs92_country_product_year_4.csv")
data_atlas.rename(columns={
'country_iso3_code':'location_code',
'product_hs92_code':'hs_product_code',
'export_value':'export_value',
'year':'year'
}, inplace=True)
data_atlas_2023 = data_atlas[data_atlas['year'] == 2023]

print("data atlas 2023 columns:", data_atlas_2023.columns.tolist())

pci_computed = pci.drop_duplicates().rename(columns={'pci':'pci_computed'})
pci_atlas = data_atlas_2023[['hs_product_code', 'pci']].drop_duplicates()

pci_compare = pd.merge(pci_computed, pci_atlas, on='hs_product_code', how='inner')
print(pci_compare.head())

pci_compare.rename(columns={'pci':'pci_atlas'}, inplace=True)

corr = pci_compare[['pci_computed','pci_atlas']].corr().iloc[0,1]
print(f"PCI correlation: {corr:.4f}")

pci_compare['rank_computed'] = pci_compare['pci_computed'].rank(ascending=False, method='dense')
pci_compare['rank_atlas'] = pci_compare['pci_atlas'].rank(ascending=False, method='dense')
pci_compare['rank_diff'] = pci_compare['rank_computed'] - pci_compare['rank_atlas']
print(pci_compare.sort_values(by='rank_diff', key=abs, ascending=False).head(10))

save_path = os.path.join("04_Results", f"pci_comparison_hs92_{HS_code_level}_econci.csv")
pci_compare.to_csv(save_path, index=False)
print(f"Saved PCI comparison to {save_path}")

eci_computed = eci.drop_duplicates().rename(columns={'eci':'eci_computed'})
print("ECI computed columns:", eci_computed.columns.tolist())

eci_Atlas = pd.read_csv("01_Data/growth_proj_eci_rankings.csv")
eci_Atlas = eci_Atlas[eci_Atlas['year'] == 2023]
print(eci_Atlas.head())

eci_Atlas = eci_Atlas[['country_iso3_code', 'eci_hs92']]

eci_Atlas.rename(columns={'country_iso3_code':'location_code', 'eci_hs92':'eci_atlas'}, inplace=True)

eci_ecomplexity = pd.read_csv("04_Results/eci_results_Atlas_hs92_4_filtered.csv")
eci_ecomplexity = eci_ecomplexity[eci_ecomplexity['year']==2023]
eci_ecomplexity.rename(columns={'eci':'eci_ecomplexity'}, inplace=True)
eci_ecomplexity = eci_ecomplexity[['location_code', 'eci_ecomplexity']].drop_duplicates()

eci_compare = pd.merge(eci_computed, eci_Atlas, on='location_code', how='inner')

print("ECI ecomplexity columns:" , eci_ecomplexity.columns.tolist())

eci_compare = pd.merge(eci_compare, eci_ecomplexity, on='location_code', how='inner')

corr_eci_atlas = eci_compare[['eci_computed','eci_atlas']].corr().iloc[0,1]
print(f"ECI correlation with Atlas: {corr_eci_atlas:.4f}")
corr_eci_ecomplexity = eci_compare[['eci_computed','eci_ecomplexity']].corr().iloc[0,1]
print(f"ECI correlation with Ecomplexity: {corr_eci_ecomplexity:.4f}")

eci_compare['rank_computed'] = eci_compare['eci_computed'].rank(ascending=False, method='dense')
eci_compare['rank_atlas'] = eci_compare['eci_atlas'].rank(ascending=False, method='dense')
eci_compare['rank_ecomplexity'] = eci_compare['eci_ecomplexity'].rank(ascending=False, method='dense')
eci_compare['rank_diff_atlas'] = eci_compare['rank_computed'] - eci_compare['rank_atlas']
print("Top 10 rank differences with Atlas:")
print(eci_compare.sort_values(by='rank_diff_atlas', key=abs, ascending=False).head(10))
print("Top 10 rank differences with Ecomplexity:")
eci_compare['rank_diff_ecomplexity'] = eci_compare['rank_computed'] - eci_compare['rank_ecomplexity']
print(eci_compare.sort_values(by='rank_diff_ecomplexity', key=abs, ascending=False).head(10))
save_path_eci = os.path.join("04_Results", f"eci_comparison_hs92_{HS_code_level}_econci.csv")
eci_compare.to_csv(save_path_eci, index=False)
print(f"Saved ECI comparison to {save_path_eci}")