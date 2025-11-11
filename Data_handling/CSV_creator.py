import pandas as pd

# Path to your Excel file
excel_path = r"C:\Users\marvi\OneDrive\Semester Thesis\Surefire_product_codes_HS22.xlsx"

yellow = 0

if yellow == 1:
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
    baci = pd.concat([df_first] + dfs_rest, ignore_index=True)
else:
    sheets_to_read = ["25", "26", "27", "28", "38", "44", "71", "72", "73", "74", "75", "76", "78", "79", "80", "81", "84", "85", "87", "90"]
    baci = pd.concat(
        [pd.read_excel(excel_path, sheet_name=sh, skiprows=1, header=None) for sh in sheets_to_read],
        ignore_index=True
    )

    # If only one column exists, split it into two
    if baci.shape[1] == 1:
        baci = baci[0].str.split(",", n=1, expand=True)
        baci.columns = ["code", "description"]

# --- FIX: if the Excel produced a single combined column, split it here ---
if "code, description" in baci.columns:
    # Drop any accidental header rows
    baci = baci[baci["code, description"] != "code, description"]

    # Split into two proper columns
    baci[["code", "description"]] = baci["code, description"].str.split(pat=",", n=1, expand=True)

    # Drop the old combined column
    baci = baci.drop(columns=["code, description"])

# Save into your Data folder
if yellow == 1:
    baci.to_csv("Data/Surefire_product_codes_HS22_yellow.csv", index=False)
else:
    baci.to_csv("Data/Surefire_product_codes_HS22.csv", index=False)

print("Combined CSV saved with", len(baci), "rows.")
print("Columns:", baci.columns.tolist())
print(baci.head())
