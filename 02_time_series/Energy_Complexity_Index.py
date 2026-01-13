import pandas as pd
from ecomplexity import ecomplexity
import numpy as np
import sys
import os
from CSV_creator import CSV_creatorHS22, CSV_creatorHS96, CSV_creatorHS17
from Data_Filter import Data_filterHS22, Data_filterHS96, Data_filterHS17
from ECI_calculator import ECI_ecomplexity
from Comparison_Results import PCI_comparison, ECI_comparison
from ECI_Map import ECI_Map
from ECI_Pillar import ECI_Pillar
from ECI_Scatter import ECI_Scatter_Population, ECI_Scatter_GDP, ECI_Scatter_Energy
from ECI_Distribution import ECI_Distribution
from ECI_time_series import ECI_time_series, ECI_time_line_plot, ECI_time_line_singular_plot

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

# Decides which dataset to use
HS_22 = 0  # 1 for HS 2022, 0 for HS 1996

years = [1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 
         2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013,
         2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023]

yellow = 1
first = 1  # 1 to use first year for top/bottom 20, 0 for last year
save_folder = "04_Results_96_23_all_Filters_relative_3" #Folder to save results
all_countries = 1  # 1 to plot all countries in time series, 0 for selected list
no_filter = 0 #no min trade value, no ubiquity, no global market share filtering 

####################################################################################
population = 1
pop_min = 1e6 #minimum population to include country in ECI calculation

####################################################################################

trade_value = 1
total_trade_value = 0 #1 to filter by total trade value, 0 to filter by relative trade value
relative_trade_value = 0.95 #include top 90% of trade value countries

#BACI value is in thousand $
min_trade_value = {1996: 1e4, #141 -> 125
                1997: 4e4, #144 -> 102
                1998: 4e4, #144 -> 104
                1999: 4e4, #144 -> 106
                2000: 4e4, #150 -> 118
                2001: 7e4, #150 -> 119
                2002: 8e4, #150 -> 118
                2003: 1.2e5, #150 -> 119
                2004: 1.5e5, #151 -> 123
                2005: 2e5, #151 -> 121
                2006: 2e5, #152 -> 128
                2007: 2.5e5, #156 -> 129
                2008: 3.5e5, #156 -> 128
                2009: 3.5e5, #156 -> 126
                2010: 4e5, #156 -> 129
                2011: 4e5, #156 -> 131
                2012: 4.5e5, #157 -> 134 
                2013: 5e5, #157 -> 131
                2014: 5e5, #157 -> 131
                2015: 5e5, #158 -> 126
                2016: 5e5, #158 -> 129
                2017: 5.25e5, #158 -> 130
                2018: 5.25e5, #158 -> 130
                2019: 6e5, #158 -> 133
                2020: 5.5e5, #158 -> 134
                2021: 6.5e5, #158 -> 133
                2022: 6.5e5, #158 -> 133
                2023: 6e5} #158 -> 132

###########################################################################################################

#BACI value in thousand $
min_trade = {1996: 1,
                1997: 1,
                1998: 1,
                1999: 1,
                2000: 1,
                2001: 1,
                2002: 1,
                2003: 1,
                2004: 1,
                2005: 1,
                2006: 1,
                2007: 1,
                2008: 1,
                2009: 1,
                2010: 1,
                2011: 1,
                2012: 1,
                2013: 1,
                2014: 1,
                2015: 1,
                2016: 1,
                2017: 1,
                2018: 1,
                2019: 1,
                2020: 1,
                2021: 1,
                2022: 1,
                2023: 1}

absolute_min_val = 1 #1 to filter with absolute values, 0 to filter with relative percentage
percentage_threshold = 0.95 #keep top 95% of trades by value by getting trade value of quantile 0.05 and then cutting everything below that

min_val = {
    1996: 1, #1'000 $
    1997: 1, #1'000 $
    1998: 1, #1'000 $
    1999: 1, #1'000 $
    2000: 0.7, #700 $
    2001: 2, #to correct ECI of Canada
    2002: 0.5,
    2003: 0.5, #to flatten ECI of top countries
    2004: 0.5,
    2005: 0.5,
    2006: 0.5,
    2007: 0.5,
    2008: 0.5,
    2009: 0.5,
    2010: 0.5,
    2011: 0.5,
    2012: 0.5,
    2013: 0.5,
    2014: 0.5,
    2015: 0.5,
    2016: 0.5,
    2017: 0.5,
    2018: 0.5,
    2019: 0.5,
    2020: 0.5,
    2021: 0.5,
    2022: 0.5,
    2023: 0.5
}

