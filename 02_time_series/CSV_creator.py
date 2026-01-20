import pandas as pd
import os


# Path to your Excel file
def CSV_creatorHS22(supplementary, year):
    excel_path = r"C:\Users\marvi\OneDrive\Semester Thesis\Surefire_product_codes_HS22.xlsx"

    if supplementary == 1:
        # Get all sheet names
        sheet_names = pd.ExcelFile(excel_path).sheet_names

        # Read the first sheet normally (keep headers)
        df_first = pd.read_excel(excel_path, sheet_name=sheet_names[0])

        # Read the remaining sheets, skipping the first row
        dfs_rest = [
        pd.read_excel(excel_path, sheet_name=sh, skiprows=1, header=None)
        for sh in sheet_names[1:]
        ]

        # Make sure the skipped sheets get the same column names as the first
        for df in dfs_rest:
            df.columns = df_first.columns

        # Concatenate everything into one DataFrame
        product_codes = pd.concat([df_first] + dfs_rest, ignore_index=True)
    else:
        sheets_to_read = ["25", "26", "27", "28", "38", "39", "44", "71", "72", "73", "74", "75", "76", "78", "79", "80", "81", "84", "86", "85", "87", "90"]
        product_codes = pd.concat([pd.read_excel(excel_path, sheet_name=sh, skiprows=1, header=None) for sh in sheets_to_read], ignore_index=True)

    if product_codes.shape[1] == 1:
        product_codes = product_codes.iloc[:, 0].str.split(",", n=1, expand=True)
        product_codes.columns = ["code", "description"]


    # --- FIX: if the Excel produced a single combined column, split it here ---
    if "code, description" in product_codes.columns:
        # Drop any accidental header rows
        product_codes = product_codes[product_codes["code, description"] != "code, description"]

        # Split into two proper columns
        product_codes[["code", "description"]] = product_codes["code, description"].str.split(pat=",", n=1, expand=True)

        # Drop the old combined column
        product_codes = product_codes.drop(columns=["code, description"])


    print(f"Combined HS22 CSV for year {year} saved with", len(product_codes), "rows.")
    #print("Columns:", product_codes.columns.tolist())
    #print(product_codes.head())

    # Save into your Data folder
    if supplementary == 1:
        output_dir = f"01_Data/BACI/{year}"
        os.makedirs(output_dir, exist_ok=True)  # create folder if missing

        save_path = os.path.join(output_dir, f"Surefire_product_codes_HS22_supplementary_{year}.csv")
        product_codes.to_csv(save_path, index=False)
    else:
        output_dir = f"01_Data/BACI/{year}"
        os.makedirs(output_dir, exist_ok=True)  # create folder if missing

        save_path = os.path.join(output_dir, f"Surefire_product_codes_HS22_{year}.csv")
        product_codes.to_csv(save_path, index=False)

    return product_codes


def CSV_creatorHS96(supplementary, year):
    excel_pathHS96 = r"C:\Users\marvi\OneDrive\Semester Thesis\Surefire_product_codes_HS96.xlsx"
   
    if supplementary == 1:
        # Get all sheet names
        sheet_names = pd.ExcelFile(excel_pathHS96).sheet_names

        # Read the first sheet normally (keep headers)
        df_first = pd.read_excel(excel_pathHS96, sheet_name=sheet_names[0])

        # Read the remaining sheets, skipping the first row
        dfs_rest = [
        pd.read_excel(excel_pathHS96, sheet_name=sh, skiprows=1, header=None)
        for sh in sheet_names[1:]
        ]

        # Make sure the skipped sheets get the same column names as the first
        for df in dfs_rest:
            df.columns = df_first.columns

        # Concatenate everything into one DataFrame
        product_codesHS96 = pd.concat([df_first] + dfs_rest, ignore_index=True)
    else:
        sheets_to_read = ["25", "26", "27", "28", "38", "39", "44", "71", "72", "73", "74", "75", "76", "78", "79", "80", "81", "84", "85", "87", "90"]
        product_codesHS96 = pd.concat([pd.read_excel(excel_pathHS96, sheet_name=sh, skiprows=1, header=None) for sh in sheets_to_read], ignore_index=True)


    if product_codesHS96.shape[1] == 1:
        product_codesHS96 = product_codesHS96.iloc[:, 0].str.split(",", n=1, expand=True)
        product_codesHS96.columns = ["code", "description"]


    # --- FIX: if the Excel produced a single combined column, split it here ---
    if "code, description" in product_codesHS96.columns:
        # Drop any accidental header rows
        product_codesHS96 = product_codesHS96[product_codesHS96["code, description"] != "code, description"]

        # Split into two proper columns
        product_codesHS96[["code", "description"]] = product_codesHS96["code, description"].str.split(pat=",", n=1, expand=True)

        # Drop the old combined column
        product_codesHS96 = product_codesHS96.drop(columns=["code, description"])


    print(f"Combined HS96 CSV for year {year} saved with", len(product_codesHS96), "rows.")
    #print("Columns:", product_codesHS96.columns.tolist())
    #print(product_codesHS96.head())

    # Save into your Data folder
    if supplementary == 1:
        output_dir = f"01_Data/BACI/{year}"
        os.makedirs(output_dir, exist_ok=True)  # create folder if missing
        save_path = os.path.join(output_dir, f"Surefire_product_codes_HS96_supplementary_{year}.csv")
        product_codesHS96.to_csv(save_path, index=False)
    else:
        output_dir = f"01_Data/BACI/{year}"
        os.makedirs(output_dir, exist_ok=True)  # create folder if missing
        save_path = os.path.join(output_dir, f"Surefire_product_codes_HS96_{year}.csv")
        product_codesHS96.to_csv(save_path, index=False)
        
    return product_codesHS96


def CSV_creatorHS17(supplementary, year):
    excel_pathHS17 = r"C:\Users\marvi\OneDrive\Semester Thesis\Surefire_product_codes_HS17.xlsx"
   
    sheets_to_read = ["87"]
    product_codesHS17 = pd.concat([pd.read_excel(excel_pathHS17, sheet_name=sh, skiprows=1, header=None) for sh in sheets_to_read], ignore_index=True)


    if product_codesHS17.shape[1] == 1:
        product_codesHS17 = product_codesHS17.iloc[:, 0].str.split(",", n=1, expand=True)
        product_codesHS17.columns = ["code", "description"]


    # --- FIX: if the Excel produced a single combined column, split it here ---
    if "code, description" in product_codesHS17.columns:
        # Drop any accidental header rows
        product_codesHS17 = product_codesHS17[product_codesHS17["code, description"] != "code, description"]

        # Split into two proper columns
        product_codesHS17[["code", "description"]] = product_codesHS17["code, description"].str.split(pat=",", n=1, expand=True)

        # Drop the old combined column
        product_codesHS17 = product_codesHS17.drop(columns=["code, description"])

    print(f"Combined HS 17 CSV for year {year} saved with", len(product_codesHS17), "rows.")
    #print("Columns:", product_codesHS96.columns.tolist())
    #print(product_codesHS96.head())

    # Save into your Data folder
    output_dir = f"01_Data/BACI/{year}"
    os.makedirs(output_dir, exist_ok=True)  # create folder if missing
    save_path = os.path.join(output_dir, f"Surefire_product_codes_HS17_{year}.csv")
    product_codesHS17.to_csv(save_path, index=False)

    return product_codesHS17