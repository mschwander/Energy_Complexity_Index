import pandas as pd
import os

def Data_filterHS22(product_codes, supplementary, year):

    energy_code_list = product_codes["code"].astype(str).tolist()
    
    baci = pd.read_csv(rf"C:\Users\marvi\OneDrive\Semester Thesis\BACI_HS22_V202501\BACI_HS22_Y{year}_V202501.csv")

    baci["k"] = baci["k"].astype(str)

    baci_energy = baci[baci["k"].isin(energy_code_list)]

    if supplementary:
        output_dir = f"01_Data/BACI/{year}/"
        os.makedirs(output_dir, exist_ok=True)  # create folder if missing
        save_path = os.path.join(output_dir, f"baci_energy_subset_supplementary_{year}.csv")
        baci_energy.to_csv(save_path, index=False)        
    else:
        output_dir = f"01_Data/BACI/{year}/"
        os.makedirs(output_dir, exist_ok=True)  # create folder if missing
        save_path = os.path.join(output_dir, f"baci_energy_subset_{year}.csv")
        baci_energy.to_csv(save_path, index=False)

    print("Filtered dataset saved with", len(baci_energy), "rows.")

    return baci_energy

def Data_filterHS96(product_codes, supplementary, year):

    energy_code_list = product_codes["code"].astype(str).tolist()
    
    baci = pd.read_csv(rf"C:\Users\marvi\OneDrive\Semester Thesis\BACI_HS96_V202501\BACI_HS96_Y{year}_V202501.csv")
    baci["k"] = baci["k"].astype(str)

    baci_energy = baci[baci["k"].isin(energy_code_list)]

    if supplementary:
        output_dir = f"01_Data/BACI/{year}/"
        os.makedirs(output_dir, exist_ok=True)  # create folder if missing
        save_path = os.path.join(output_dir, f"baci_energy_subset_supplementary_{year}.csv")
        baci_energy.to_csv(save_path, index=False)
    else:
        output_dir = f"01_Data/BACI/{year}/"
        os.makedirs(output_dir, exist_ok=True)  # create folder if missing
        save_path = os.path.join(output_dir, f"baci_energy_subset_{year}.csv")
        baci_energy.to_csv(save_path, index=False)
        
    print("Filtered dataset saved with", len(baci_energy), "rows.")

    return baci_energy

def Data_filterHS17(product_codes, supplementary, year):

    energy_code_list = product_codes["code"].astype(str).tolist()
    
    baci = pd.read_csv(rf"C:\Users\marvi\OneDrive\Semester Thesis\BACI_HS17_V202501\BACI_HS17_Y{year}_V202501.csv")
    baci["k"] = baci["k"].astype(str)

    baci_energy = baci[baci["k"].isin(energy_code_list)]

    if supplementary:
        output_dir = f"01_Data/BACI/{year}/"
        os.makedirs(output_dir, exist_ok=True)  # create folder if missing
        save_path = os.path.join(output_dir, f"baci_energy_subset_supplementary_{year}.csv")
        baci_energy.to_csv(save_path, index=False)
    else:
        output_dir = f"01_Data/BACI/{year}/"
        os.makedirs(output_dir, exist_ok=True)  # create folder if missing
        save_path = os.path.join(output_dir, f"baci_energy_subset_{year}.csv")
        baci_energy.to_csv(save_path, index=False)
        
    print("Filtered dataset saved with", len(baci_energy), "rows.")

    return baci_energy