#################################################################################################

ubiquity = {1996: 1,
            1997: 1,
            1998: 1,
            1999: 1,
            2000: 1,
            2001: 1,
            2002: 1,
            2003: 1,
            2004: 1,
            2005: 1,
            2006: 1,
            2007: 1,
            2008: 1,
            2009: 1,
            2010: 1,
            2011: 1,
            2012: 1,
            2013: 1,
            2014: 1,
            2015: 1,
            2016: 1,
            2017: 1,
            2018: 1,
            2019: 1,
            2020: 1,
            2021: 1,
            2022: 1,
            2023: 1}

absolute_ubiquity = 0 #1 to use absolute ubiquity limits, 0 to use relative ubiquity limits

relative_lower_limit = 1.25 #set so that all products below xx*min ubiquity are cut off; if min ubiquity below 3, just remove bottom 3 ubiquity

lower_limit = { 1996: 12, #min 8/8
                1997: 10, #min 8/8
                1998: 15, #min 15/15
                1999: 14, #min 12/12
                2000: 11, #min 10/9
                2001: 10, #min 12/12
                2002: 10, #min 7/7
                2003: 10, #min 5/5
                2004: 10, #min 11/3
                2005: 8, #min 6/3
                2006: 8, #min 6/1
                2007: 14, #min 4/1
                2008: 6, #min 2/2
                2009: 6, #min 3/3
                2010: 4, #min 1/1
                2011: 4, #min 1/1
                2012: 4, #min 1/1
                2013: 4, #min 1/1
                2014: 4, #min 1/1
                2015: 4, #min 1/1
                2016: 4, #min 1/1
                2017: 4, #min 1/1
                2018: 12, #min 8/1 
                2019: 5, #min 2/1
                2020: 15, #min 11/2
                2021: 11, #min 7/2
                2022: 6, #min 2/2
                2023: 6} #min 2/

relative_upper_limit = 0.97 #set so that all products over xx*max ubiquity are cut off

upper_limit = { 1996: 100, #set so that no upper limit is applied; max 86/87
                1997: 104, #set so that no upper limit is applied; max 102/103
                1998: 105, #set so that no upper limit is applied; max 103/108
                1999: 107, #set so that no upper limit is applied; max 104/109
                2000: 110, #cut out some of the very high ubiquity products; max 116/119
                2001: 115, #max 119/120
                2002: 120, #set so that no upper limit is applied; max 117/120
                2003: 115, #max 117/118
                2004: 110, #max 123/126
                2005: 118, #max 121/123
                2006: 130, #max 127/129
                2007: 115, #max 129/131
                2008: 128, #max 130/134
                2009: 117, #max 126/126
                2010: 125, #max 129/130
                2011: 125, #max 131/132
                2012: 125, #max 134/136
                2013: 140, #max 130/133
                2014: 125, #max 131/134
                2015: 140, #max 126/129
                2016: 125, #max 129/131
                2017: 127, #max 130/133
                2018: 125, #max 130/134
                2019: 130, #max 133/134
                2020: 130, #max 134/136
                2021: 133, #max 133/135
                2022: 140, #max 133/133
                2023: 140} #max 132

###########################################################################################

global_market_share = {1996: 0,
                        1997: 0,
                        1998: 0,
                        1999: 0,
                        2000: 0,
                        2001: 0,
                        2002: 0,
                        2003: 0,
                        2004: 0,
                        2005: 0,
                        2006: 0,
                        2007: 0,
                        2008: 0,
                        2009: 0,
                        2010: 0,
                        2011: 0,
                        2012: 0,
                        2013: 0,
                        2014: 0,
                        2015: 0,
                        2016: 0,
                        2017: 0,
                        2018: 0,
                        2019: 0,
                        2020: 0,
                        2021: 0,
                        2022: 0,
                        2023: 0}

#Trying to filter around 40'000-50'000 products per year
min_global_market_share = {1996: 3e-9,
                           1997: 3e-9,
                           1998: 3e-9,
                           1999: 3e-9,
                           2000: 1e-9,
                           2001: 3e-9,
                           2002: 2e-9,
                           2003: 1e-9,
                           2004: 1e-9,
                           2005: 1e-9,
                           2006: 3e-10,
                           2007: 6e-10,
                           2008: 3e-10,
                           2009: 3e-10,
                           2010: 3e-10,
                           2011: 4e-10,
                           2012: 4e-10,
                           2013: 3e-10,
                           2014: 3e-10,
                           2015: 4e-10,
                           2016: 3e-10,
                           2017: 3e-10,
                           2018: 3.5e-10,
                           2019: 4e-10,
                           2020: 3e-10,
                           2021: 3e-10,
                           2022: 1e-10,
                           2023: 1.5e-10}

