import pandas as pd
import numpy as np
from tabulate import tabulate

# Load the three CSVs
df_age = pd.read_csv("../Data/raw/median_age.csv")
df_income = pd.read_csv("../Data/raw/median_income.csv")
df_renters = pd.read_csv("../Data/raw/tenure_b25003.csv")

# Check what columns are available in each file
print("Columns in median_age.csv:")
print(df_age.columns.tolist())
print("\nColumns in median_income.csv:")
print(df_income.columns.tolist())
print("\nColumns in tenure_b25003.csv:")
print(df_renters.columns.tolist())
print("\nFirst few rows of each file:")
print("median_age.csv:")
print(df_age.head(3))
print("\nmedian_income.csv:")
print(df_income.head(3))
print("\ntenure_b25003.csv:")
print(df_renters.head(3))
print("\n" + "="*80 + "\n")

# Extract & rename relevant columns with correct column names
# Based on ACS 2023 5-year data (2019-2023) metadata:
# B01002A001 = "Total:" median age (White alone population)
# B19013001 = "Median household income in the past 12 months (in 2023 inflation-adjusted dollars)"
# B25003001 = "Total:" occupied housing units
# B25003003 = "Renter occupied" housing units

df_age = df_age[["name", "B01002A001"]].rename(columns={
    "name": "ZIP", "B01002A001": "Median_Age"
})
df_income = df_income[["name", "B19013001"]].rename(columns={
    "name": "ZIP", "B19013001": "Median_Income"
})
df_renters = df_renters[["name", "B25003001", "B25003003"]].rename(columns={
    "name": "ZIP",
    "B25003001": "Total_Occupied",
    "B25003003": "Renter_Occupied"
})
df_renters["Percent_Renters"] = (df_renters["Renter_Occupied"] / df_renters["Total_Occupied"]) * 100

# Clean ZIP field to contain just the ZIP code - filter for actual ZIP codes only
# Filter age data to only include 5-digit ZIP codes and convert to 4-digit format
df_age = df_age[df_age["ZIP"].str.match(r'^\d{5}$', na=False)]
df_age["ZIP"] = df_age["ZIP"].str[1:]  # Remove leading 0 to match 4-digit format

# Income and renters data already have 4-digit ZIP codes, just ensure they're strings
df_income["ZIP"] = df_income["ZIP"].astype(str)
df_renters["ZIP"] = df_renters["ZIP"].astype(str)

# Debug: Check what ZIP codes we have after cleaning
print("Sample ZIP codes from each dataset after cleaning:")
print("Age data ZIPs:", df_age["ZIP"].head().tolist())
print("Income data ZIPs:", df_income["ZIP"].head().tolist())
print("Renters data ZIPs:", df_renters["ZIP"].head().tolist())

# Merge on ZIP
df_demo = df_age.merge(df_income, on="ZIP").merge(df_renters[["ZIP", "Percent_Renters"]], on="ZIP")

print(f"After merging: {len(df_demo)} rows in combined demographic data")
print("Sample merged data:")
print(df_demo.head())

# Helper functions for formatting
def format_currency(value):
    if pd.notna(value):
        return f"${value:,.0f}"
    else:
        return "N/A"

def format_rent(value):
    if pd.notna(value):
        return f"${value:,.2f}"
    else:
        return "N/A"

def format_age(value):
    if pd.notna(value):
        return f"{value:.1f} years"
    else:
        return "N/A"

def format_percentage(value):
    if pd.notna(value):
        return f"{value:.1f}%"
    else:
        return "N/A"

# Print demographic data summary
print("Demographic Data Summary:")
print("Data Source: ACS 2023 5-year estimates (2019-2023)")
print(f"Total ZIP codes with demographic data: {len(df_demo)}")
print("\nFirst few rows of demographic data:")
# Format the demographic data for display
df_demo_display = df_demo.copy()
# Format income with dollar signs and commas
df_demo_display["Median_Income"] = df_demo_display["Median_Income"].map(format_currency)
# Format age with years label
df_demo_display["Median_Age"] = df_demo_display["Median_Age"].map(format_age)
# Format percentage with % symbol
df_demo_display["Percent_Renters"] = df_demo_display["Percent_Renters"].map(format_percentage)
print(tabulate(df_demo_display.head(10), headers='keys', tablefmt='psql'))
print("\n" + "="*80 + "\n")

