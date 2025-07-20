import pandas as pd
import numpy as np

df = pd.read_csv('Zillow_Renter_Zip_Code.csv')

zip_codes_boston = [2151, 2128, 2129, 2163, 2113, 2114, 2134, 2203, 2109, 2108, 2110, 2116, 2111, 2199, 2135, 2215, 
                    2210, 2467, 2115, 2118, 2127, 2120, 2119, 2125, 2130, 2121, 2122, 2124, 2131, 2132, 2126, 2136]
df_boston = df[df["RegionName"].astype(int).isin(zip_codes_boston)]

df_boston = df_boston.drop(columns=["RegionID", "SizeRank", "State"])

# Calculate average rent in 2024 (example)
df_boston["avg_rent_2024"] = df_boston[[
    "2024-01-31", "2024-02-29", "2024-03-31", "2024-04-30", "2024-05-31", "2024-06-30",
    "2024-07-31", "2024-08-31", "2024-09-30", "2024-10-31", "2024-11-30", "2024-12-31"
]].mean(axis=1).round(2)

# View results
print(df_boston[["City", "StateName", "RegionName", "avg_rent_2024"]].reset_index(drop=True))