if no_filter == 1:
    #population = 0
    #trade_value = 0
    min_trade = {1996: 0,
                1997: 0,
                1998: 0,
                1999: 0,
                2000: 0,
                2001: 0,
                2002: 0,
                2003: 0,
                2004: 0,
                2005: 0,
                2006: 0,
                2007: 0,
                2008: 0,
                2009: 0,
                2010: 0,
                2011: 0,
                2012: 0,
                2013: 0,
                2014: 0,
                2015: 0,
                2016: 0,
                2017: 0,
                2018: 0,
                2019: 0,
                2020: 0,
                2021: 0,
                2022: 0,
                2023: 0}

    ubiquity = {1996: 0,
                1997: 0,
                1998: 0,
                1999: 0,
                2000: 0,
                2001: 0,
                2002: 0,
                2003: 0,
                2004: 0,
                2005: 0,
                2006: 0,
                2007: 0,
                2008: 0,
                2009: 0,
                2010: 0,
                2011: 0,
                2012: 0,
                2013: 0,
                2014: 0,
                2015: 0,
                2016: 0,
                2017: 0,
                2018: 0,
                2019: 0,
                2020: 0,
                2021: 0,
                2022: 0,
                2023: 0}

    global_market_share = {1996: 0,
                1997: 0,
                1998: 0,
                1999: 0,
                2000: 0,
                2001: 0,
                2002: 0,
                2003: 0,
                2004: 0,
                2005: 0,
                2006: 0,
                2007: 0,
                2008: 0,
                2009: 0,
                2010: 0,
                2011: 0,
                2012: 0,
                2013: 0,
                2014: 0,
                2015: 0,
                2016: 0,
                2017: 0,
                2018: 0,
                2019: 0,
                2020: 0,
                2021: 0,
                2022: 0,
                2023: 0}

ECI_comparison_greenplexity = 1

ECI_Map_Plot = 1

ECI_Pillar_Plot = 1

ECI_Scatter_Population_Plot = 1

ECI_Scatter_GDP_Plot = 1

ECI_Scatter_Energy_Plot = 1

ECI_Population_Plot = 1

ECI_Distribution_Plot = 1

ECI_time_series_plot = 1

