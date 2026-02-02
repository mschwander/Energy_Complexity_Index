import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.cm as cm  # Import colormaps
import numpy as np
import math

def PCI_time_series(years, supplementary, save_folder, HS_code):
    dfs = []
    first_year = years[0]
    last_year = years[-1]
    save_path = f"{save_folder}/Time_Series/PCI"
    
    for year in years:
        if supplementary:
            file_path = f"{save_folder}/{year}/supplementary/eci_results_Energy_supplementary_{year}.csv"
        else:
            file_path = f"{save_folder}/{year}/Energy/eci_results_Energy_{year}.csv"
        
        if not os.path.exists(file_path):
            print(f"Warning: File not found: {file_path}")
            continue
        df = pd.read_csv(file_path)

        if 'hs_product_code' not in df.columns or 'pci' not in df.columns:
            print(f"Skipping {year}: Missing required columns.")
            continue

        df['hs_product_code'] = df['hs_product_code'].astype(str).str.replace(r'\.0$', '', regex=True)
        df['hs_product_code'] = df['hs_product_code'].str.zfill(6)

        if HS_code == 4:
            df['product_code'] = df['hs_product_code'].str[:4]
            df = df.groupby('product_code')['pci'].mean().reset_index()
            
            print(f"Year {year}: Aggregated to {len(df)} HS4 codes.")
        else:
            df['product_code'] = df['hs_product_code']
            df = df[['product_code', 'pci']].copy()
            df = df.drop_duplicates(subset=['product_code'])

        df = df.rename(columns={"pci": f"pci_{year}"})
        df = df[['product_code', f"pci_{year}"]]
        dfs.append(df)
        print(f"Loaded PCI data for year: {year} with HS_code{HS_code}")

    if not dfs:
        print("No data loaded. Check your file paths.")
        return None

    merged = dfs[0]
    for df in dfs[1:]:
        merged = merged.merge(df, on="product_code", how="outer")

    for year in years:
        col = f"pci_{year}"
        if col in merged.columns:
            merged[f"pci_rank_{year}"] = merged[col].rank(ascending=False, method='min')

    merged = merged.replace(r'^\s*$', np.nan, regex=True)
    prod_names = pd.read_csv("01_Data/product_codes_HS96_V202501.csv")
    if 'code' in prod_names.columns: # Common synonym
                prod_names.rename(columns={'code': 'product_code'}, inplace=True)
    if HS_code == 6:
        merged = pd.merge(merged, prod_names, on='product_code', how='left')
        cols = merged.columns.tolist()
        
        # Identify likely description columns
        desc_cols = [c for c in cols if 'name' in c or 'description' in c]
        first_cols = ['product_code'] + desc_cols
        remaining = [c for c in cols if c not in first_cols]
        merged = merged[first_cols + remaining]
        print("Merged product descriptions.")
    else:
        1. Create HS4 column in metadata
        prod_names['hs4_code'] = prod_names['product_code'].str[:4]
        prod_names_hs4 = prod_names.drop_duplicates(subset=['hs4_code'], keep='first').copy()
        cols = merged.columns.tolist()
        prod_names_to_merge = prod_names_hs4[['hs4_code', 'description']].copy()
        prod_names_to_merge = prod_names_to_merge.rename(columns={'hs4_code': 'product_code'})
        
        merged = pd.merge(merged, prod_names_to_merge, on='product_code', how='left')
        
        cols = merged.columns.tolist()
        desc_cols = [c for c in cols if 'name' in c or 'description' in c]
        first_cols = ['product_code'] + desc_cols
        remaining = [c for c in cols if c not in first_cols]
        merged = merged[first_cols + remaining]
        print("Merged product descriptions.")

    output_dir = f"{save_path}/{first_year}-{last_year}/"
    os.makedirs(output_dir, exist_ok=True)
    
    folder_tag = "4" if HS_code == 4 else "6"
    if supplementary:
        save_file = os.path.join(output_dir, f"PCI_time_series_Energy_supplementary_HS_{folder_tag}_{first_year}-{last_year}.csv")
    else:
        save_file = os.path.join(output_dir, f"PCI_time_series_Energy_HS_{folder_tag}_{first_year}-{last_year}.csv")

    merged.to_csv(save_file, index=False, na_rep="NaN")
    print(f"Saved PCI time series to {save_file}")
    
    return merged

