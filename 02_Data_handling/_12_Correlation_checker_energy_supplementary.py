import pandas as pd
import numpy as np

df1 = pd.read_csv("03_Results/2023/Energy/eci_country_results_Energy_2023.csv")
df2 = pd.read_csv("03_Results/2023/supplementary/eci_country_results_Energy_supplementary_2023.csv")

df1_clean = df1[['year', 'country_iso3', 'country_name', 'eci']].rename(columns={'eci': 'eci_core'})
df2_clean = df2[['year', 'country_iso3', 'country_name', 'eci']].rename(columns={'eci': 'eci_supplementary'})

merged = pd.merge(df1_clean, df2_clean, on=['year', 'country_iso3'], how='inner')
#print(merged.columns.tolist())
merged['name_len'] = merged['country_name_x'].str.len()
merged = merged.sort_values('name_len')
merged = merged.drop_duplicates(subset=['year', 'eci_core', 'eci_supplementary'], keep='first')
merged = merged.drop(columns=['name_len'])

# ---Correlation Test ---
# Calculate Pearson correlation (standard) and Spearman (rank-based)
corr_pearson = merged['eci_core'].corr(merged['eci_supplementary'], method='pearson')
corr_spearman = merged['eci_core'].corr(merged['eci_supplementary'], method='spearman')

print(f"--- Global Correlation Results ---")
print(f"Pearson Correlation (Value linearity): {corr_pearson:.4f}")
print(f"Spearman Correlation (Rank order):     {corr_spearman:.4f}")
print("-" * 30)

merged['eci_diff_abs'] = (merged['eci_core'] - merged['eci_supplementary']).abs()
merged['rank_1'] = merged.groupby('year')['eci_core'].rank(ascending=False)
merged['rank_2'] = merged.groupby('year')['eci_supplementary'].rank(ascending=False)
merged['rank_diff_abs'] = (merged['rank_1'] - merged['rank_2']).abs()

top_20_rank_diff = merged.sort_values(by='rank_diff_abs', ascending=False).head(20)

cols_rank = ['year', 'country_name_x', 'rank_1', 'rank_2', 'rank_diff_abs']
print("\n--- Top 20 RANK Mismatches (Position Shift) ---")
print(top_20_rank_diff[cols_rank].to_string(index=False))

top_20_val_diff = merged.sort_values(by='eci_diff_abs', ascending=False).head(20)

cols_val = ['year', 'country_name_x', 'eci_core', 'eci_supplementary', 'eci_diff_abs']
print("\n--- Top 20 VALUE Mismatches (Absolute ECI Diff) ---")
print(top_20_val_diff[cols_val].to_string(index=False))