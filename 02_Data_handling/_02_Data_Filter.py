import pandas as pd
import os

def Data_filterHS22(product_codes, supplementary, year, baci_HS22_folder):

    energy_code_list = product_codes["code"].astype(str).tolist()
    baci_HS22_path = os.path.join(baci_HS22_folder, f"BACI_HS22_Y{year}_V202501.csv")
    baci_HS22 = pd.read_csv(baci_HS22_path)

    baci_HS22["k"] = baci_HS22["k"].astype(str)

    baci_energy = baci_HS22[baci_HS22["k"].isin(energy_code_list)]

    if supplementary:
        output_dir = f"01_Data/BACI/{year}/"
        os.makedirs(output_dir, exist_ok=True)
        save_path = os.path.join(output_dir, f"baci_energy_subset_supplementary_{year}.csv")
        baci_energy.to_csv(save_path, index=False)        
    else:
        output_dir = f"01_Data/BACI/{year}/"
        os.makedirs(output_dir, exist_ok=True)
        save_path = os.path.join(output_dir, f"baci_energy_subset_{year}.csv")
        baci_energy.to_csv(save_path, index=False)

    print("Filtered dataset saved with", len(baci_energy), "rows.")

    return baci_energy

def Data_filterHS96(product_codes, supplementary, year, baci_HS96_folder):

    energy_code_list = product_codes["code"].astype(str).tolist()
    
    baci_HS96_path = os.path.join(baci_HS96_folder, f"BACI_HS96_Y{year}_V202501.csv")
    baci = pd.read_csv(baci_HS96_path)
    baci["k"] = baci["k"].astype(str)

    baci_energy = baci[baci["k"].isin(energy_code_list)]

    if supplementary:
        output_dir = f"01_Data/BACI/{year}/"
        os.makedirs(output_dir, exist_ok=True)
        save_path = os.path.join(output_dir, f"baci_energy_subset_supplementary_{year}.csv")
        baci_energy.to_csv(save_path, index=False)
    else:
        output_dir = f"01_Data/BACI/{year}/"
        os.makedirs(output_dir, exist_ok=True)
        save_path = os.path.join(output_dir, f"baci_energy_subset_{year}.csv")
        baci_energy.to_csv(save_path, index=False)
        
    print("Filtered dataset saved with", len(baci_energy), "rows.")

    return baci_energy

def Data_filterHS17(product_codes, supplementary, year, baci_HS17_folder):

    energy_code_list = product_codes["code"].astype(str).tolist()
    
    baci_HS17_path = os.path.join(baci_HS17_folder, f"BACI_HS17_Y{year}_V202501.csv")
    baci = pd.read_csv(baci_HS17_path)
    baci["k"] = baci["k"].astype(str)

    baci_energy = baci[baci["k"].isin(energy_code_list)]

    if supplementary:
        output_dir = f"01_Data/BACI/{year}/"
        os.makedirs(output_dir, exist_ok=True)
        save_path = os.path.join(output_dir, f"baci_energy_subset_supplementary_{year}.csv")
        baci_energy.to_csv(save_path, index=False)
    else:
        output_dir = f"01_Data/BACI/{year}/"
        os.makedirs(output_dir, exist_ok=True)
        save_path = os.path.join(output_dir, f"baci_energy_subset_{year}.csv")
        baci_energy.to_csv(save_path, index=False)
        
    print("Filtered dataset saved with", len(baci_energy), "rows.")

    return baci_energy