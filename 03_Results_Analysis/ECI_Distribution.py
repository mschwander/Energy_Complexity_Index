import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

yellow = 0

if yellow:
    eci_country = pd.read_csv("04_Results/eci_country_results_Energy_yellow.csv")
    output_prefix = "04_Results/ECI_Energy_yellow"
else:
    eci_country = pd.read_csv("04_Results/eci_country_results_Energy.csv")
    #eci_country = pd.read_csv("04_Results/eci_country_results_BACI.csv")
    output_prefix = "04_Results/ECI_Energy"

#print(eci_country.head())

eci_2023 = eci_country[eci_country["t"] == 2023].dropna(subset=["eci"])

# --- Scatter plot ---
plt.figure(figsize=(12, 6))
plt.scatter(eci_2023["country_name"], eci_2023["eci"], alpha=0.7)
plt.xticks(rotation=75, ha="right")
plt.title("Scatter Plot of ECI by Country (2023)")
plt.ylabel("Economic Complexity Index (ECI)")
plt.xlabel("Country")
plt.tight_layout()
plt.savefig(f"{output_prefix}_Scatter.png", dpi=300)
plt.close()

# --- Histogram ---
plt.figure(figsize=(8, 6))
plt.hist(eci_2023["eci"], bins=20, color="skyblue", edgecolor="black")
plt.title("Histogram of ECI Values (2023)")
plt.xlabel("Economic Complexity Index (ECI)")
plt.ylabel("Frequency")
plt.tight_layout()
plt.savefig(f"{output_prefix}_Histogram.png", dpi=300)
plt.close()

# --- Density plot ---
plt.figure(figsize=(8, 6))
sns.kdeplot(eci_2023["eci"], fill=True, color="purple", alpha=0.5)
plt.title("Density Plot of ECI Values (2023)")
plt.xlabel("Economic Complexity Index (ECI)")
plt.ylabel("Density")
plt.tight_layout()
plt.savefig(f"{output_prefix}_Density.png", dpi=300)
plt.close()

print(f"Saved scatter, histogram, and density plots with prefix {output_prefix}")

