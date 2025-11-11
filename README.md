# ENERGY_COMPLEXITY_INDEX

A data analysis project focused on the **Energy Complexity Index (ECI)**.  
This repository contains datasets, scripts, and results that together form a workflow for calculating, analyzing, and visualizing the ECI across countries and products.

---

## 📂 Project Structure

### 1. `Data/`
Raw datasets and input files used in the analysis.  
- `ne_110m_admin_0_countries/` – Needed for the ECI map  
- `baci_energy_subset_yellow.csv` – Subset of BACI of all trade flows important for the energy sector and yellow products  
- `baci_energy_subset.csv` – Subset of BACI of all trade flows important for the energy sector
- `country_codes_V202501.csv` – Country codes
- `product_codes_HS22_V202501.csv` – All product codes  
- `Surefire_product_codes_HS22_yellow.csv` – Product codes for the energy sector and yellow products  
- `Surefire_product_codes_HS22.csv` – Product codes for the energy sector

---

### 2. `Data_handling/`
Scripts for preparing and filtering datasets.  
- `CSV_creator.py` – Takes the .xlsx file and creates a CSV with the specific sheets needed  
- `Data_filter.py` – Filters out all trade flows which include the products from the CSV file

---

### 3. `Results_Analysis/`
Scripts for deeper exploration and visualization of results.  
- `eci_calculator.py` – Calculates the ECI value of each country and other stuff with the ecomplexity package  
- `ECI_Map.py` – Takes the results of the ECI calculation and plots it in a world map  

---

### 4. `Results/`
Generated outputs from the analysis, including country-level results and visualizations.  
- `eci_country_results_BACI.csv` – Results per country of ECI calculation of whole BACI dataset  
- `eci_country_results_Energy_yellow.csv` – Results per country of ECI calculation of Energy sector and yellow products  
- `eci_country_results_Energy.csv` – Results per country of ECI calculation of Energy sector 
- `ECI_Map_BACI.png` – World map of ECI values of whole BACI dataset
- `ECI_Map_Energy_yellow.png` – World map of ECI values of energy sector and yellow products
- `ECI_Map_Energy.png` – World map of ECI values of energy sector
- `eci_results_BACI.csv` – Whole results of ECI calculation of whole BACI dataset
- `eci_results_Energy_yellow.csv` – Whole results of ECI calculation of energy sector and yellow products
- `eci_results_Energy.csv` – Whole results of ECI calcuation of energy sector

---

- `.gitignore` – Ignores big files so as to not get error when pushing to github  