def PCI_time_line_plot_TopBottom(df, years, save_folder, supplementary, first, HS_code):
    first_year = years[0]
    last_year = years[-1]
    save_path_base = f"{save_folder}/Time_Series/PCI"
    
    target_year = first_year if first == 1 else last_year
    rank_col = f"pci_rank_{target_year}"
    
    if rank_col not in df.columns:
        print(f"Error: Column {rank_col} not found.")
        return
    
    valid_df = df.dropna(subset=[rank_col])

    top_30 = valid_df.nsmallest(30, rank_col)
    bottom_30 = valid_df.nlargest(30, rank_col)

    def plot_subset(subset_df, title_prefix, filename_suffix):
        plt.figure(figsize=(14, 8))
        ax = plt.gca()
        ax.invert_yaxis()  
        # Generate 30 distinct colors
        colors = plt.cm.nipy_spectral(np.linspace(0, 1, len(subset_df)))
        
        for i, (_, row) in enumerate(subset_df.iterrows()):
            ranks = [row.get(f"pci_rank_{y}", np.nan) for y in years]
            
            if all(pd.isna(x) for x in ranks):
                continue
            
            # Create Label: Truncate description to 20 chars
            desc = str(row.get('description', row['product_code']))
            label_text = (desc[:20] + '..') if len(desc) > 20 else desc
            plt.plot(years, ranks, marker="o", linewidth=1.5, alpha=0.8, 
                     label=label_text, color=colors[i])

        plt.xticks(years, rotation=45, ha="right")
        plt.ylabel("PCI Rank")
        
        data_type = "Supplementary" if supplementary else "Energy"
        plt.title(f"{title_prefix} Products by PCI Rank ({first_year}-{last_year}) - {data_type}")
        plt.grid(True, linestyle="--", alpha=0.5)

        plt.legend(
            loc='upper center', 
            bbox_to_anchor=(0.5, -0.15), 
            fancybox=True, 
            shadow=True, 
            ncol=5,  # 5 columns for 30 items
            fontsize='x-small'
        )

        plt.tight_layout()
        plt.subplots_adjust(bottom=0.25)

        output_dir = f"{save_path_base}/{first_year}-{last_year}/"
        os.makedirs(output_dir, exist_ok=True)
        
        sort_type = "First" if first == 1 else "Last"
        HS_type = "HS_4" if HS_code == 4 else "HS_6"
        filename = f"{filename_suffix}_PCI_time_series_{data_type}_{HS_type}_{sort_type}_{first_year}-{last_year}.png"
        
        save_path = os.path.join(output_dir, filename)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved: {save_path}")

    plot_subset(top_30, "Top 30", "Top_30")
    plot_subset(bottom_30, "Bottom 30", "Bottom_30")