df = pd.read_csv('../Data/raw/Zillow_Renter_Zip_Code.csv')

# Define Boston zip codes
# These zip codes are used to filter the DataFrame for Boston rental data
# 2199 is used in Back Bay, and parts of 2210, 2215
# data sheet does not start zips with 0, so we use integers
zip_codes_boston = [2108, 2109, 2110, 2111, 2113, 2114, 2115, 2116,
2118, 2119, 2120, 2121, 2122, 2124, 2125, 2126,
2127, 2128, 2129, 2130, 2131, 2132, 2134, 2135,
2136, 2199, 2210, 2215]
df_boston = df[df["RegionName"].astype(int).isin(zip_codes_boston)]

df_boston = df_boston.drop(columns=["RegionID", "SizeRank", "State"])

# Calculate average rent in 2024 
df_boston["avg_rent_2024"] = df_boston[[
    "2024-01-31", "2024-02-29", "2024-03-31", "2024-04-30", "2024-05-31", "2024-06-30",
    "2024-07-31", "2024-08-31", "2024-09-30", "2024-10-31", "2024-11-30", "2024-12-31"
]].mean(axis=1).round(2)

# Separate data with and without NaN values
df_with_data = df_boston[df_boston["avg_rent_2024"].notna()]
df_with_nan = df_boston[df_boston["avg_rent_2024"].isna()]

# View results with data AKA useful data
print("Boston Rental Data - With Average Rent 2024:")
print("Data Source: Zillow Rental Data (January - December 2024)")
df_with_data_display = df_with_data[["City", "StateName", "RegionName", "avg_rent_2024"]].copy().reset_index(drop=True)
# Format rent with dollar signs and commas
df_with_data_display["avg_rent_2024"] = df_with_data_display["avg_rent_2024"].map(format_rent)
print(tabulate(df_with_data_display, headers='keys', tablefmt='psql'))

print("\n" + "="*60 + "\n")

# View results with NaN values AKA no useful data
print("Boston Rental Data - Missing Average Rent 2024:")
df_with_nan_display = df_with_nan[["City", "StateName", "RegionName", "avg_rent_2024"]].copy().reset_index(drop=True)
df_with_nan_display["avg_rent_2024"] = "No Data"
print(tabulate(df_with_nan_display, headers='keys', tablefmt='psql'))

print("\n" + "="*80 + "\n")

# Check which Boston zip codes have demographic data
boston_zips_str = [str(zip_code) for zip_code in zip_codes_boston]  # Convert to strings
demo_boston = df_demo[df_demo["ZIP"].isin(boston_zips_str)]

print("Boston ZIP Codes with Demographic Data:")
print("Demographic Data: ACS 2023 5-year estimates (2019-2023)")
print(f"Total Boston ZIP codes with demographic data: {len(demo_boston)}")
if len(demo_boston) > 0:
    # Format the Boston demographic data for display
    demo_boston_display = demo_boston.copy()
    demo_boston_display["Median_Income"] = demo_boston_display["Median_Income"].map(format_currency)
    demo_boston_display["Median_Age"] = demo_boston_display["Median_Age"].map(format_age)
    demo_boston_display["Percent_Renters"] = demo_boston_display["Percent_Renters"].map(format_percentage)
    print(tabulate(demo_boston_display, headers='keys', tablefmt='psql'))
    
    print("\n" + "="*80)
    print("DATA SUMMARY & TIME FRAMES")
    print("="*80)
    print("📊 RENTAL DATA:")
    print("   • Source: Zillow Rental Listings")
    print("   • Time Period: January 2024 - December 2024")
    print("   • Coverage: 25 Boston ZIP codes with data, 2 missing")
    print()
    print("👥 DEMOGRAPHIC DATA:")
    print("   • Source: U.S. Census Bureau ACS 2023 5-year estimates")
    print("   • Time Period: 2019-2023 (5-year average)")
    print("   • Coverage: 28 Boston ZIP codes")
    print()
    print("⚠️  NOTE: Demographic data represents 5-year averages (2019-2023)")
    print("   while rental data is from 2024 only. This timing difference")
    print("   should be considered when interpreting correlations.")
    print("="*80)
else:
    print("No demographic data found for Boston ZIP codes.")
    print("Available ZIP codes in demographic data:")
    print(df_demo["ZIP"].head(10).tolist())
