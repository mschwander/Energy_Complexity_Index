import pandas as pd

population_data = pd.read_csv("01_Data/WPP2024_Demographic_Indicators_Medium.csv")

population_2023 = population_data[population_data["Time"] == 2023]

# Select relevant columns and rename
population_2023 = population_2023[["ISO3_code", "TPopulation1July"]].rename(
    columns={"ISO3_code": "country_iso3", "TPopulation1July": "population"}
)

#take out the ones that don't have iso3 codes
population_2023 = population_2023.dropna(subset=["country_iso3"])

population_2023["population"] = population_2023["population"] * 1000

#print(population_2023.head())

# Save to CSV
population_2023.to_csv("01_Data/population_2023.csv", index=False)
print("Saved population data for 2023 to '01_Data/population_2023.csv'")