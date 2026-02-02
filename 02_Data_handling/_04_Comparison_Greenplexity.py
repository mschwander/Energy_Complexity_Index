import pandas as pd
import os
from ecomplexity import ecomplexity


def PCI_comparison(cdata, year, supplementary, pci_greenplexity, save_folder):
    pci_computed = cdata[['hs_product_code', 'pci']].copy()
    pci_computed.rename(columns={'pci': 'pci_computed'}, inplace=True).drop_duplicates()
    pci_compare = pd.merge(pci_computed, pci_greenplexity, on='hs_product_code', how='inner')
    
    if supplementary == 1:
        output_dir = f"{save_folder}/{year}/supplementary"
        os.makedirs(output_dir, exist_ok=True)
        save_path = os.path.join(output_dir, "PCI_comparison_Energy_supplementary_greenplexity.csv")
        pci_compare.to_csv(save_path, index=False)
        print(f"Saved PCI comparison to {save_path}")
        correlation = pci_compare[['pci_computed', 'pci_greenplexity']].corr().iloc[0, 1]
        print(f"PCI correlation (Energy supplementary vs Atlas): {correlation:.4f}")
    else:
        output_dir = f"{save_folder}/{year}/Energy"
        os.makedirs(output_dir, exist_ok=True)
        save_path = os.path.join(output_dir, "PCI_comparison_Energy_greenplexity.csv")
        pci_compare.to_csv(save_path, index=False)
        print(f"Saved PCI comparison to {save_path}")
        correlation = pci_compare[['pci_computed', 'pci_greenplexity']].corr().iloc[0, 1]
        print(f"PCI correlation (Energy vs Atlas): {correlation:.4f}")

    pci_compare['rank_computed'] = pci_compare['pci_computed'].rank(ascending=False, method='dense')
    pci_compare['rank_greenplexity'] = pci_compare['pci_greenplexity'].rank(ascending=False, method='dense')
    pci_compare['rank_diff'] = pci_compare['rank_computed'] - pci_compare['rank_greenplexity']

    # Sort by biggest mismatch
    rank_mismatch = pci_compare.sort_values(by='rank_diff', key=abs, ascending=False).head(10)
    print("Top 10 PCI rank mismatches:")
    print(rank_mismatch[['hs_product_code','pci_computed','pci_greenplexity','rank_computed','rank_greenplexity','rank_diff']])

def ECI_comparison(cdata, year, supplementary, eci_greenplexity, save_folder):
    eci_computed = cdata[['country_iso3', 'eci']].copy()
    eci_computed.rename(columns={'eci': 'eci_computed'}, inplace=True)
    
    eci_computed = eci_computed.drop_duplicates()

    eci_compare = pd.merge(eci_computed, eci_greenplexity, on='country_iso3', how='inner')
    
    eci_compare['rank_computed'] = eci_compare['eci_computed'].rank(ascending=False, method='dense')
    eci_compare['rank_greenplexity'] = eci_compare['eci_greenplexity'].rank(ascending=False, method='dense')
    eci_compare['rank_diff'] = eci_compare['rank_computed'] - eci_compare['rank_greenplexity']
    rank_mismatch = eci_compare.sort_values(by='rank_diff', key=abs, ascending=False).head(10)
    
    if supplementary == 1:
        output_dir = f"{save_folder}/{year}/supplementary"
        os.makedirs(output_dir, exist_ok=True)
        save_path = os.path.join(output_dir, f"ECI_comparison_Energy_supplementary_greenplexity_{year}.csv")
        eci_compare.to_csv(save_path, index=False)
        print(f"Saved ECI comparison to {save_path}")
        correlation = eci_compare[['eci_computed', 'eci_greenplexity']].corr().iloc[0, 1]
        print(f"ECI correlation (Energy supplementary vs Greenplexity) in {year}: {correlation:.4f}")
    else:
        output_dir = f"{save_folder}/{year}/Energy"
        os.makedirs(output_dir, exist_ok=True)
        save_path = os.path.join(output_dir, f"ECI_comparison_Energy_greenplexity_{year}.csv")
        eci_compare.to_csv(save_path, index=False)
        print(f"Saved ECI comparison to {save_path}")
        correlation = eci_compare[['eci_computed', 'eci_greenplexity']].corr().iloc[0, 1]
        print(f"ECI correlation (Energy vs Greenplexity) in {year}: {correlation:.4f}")

    if supplementary ==1:
        print(f"Top 10 ECI rank mismatches  in {year} (Energy supplementary vs Greenplexity):")
    else:
        print(f"Top 10 ECI rank mismatches  in {year} (Energy vs Greenplexity):")

    print(rank_mismatch[['country_iso3','eci_computed','eci_greenplexity','rank_computed','rank_greenplexity','rank_diff']])