def RCA_time_line_plot_global1(pci_df, country_iso, years, number_products, data_folder, supplementary, first, HS_code):
    first_year = years[0]
    last_year = years[-1]
    target_year = first_year if first == 1 else last_year
    
    if supplementary:
        target_path = f"{data_folder}/{target_year}/supplementary/eci_results_Energy_supplementary_{target_year}.csv"
    else:
        target_path = f"{data_folder}/{target_year}/Energy/eci_results_Energy_{target_year}.csv"

    if not os.path.exists(target_path):
        print(f"Error: Could not find country data for {target_year} at {target_path}")
        return

    print(f"Loading target year {target_year} data for selection...")
    target_df = pd.read_csv(target_path)

    target_exports = target_df[
        (target_df['location_code'] == country_iso) & 
        (target_df['rca'] > 1)
    ].copy()
    
    if target_exports.empty and 'country_iso3' in target_df.columns:
         target_exports = target_df[
            (target_df['country_iso3'] == country_iso) & 
            (target_df['rca'] > 1)
        ].copy()

    if target_exports.empty:
        print(f"Warning: No products with RCA > 1 found for {country_iso} in {target_year}.")
        return

    if 'hs_product_code' in target_exports.columns:
        target_exports['hs_product_code'] = target_exports['hs_product_code'].astype(str).str.replace(r'\.0$', '', regex=True).str.zfill(6)
    
    if HS_code == 4:
        target_exports['code_match'] = target_exports['hs_product_code'].str[:4]
    else:
        target_exports['code_match'] = target_exports['hs_product_code']
        
    valid_codes_target = set(target_exports['code_match'].unique())
    
    pci_df['product_code'] = pci_df['product_code'].astype(str).str.zfill(4 if HS_code == 4 else 6)
    
    export_codes = valid_codes_target


    subset_df = pci_df[pci_df['product_code'].isin(export_codes)].copy()
    
    if subset_df.empty:
        print("Error: No matching products found in the provided PCI dataframe.")
        return

    rank_col = f"pci_rank_{target_year}"
    valid_subset = subset_df.dropna(subset=[rank_col])
    top_products = valid_subset.nsmallest(number_products, rank_col)
    bottom_products = valid_subset.nlargest(number_products, rank_col)

    def plot_subset_rca_global(data, title_prefix, suffix, HS_code, first):
        plt.figure(figsize=(14, 8))
        ax = plt.gca()
        ax.invert_yaxis()

        cycle_len = 8  # Change marker every 8 lines
        
        # Generate exactly 8 distinct colors to cycle through
        # You can change 'nipy_spectral' to 'tab10' or 'Set1' for even better distinction
        base_colors = plt.cm.nipy_spectral(np.linspace(0, 0.9, cycle_len))
        
        # Define your sequence of markers: 
        # 'o'=circle, '^'=triangle up, 's'=square, 'D'=diamond, 'v'=triangle down
        markers = ['o', '^', 's', 'D', 'v', 'P', 'X', '*'] 

        for i, (_, row) in enumerate(data.iterrows()):
            ranks = [row.get(f"pci_rank_{y}", np.nan) for y in years]
            
            if all(pd.isna(x) for x in ranks):
                continue
 
            current_color = base_colors[i % cycle_len]
            
            marker_idx = (i // cycle_len) % len(markers) # The % len(markers) is a safety limit
            current_marker = markers[marker_idx]
            desc = str(row.get('description', row['product_code']))
            label_text = (desc[:25] + '..') if len(desc) > 25 else desc
            
            plt.plot(years, ranks, marker=current_marker, linewidth=1.5, alpha=0.8, 
                    label=label_text, color=current_color)

        plt.xticks(years, rotation=45, ha="right")
        plt.ylabel("PCI Rank (Global)")
        
        data_type = "Supplementary" if supplementary else "Energy"
        hs_str = "HS4" if HS_code == 4 else "HS6"
        plt.title(f"{country_iso} {title_prefix} Exports (RCA>1 in {target_year}) - {data_type} {hs_str}")
        plt.grid(True, linestyle="--", alpha=0.5)

        plt.legend(
            loc='upper center', 
            bbox_to_anchor=(0.5, -0.15), 
            fancybox=True, 
            shadow=True, 
            ncol=5, 
            fontsize='x-small'
        )

        plt.tight_layout()
        plt.subplots_adjust(bottom=0.25)
        save_path_base = f"{data_folder}/Time_Series/PCI/{years[0]}-{years[-1]}/{country_iso}/Global_Ranking/"
        os.makedirs(save_path_base, exist_ok=True)
        start_data = "first" if first == 1 else "last"
        filename = f"RCA_{country_iso}_{suffix}_{title_prefix.replace(' ', '_')}_HS_code_{HS_code}_{start_data}_{first_year}-{last_year}.png"
        full_save_path = os.path.join(save_path_base, filename)
        
        plt.savefig(full_save_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved plot: {full_save_path}")

    # 7. GENERATE PLOTS
    plot_subset_rca_global(top_products, f"Top {number_products} Complex", "Complexity", HS_code, first)
    plot_subset_rca_global(bottom_products, f"Bottom {number_products} Complex", "Complexity", HS_code, first)

def RCA_time_line_plot_global(pci_df, country_iso, years, number_products, data_folder, supplementary, first, HS_code): 
    first_year = years[0]
    last_year = years[-1]
    target_year = first_year if first == 1 else last_year
    
    if supplementary:
        target_path = f"{data_folder}/{target_year}/supplementary/eci_results_Energy_supplementary_{target_year}.csv"
    else:
        target_path = f"{data_folder}/{target_year}/Energy/eci_results_Energy_{target_year}.csv"

    if not os.path.exists(target_path):
        print(f"Error: Could not find country data for {target_year} at {target_path}")
        return

    print(f"Loading target year {target_year} data for {country_iso}...")
    target_df = pd.read_csv(target_path)

    target_exports = target_df[
        (target_df['location_code'] == country_iso) & 
        (target_df['rca'] > 1)
    ].copy()
    
    if target_exports.empty and 'country_iso3' in target_df.columns:
         target_exports = target_df[
            (target_df['country_iso3'] == country_iso) & 
            (target_df['rca'] > 1)
        ].copy()

    if target_exports.empty:
        print(f"Warning: No products with RCA > 1 found for {country_iso} in {target_year}.")
        return

    if 'hs_product_code' in target_exports.columns:
        target_exports['hs_product_code'] = target_exports['hs_product_code'].astype(str).str.replace(r'\.0$', '', regex=True).str.zfill(6)
    
    if HS_code == 4:
        target_exports['code_match'] = target_exports['hs_product_code'].str[:4]
    else:
        target_exports['code_match'] = target_exports['hs_product_code']

    export_codes = set(target_exports['code_match'].unique())
    print(f"Identified {len(export_codes)} products with RCA > 1 in target year.")
    pci_df['product_code'] = pci_df['product_code'].astype(str).str.zfill(4 if HS_code == 4 else 6)
    
    subset_df = pci_df[pci_df['product_code'].isin(export_codes)].copy()
    
    if subset_df.empty:
        print("Error: No matching products found in PCI dataframe.")
        return
    rank_col = f"pci_rank_{target_year}"
    valid_subset = subset_df.dropna(subset=[rank_col])
    
    top_df = valid_subset.nsmallest(number_products, rank_col).copy()
    bottom_df = valid_subset.nlargest(number_products, rank_col).copy()

    print(f"Retrieving RCA history for {len(years)} years...")

    for year in years:
        if supplementary:
            y_path = f"{data_folder}/{year}/supplementary/eci_results_Energy_supplementary_{year}.csv"
        else:
            y_path = f"{data_folder}/{year}/Energy/eci_results_Energy_{year}.csv"
            
        if not os.path.exists(y_path):
            continue
            
        y_df = pd.read_csv(y_path)
        y_country = y_df[y_df['location_code'] == country_iso].copy()
        if y_country.empty and 'country_iso3' in y_df.columns:
            y_country = y_df[y_df['country_iso3'] == country_iso].copy()
        
        if 'hs_product_code' in y_country.columns:
            y_country['hs_product_code'] = y_country['hs_product_code'].astype(str).str.replace(r'\.0$', '', regex=True).str.zfill(6)
            
        if HS_code == 4:
            y_country['code_match'] = y_country['hs_product_code'].str[:4]
            rca_map = y_country.set_index('code_match')['rca']
        else:
            rca_map = y_country.set_index('hs_product_code')['rca']
            
        top_df[f'rca_{year}'] = top_df['product_code'].map(rca_map)
        bottom_df[f'rca_{year}'] = bottom_df['product_code'].map(rca_map)

    def plot_subset_rca_global(data, title_prefix, suffix, HS_code, first):
        plt.figure(figsize=(14, 8))
        ax = plt.gca()
        ax.invert_yaxis()

        # Styling
        cycle_len = 8 
        base_colors = plt.cm.nipy_spectral(np.linspace(0, 0.9, cycle_len))
        markers = ['o', '^', 's', 'D', 'v', 'P', 'X', '*'] 

        for i, (_, row) in enumerate(data.iterrows()):
            ranks = [row.get(f"pci_rank_{y}", np.nan) for y in years]
            
            if all(pd.isna(x) for x in ranks):
                continue

            current_color = base_colors[i % cycle_len]
            marker_idx = (i // cycle_len) % len(markers)
            current_marker = markers[marker_idx]

            desc = str(row.get('description', row['product_code']))
            label_text = (desc[:25] + '..') if len(desc) > 25 else desc

            plt.plot(years, ranks, marker=current_marker, linewidth=1.5, alpha=0.8, 
                     label=label_text, color=current_color)
            
            # --- RED BORDER OVERLAY ---
            bad_years = []
            bad_ranks = []
            
            for y_idx, year in enumerate(years):
                rank_val = ranks[y_idx]
                rca_val = row.get(f"rca_{year}", np.nan)
                
                if pd.notna(rank_val) and (pd.isna(rca_val) or rca_val <= 1):
                    bad_years.append(year)
                    bad_ranks.append(rank_val)
            
            if bad_years:
                plt.scatter(bad_years, bad_ranks, 
                            marker=current_marker, 
                            s=60, 
                            facecolors='none', 
                            edgecolors='red', 
                            linewidths=2.0, 
                            zorder=10)

        plt.xticks(years, rotation=45, ha="right")
        plt.ylabel("PCI Rank (Global)")
        
        data_type = "Supplementary" if supplementary else "Energy"
        hs_str = "HS4" if HS_code == 4 else "HS6"
        plt.title(f"{country_iso} {title_prefix} Exports (RCA>1 in {target_year}) - {data_type} {hs_str}")
        plt.grid(True, linestyle="--", alpha=0.5)

        plt.legend(
            loc='upper center', 
            bbox_to_anchor=(0.5, -0.15), 
            fancybox=True, shadow=True, ncol=5, fontsize='x-small'
        )

        plt.tight_layout()
        plt.subplots_adjust(bottom=0.25)

        save_path_base = f"{data_folder}/Time_Series/PCI/{years[0]}-{years[-1]}/{country_iso}/Global_Ranking/"
        os.makedirs(save_path_base, exist_ok=True)
        start_data = "first" if first == 1 else "last"
        filename = f"RCA_{country_iso}_{suffix}_{title_prefix.replace(' ', '_')}_HS_code_{HS_code}_{start_data}_{first_year}-{last_year}.png"
        full_save_path = os.path.join(save_path_base, filename)
        
        plt.savefig(full_save_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved plot: {full_save_path}")

    plot_subset_rca_global(top_df, f"Top {number_products} Complex", "Complexity", HS_code, first)
    plot_subset_rca_global(bottom_df, f"Bottom {number_products} Complex", "Complexity", HS_code, first)

def RCA_time_line_plot(pci_df, country_iso, years, number_products, data_folder, supplementary, first, HS_code):
    
    first_year = years[0]
    last_year = years[-1]
    target_year = first_year if first == 1 else last_year
    
    if supplementary:
        target_path = f"{data_folder}/{target_year}/supplementary/eci_results_Energy_supplementary_{target_year}.csv"
    else:
        target_path = f"{data_folder}/{target_year}/Energy/eci_results_Energy_{target_year}.csv"

    if not os.path.exists(target_path):
        print(f"Error: Could not find country data for {target_year} at {target_path}")
        return

    print(f"Loading target year {target_year} data for selection...")
    target_df = pd.read_csv(target_path)

    target_exports = target_df[
        (target_df['location_code'] == country_iso) & 
        (target_df['rca'] > 1)
    ].copy()
    
    if target_exports.empty and 'country_iso3' in target_df.columns:
         target_exports = target_df[
            (target_df['country_iso3'] == country_iso) & 
            (target_df['rca'] > 1)
        ].copy()

    if target_exports.empty:
        print(f"Warning: No products with RCA > 1 found for {country_iso} in {target_year}.")
        return

    if 'hs_product_code' in target_exports.columns:
        target_exports['hs_product_code'] = target_exports['hs_product_code'].astype(str).str.replace(r'\.0$', '', regex=True).str.zfill(6)
    
    if HS_code == 4:
        target_exports['code_match'] = target_exports['hs_product_code'].str[:4]
    else:
        target_exports['code_match'] = target_exports['hs_product_code']
        
    valid_codes_target = set(target_exports['code_match'].unique())
    pci_df['product_code'] = pci_df['product_code'].astype(str).str.zfill(4 if HS_code == 4 else 6)
    
    selection_subset = pci_df[pci_df['product_code'].isin(valid_codes_target)].copy()    

    raw_pci_col = f"pci_{target_year}"
    if raw_pci_col not in selection_subset.columns:
        print(f"Error: PCI column {raw_pci_col} missing.")
        return
        
    selection_subset['selection_rank'] = selection_subset[raw_pci_col].rank(ascending=False, method='min')
    
    top_codes = selection_subset.nsmallest(number_products, 'selection_rank')['product_code'].tolist()
    bottom_codes = selection_subset.nlargest(number_products, 'selection_rank')['product_code'].tolist()
    
    top_df = pci_df[pci_df['product_code'].isin(top_codes)].copy()
    bottom_df = pci_df[pci_df['product_code'].isin(bottom_codes)].copy()
    
    print(f"Calculating dynamic local ranks for {len(years)} years...")
    
    for year in years:
        if supplementary:
            y_path = f"{data_folder}/{year}/supplementary/eci_results_Energy_supplementary_{year}.csv"
        else:
            y_path = f"{data_folder}/{year}/Energy/eci_results_Energy_{year}.csv"
            
        if not os.path.exists(y_path):
            continue
            
        y_df = pd.read_csv(y_path)

        y_exports = y_df[
            (y_df['location_code'] == country_iso) & 
            (y_df['rca'] > 1)
        ].copy()
        
        if y_exports.empty and 'country_iso3' in y_df.columns:
            y_exports = y_df[
                (y_df['country_iso3'] == country_iso) & 
                (y_df['rca'] > 1)
            ].copy()
            
        if 'hs_product_code' in y_exports.columns:
            y_exports['hs_product_code'] = y_exports['hs_product_code'].astype(str).str.replace(r'\.0$', '', regex=True).str.zfill(6)
            
        if HS_code == 4:
            valid_codes_year = set(y_exports['hs_product_code'].str[:4].unique())
        else:
            valid_codes_year = set(y_exports['hs_product_code'].unique())
            
        subset_year = pci_df[pci_df['product_code'].isin(valid_codes_year)].copy()

        pci_col = f"pci_{year}"
        if pci_col in subset_year.columns:
            subset_year[f'local_rank_{year}'] = subset_year[pci_col].rank(ascending=False, method='min')            
            rank_map = subset_year.set_index('product_code')[f'local_rank_{year}']
            top_df[f'local_rank_{year}'] = top_df['product_code'].map(rank_map)
            bottom_df[f'local_rank_{year}'] = bottom_df['product_code'].map(rank_map)
        else:
            top_df[f'local_rank_{year}'] = np.nan
            bottom_df[f'local_rank_{year}'] = np.nan
    
    def plot_subset_local(data, title_prefix, suffix, HS_code, first):
        plt.figure(figsize=(10, 8))
        ax = plt.gca()
        ax.invert_yaxis()

        # Setup Cyclic Styling
        cycle_len = 8 
        base_colors = plt.cm.nipy_spectral(np.linspace(0, 0.9, cycle_len))
        markers = ['o', '^', 's', 'D', 'v', 'P', 'X', '*'] 

        for i, (_, row) in enumerate(data.iterrows()):
            ranks = [row.get(f"local_rank_{y}", np.nan) for y in years]
            
            if all(pd.isna(x) for x in ranks):
                continue
            
            # Styling
            current_color = base_colors[i % cycle_len]
            marker_idx = (i // cycle_len) % len(markers)
            current_marker = markers[marker_idx]

            # Label
            desc = str(row.get('description', row['product_code']))
            label_text = (desc[:25] + '..') if len(desc) > 25 else desc

            plt.plot(years, ranks, marker=current_marker, linewidth=1.5, alpha=0.8, 
                     label=label_text, color=current_color)

        plt.xticks(years, rotation=45, ha="right")
        plt.ylabel("PCI Rank (Country Specific)")
        
        data_type = "Supplementary" if supplementary else "Energy"
        hs_str = "HS4" if HS_code == 4 else "HS6"
        plt.title(f"{country_iso} {title_prefix} Exports (RCA>1) - Local Ranking - {data_type} {hs_str}")
        plt.grid(True, linestyle="--", alpha=0.5)

        plt.legend(
            loc='upper center', 
            bbox_to_anchor=(0.5, -0.15), 
            fancybox=True, shadow=True, ncol=5, fontsize='x-small'
        )

        plt.tight_layout()
        plt.subplots_adjust(bottom=0.25)

        save_path_base = f"{data_folder}/Time_Series/PCI/{years[0]}-{years[-1]}/{country_iso}/local_Ranking/"
        os.makedirs(save_path_base, exist_ok=True)
        start_data = "first" if first == 1 else "last"
        filename = f"LocalRank_{country_iso}_{suffix}_{title_prefix.replace(' ', '_')}_HS{HS_code}_{start_data}_{first_year}-{last_year}.png"
        full_save_path = os.path.join(save_path_base, filename)
        
        plt.savefig(full_save_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved plot: {full_save_path}")

    def plot_subset_rca_global(data, title_prefix, suffix, HS_code, first):
        plt.figure(figsize=(10, 8))
        ax = plt.gca()
        ax.invert_yaxis()

        # --- 1. SETUP CYCLIC STYLING ---
        cycle_len = 8  # Change marker every 8 lines
        base_colors = plt.cm.nipy_spectral(np.linspace(0, 0.9, cycle_len))
        markers = ['o', '^', 's', 'D', 'v', 'P', 'X', '*'] 

        for i, (_, row) in enumerate(data.iterrows()):
            ranks = [row.get(f"pci_rank_{y}", np.nan) for y in years]
            
            if all(pd.isna(x) for x in ranks):
                continue
            
            current_color = base_colors[i % cycle_len]
            
            marker_idx = (i // cycle_len) % len(markers)
            current_marker = markers[marker_idx]

            desc = str(row.get('description', row['product_code']))
            label_text = (desc[:25] + '..') if len(desc) > 25 else desc
            
            plt.plot(years, ranks, marker=current_marker, linewidth=1.5, alpha=0.8, 
                    label=label_text, color=current_color)

        plt.xticks(years, rotation=45, ha="right")
        plt.ylabel("PCI Rank (Global)")
        
        data_type = "Supplementary" if supplementary else "Energy"
        hs_str = "HS4" if HS_code == 4 else "HS6"
        plt.title(f"{country_iso} {title_prefix} Exports (RCA>1 in {target_year}) - {data_type} {hs_str}")
        plt.grid(True, linestyle="--", alpha=0.5)

        plt.legend(
            loc='upper center', 
            bbox_to_anchor=(0.5, -0.15), 
            fancybox=True, 
            shadow=True, 
            ncol=5, 
            fontsize='x-small'
        )

        plt.tight_layout()
        plt.subplots_adjust(bottom=0.25)

        save_path_base = f"{data_folder}/Time_Series/PCI/{years[0]}-{years[-1]}/{country_iso}/Global_Ranking/"
        os.makedirs(save_path_base, exist_ok=True)
        start_data = "first" if first == 1 else "last"
        filename = f"RCA_{country_iso}_{suffix}_{title_prefix.replace(' ', '_')}_HS_code_{HS_code}_{start_data}_{first_year}-{last_year}.png"
        full_save_path = os.path.join(save_path_base, filename)
        
        plt.savefig(full_save_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved plot: {full_save_path}")


    #GENERATE PLOTS
    plot_subset_rca_global(top_df, f"Top {number_products} Complex", "Complexity", HS_code, first)
    plot_subset_rca_global(bottom_df, f"Bottom {number_products} Complex", "Complexity", HS_code, first)

    plot_subset_local(top_df, f"Top {number_products} Complex", "Complexity", HS_code, first)
    plot_subset_local(bottom_df, f"Bottom {number_products} Complex", "Complexity", HS_code, first)

##############################################################################################################################
##############################################################################################################################

'''Example Usage'''
'''
# PCI_time_line_plot_TopBottom(df_pci, years_list, "03_Results", supplementary=True, first=0)

#years = [1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 
#         2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013,
#         2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023]
#years = [2002, 2003, 2004, 2005, 2006]
#years = [2007, 2008, 2009, 2010, 2011, 2012]
#years = [2013, 2014, 2015, 2016, 2017, 2018]
years = [2019, 2020, 2021, 2022, 2023]

supplementary = 1
save_folder = "03_Results"
HS_codes = [4, 6]
HS_code_singular = 6
first = 1
number_products = [15, 20]
#country_list = ["AUS", "CHE", "DEU", "USA", "CHN", "ARE", "RUS",  "POL" ] #"HRV", "GBR"]
country_list = ["RUS"]
df = PCI_time_series(years, supplementary, save_folder, HS_code_singular)

#df = pd.read_csv(f"03_Results/Time_Series/PCI/{years[0]}-{years[-1]}/PCI_time_series_Energy_supplementary_HS_{HS_code_singular}_{years[0]}-{years[-1]}.csv")

#PCI_time_line_plot_TopBottom(df, years, save_folder, supplementary, first)

#RCA_time_line_plot_global(df, "CHE", years, 20, save_folder, supplementary, first, HS_code_singular)
#RCA_time_line_plot_local(df, "CHE", years, 20, save_folder, supplementary, first, HS_code_singular)
for country in country_list:
    for first in [0, 1]:
        if HS_code_singular == 4:
            df = pd.read_csv(f"03_Results/Time_Series/PCI/{years[0]}-{years[-1]}/PCI_time_series_Energy_supplementary_HS_4_{years[0]}-{years[-1]}.csv")
        else:
            df = pd.read_csv(f"03_Results/Time_Series/PCI/{years[0]}-{years[-1]}/PCI_time_series_Energy_supplementary_HS_6_{years[0]}-{years[-1]}.csv")
        
        for number_product in number_products:
            #RCA_time_line_plot_local(df, country, years, number_product, save_folder, supplementary, first, HS_code_singular)
            #RCA_time_line_plot_global1(df, country, years, number_product, save_folder, supplementary, first, HS_code_singular)
            RCA_time_line_plot(df, country, years, number_product, save_folder, supplementary, first, HS_code_singular)  

#'''