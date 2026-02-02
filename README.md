# ENERGY_COMPLEXITY_INDEX

A data analysis project focused on the **Energy Complexity Index (ECI)**.  
This repository contains datasets, scripts, and results that together form a workflow for calculating, analyzing, and visualizing the ECI across countries and products.


## Workflow & Usage

This project uses a central python file to manage the entire analysis pipeline, from data cleaning to visualization. You do not need to run individual scripts manually.

### 1. Configuration
Open **`02_Data_handling/_00_Energy_Complexity_Index.py`**. This file serves as the "Control Panel" for the project. Adjust the parameters at the top of the script to define your analysis:

* **`supplementary`**: Toggle `1` to include supplementary products, or `0` for core energy products only.
* **`years`**: Define the list of years to analyze (e.g., `[2023]` for a single year or `range(1996, 2024)` for a time series).
* **`save_folder`**: Define the save folder

* **Filtering Thresholds**: Adjust dictionaries like `min_trade_value` or `global_market_share` to fine-tune data cleaning logic. One can decide between absolute and relative filters
* **Plotting Toggles**: Set flags (e.g., `ECI_Map_Plot = 1`) to enable or disable specific visualization outputs.

### 2. Execution
Run the orchestrator script from the data handling directory:

### 3. Further Analysis
Run the python files `_10_*` to `_12_*` for additional information on specific countries and products.

---

## Project Structure

### 1. `01_Data/`
Directory containing raw datasets, shapefiles, and classification tables used in the analysis.

#### Subdirectories
- **`BACI/`** – Folder containing raw trade data and subsets:
  - `baci_energy_subset.csv`: Trade flows important utilizing only the core energy dataset.
  - `baci_energy_subset_supplementary.csv`: Trade flows important utilizin the supplementary datset as well.
- **`Greenplexity/`** – Data related to green complexity indices.
- **`ne_110m_admin_0_countries/`** – Natural Earth shapefiles required for generating the ECI global map.

#### Socio-Economic & Demographic Indicators
- `CO2_Emissions_World_Bank.csv` – Historical CO2 emissions data.
- `Energy_use_World_Bank.csv` – National energy use statistics.
- `GDP_World_Bank.csv` – GDP data for economic scaling.
- `growth_proj_eci_rankings.csv` – Economic complexity growth projections and rankings.
- `WPP2024_Demographic_Indicators_Medium.csv` – UN World Population Prospects (2024) data.

#### Classifications & Lookups
- `country_codes_V202501.csv` – Standardized country codes and ISO mappings.
- **Product Codes (Harmonized System):**
  - `product_codes_HS17_V202501.csv` – HS 2017 revision codes.
  - `product_codes_HS22_V202501.csv` – HS 2022 revision codes.
  - `product_codes_HS96_V202501.csv` – HS 1996 revision codes.
  
### 2. `02_Data_handling/`
This directory contains the Python scripts responsible for the end-to-end data pipeline: from CSV generation and data filtering to ECI calculation and visualization.

The scripts are numbered to demonstrate the order of operations:

#### Core Processing & Calculation
- **`_00_Energy_Complexity_Index.py`** – The main entry point/orchestrator for the Energy Complexity Index analysis.
- **`_01_CSV_creator.py`** – Generates the required formatted CSV files from the raw data sources found in `01_Data`.
- **`_02_Data_Filter.py`** – Filters whole BACI datasets to focus specifically on energy-related trade flows and products.
- **`_03_ECI_calculator.py`** – Performs the mathematical computation of the Economic Complexity Index using the Method of Reflections.

#### Comparative Analysis
- **`_04_Comparison_Greenplexity.py`** – Compares the calculated Energy ECI results against existing Greenplexity indices.

#### Visualizations & Plotting
- **`_05_ECI_Map.py`** – Generates geospatial maps visualizing ECI distribution globally.
- **`_06_ECI_Pillar.py`** – Creates a top and bottom 15 ECI value pillar chart of countries.
- **`_07_ECI_Scatter.py`** – Produces scatter plots to analyze correlations (e.g., ECI vs. GDP).
- **`_08_ECI_Distribution.py`** – Visualizes the statistical distribution of the ECI.
- **`_09_ECI_time_series.py`** – Plots the evolution of ECI for countries over the analyzed time period.
- **`_10_ECI_country_additional_information.py`** – Generates detailed, country-specific profiles and additional statistical metrics.
- **`_11_PCI_time_series.py`** – Plots the time series evolution of the Product Complexity Index (PCI).
- **`_12_Correlation_checker_energy_supplementary.py`** – Makes a correlation check between the results achieved through the energy dataset and the complementary dataset.

---

### 4. `03_Results*/`
This directory and all following it (*) serving as the main output repository for all analyses, containing calculated indices, statistical summaries, and generated visualizations.

#### Yearly Analysis Structure (e.g., `1996/` to `2023/`)
The primary results are organized chronologically by year. Within each specific year folder, the output is further divided into **`Energy/`** (core product dataset analysis) and **`supplementary/`** (analysis including supplementary products) subdirectories.

These folders contain:
- **CSV Datasets:** Final calculated ECI scores and country rankings.
- **Visualizations (PNG):** A suite of plots including global maps, histograms, scatter plots against other variables (GDP, Population), and top/bottom ranking bar charts.
- **Logs:** Execution logs recording the terminal output for that specific run.

#### Key Aggregated Analysis Folders
In addition to the yearly data, three specific folders hold aggregated results of importance:
- **`Comparisons/`** – Results from validation scripts comparing different model runs (e.g., correlation between energy and supplementary results).
- **`ECI_country_additional_information/`** – Output containing detailed country profiles and extended statistics.
- **`Time_Series/`** – Aggregated longitudinal plots showing the evolution of ECI and PCI over the entire period analyzed.

---

### 5. `04_ecomplexity_certification/`
This directory contains validation scripts and data aimed at certifying the robustness of the complexity indices across different levels of granularities.

#### HS Level Aggregation
The analysis is tested against various levels of the Harmonized System product hierarchy:
- **`HS_code_level_1/` to `6/`** – Contains data or outputs specific to different digits of HS codes (e.g., broad categories vs. specific products) to ensure the ECI remains consistent regardless of aggregation depth.

#### Validation Scripts
- **`ComplexityData.py`** – A helper module used to structure and load the complexity data specifically for these validation tests.
- **`Ecomplexity_checker.py`** – A script designed to verify the standard `ecomplexity` Python package.
- **`econci_checker.py`** – A secondary validation script, comparing results against the `econci` implementation.

---

### 5. `05_Results_ecomplexity_certification/`
Includes all the results of our certification. This folder contains:
- **CSV Datasets:** Final calculated ECI scores and country rankings.
- **Visualizations (PNG):** A suite of plots including global maps, histograms, scatter plots against other variables (GDP, Population), and top/bottom ranking bar charts.
- **Logs:** Execution logs recording the terminal output for that specific run.

---


- `.gitignore` – Ignores big files so as to not get error when pushing to github  