for year in years:
    # build the directory path depending on yellow flag
    if yellow:
        dir_path = f"{save_folder}/{year}/Yellow"
        log_path = os.path.join(dir_path, f"Terminal_output_Yellow_{year}.log")
    else:
        dir_path = f"{save_folder}/{year}/Energy"
        log_path = os.path.join(dir_path, f"Terminal_output_Energy_{year}.log")

    # make sure directory exists
    os.makedirs(dir_path, exist_ok=True)

    # open logfile
    logfile = open(log_path, "w")

    # tee stdout/stderr
    tee = Tee(sys.stdout, logfile)
    sys.stdout = tee
    sys.stderr = tee

    #I want the names for the columns to be year, exporter, product_code and export_value
    if HS_22 == 1:
        product_codes = CSV_creatorHS22(yellow, year)
        df = Data_filterHS22(product_codes, yellow, year)
    
    else:
        product_codesHS96 = CSV_creatorHS96(yellow, year)
        if year >= 2017:
            product_codesHS17 = CSV_creatorHS17(yellow, year)
            df_1 = Data_filterHS96(product_codesHS96, yellow, year)
            df_2 = Data_filterHS17(product_codesHS17, yellow, year)
            df = pd.concat([df_1, df_2], ignore_index=True)
            print("Combined dataset of HS 96 and HS 17 with", len(df), "rows.")
        else:
            df = Data_filterHS96(product_codesHS96, yellow, year)
    
    df = df.rename(columns={'t': 'year', 'i': 'location_code', 'k': 'hs_product_code', 'v': 'export_value'})
    

    Ecomplexity_df = ECI_ecomplexity(df, year, yellow, absolute_min_val, percentage_threshold, min_trade, min_val, ubiquity, absolute_ubiquity, relative_lower_limit, lower_limit, relative_upper_limit, upper_limit,
                        population, pop_min, trade_value, total_trade_value, relative_trade_value, min_trade_value, global_market_share,
                        min_global_market_share, save_folder)

    print(f"Ecomplexity calculation for the year {year} done.")
    #print("Ecomplexity_df columns:", Ecomplexity_df.columns.to_list())


    if population == 1:
            #columns: Ecomplexity_df columns: ['location_code', 'hs_product_code', 'export_value', 'year', 'diversity', 
    # 'ubiquity', 'mcp', 'eci', 'pci', 'density', 'coi', 'cog', 'rca', 'j', 'q', 'country_code', 'country_iso3',
    #  'global_market_share']
        #Use location code from counry_codes to fill NaN values in country_iso3
        country_codes = pd.read_csv("01_Data/BACI/country_codes_V202501.csv")
        country_codes = country_codes[['country_code','country_iso3']]
        Ecomplexity_df = pd.merge(Ecomplexity_df, country_codes, left_on='location_code', right_on='country_code', how='left', suffixes=('', '_y'))
        Ecomplexity_df['country_iso3'] = Ecomplexity_df['country_iso3'].combine_first(Ecomplexity_df['country_iso3_y'])
        Ecomplexity_df = Ecomplexity_df.drop(columns=['country_iso3_y'])
        #Check if there are still NaN values in country_iso3
        if Ecomplexity_df['country_iso3'].isnull().any():
            print("Warning: There are still NaN values in country_iso3 after merging with country codes.")
            #print rows with NaN country_iso3
            print(Ecomplexity_df[Ecomplexity_df['country_iso3'].isnull()])
        else:
            print("No NaN values in country_iso3 after merging.")
    else:
        country_codes = pd.read_csv("01_Data/BACI/country_codes_V202501.csv")
        country_codes = country_codes[['country_code','country_iso3']]
        Ecomplexity_df = pd.merge(Ecomplexity_df, country_codes, left_on='location_code', right_on='country_code', how='left', suffixes=('', '_y'))
        #print("Merged country codes. Ecomplexity_df columns now:", Ecomplexity_df.columns.to_list())
    

    if ECI_comparison_greenplexity == 1 and year >= 2012:
        eci_greenplexity = pd.read_csv(f"01_Data/Greenplexity/greenplexity_country_index_{year}.csv")
        #eci should have columns country and eci_greenplexity
        eci_greenplexity = eci_greenplexity.rename(columns={'ISO3 Code': 'country_iso3','Greenplexity Index': 'eci_greenplexity'})

        ECI_comparison(Ecomplexity_df, year, yellow, eci_greenplexity, save_folder)

    if ECI_Map_Plot == 1:
        ECI_Map(Ecomplexity_df, yellow, year, save_folder)

    if ECI_Pillar_Plot == 1:
        ECI_Pillar(Ecomplexity_df, yellow, year, save_folder)

    if ECI_Scatter_Population_Plot == 1:
        ECI_Scatter_Population(Ecomplexity_df, yellow, year, save_folder)
    
    if ECI_Scatter_GDP_Plot == 1:
        ECI_Scatter_GDP(Ecomplexity_df, yellow, year, save_folder)

    if ECI_Scatter_Energy_Plot == 1:
        ECI_Scatter_Energy(Ecomplexity_df, yellow, year, save_folder)

    if ECI_Distribution_Plot == 1:
        ECI_Distribution(Ecomplexity_df, yellow, year, save_folder)

    # restore stdout/stderr and close file
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__
    logfile.close()

#Do a time series plot of ECI for all years calculated
if ECI_time_series_plot == 1 and len(years) > 1:
    
    time_series = ECI_time_series(years, yellow, population, save_folder)
    ECI_time_line_plot(time_series, years, save_folder, yellow, first)
    if all_countries == 1:
        country_iso3_list = pd.read_csv("01_Data/country_codes_V202501.csv")['country_iso3'].tolist()
    else:
        country_iso3_list = ["NLD", "ESP", "CHN", "DNK", "GBR", "JPN", "ISR", "DEU", "ITA", "POL", "USA", "CHE", "FRA", "SGP", "AUT", "AUS", "FIN", "IND", "SWE", "IRL", "KOR", "LVA", "EST", "BEL", "CAN", "SVK", "SVN", "HUN", "PRT", "NZL", "NOR", "TUR", "RUS", "ROU", "ZAF", "BRA", "MEX", "CZE", "GRC", "BGR", "HRV", "LTU", "UKR", "ARG", "CHL", "COL", "PER", "VEN", "ECU", "CRI", "PAN", "URY"] 

    ECI_time_line_singular_plot(time_series, country_iso3_list, years, save_folder, yellow)