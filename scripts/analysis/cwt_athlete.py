## ----------------------------------------------------------------------
## Extract features last nth competition of athlete FIM
## ----------------------------------------------------------------------

import pandas as pd
import numpy as np

# Load dataset
df = pd.read_csv("/home/bernard/Documents/class3/aida ranking project/fimranks.csv")

# Replace '-' with 0
df.replace('-', 0, inplace=True)

# Ensure numeric columns are converted properly
numeric_cols = ["Rank", "Result", "Announced", "Points", "Penalties"]
df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")

# Fill NaN values with 0
df.fillna(0, inplace=True)
df.dropna(how='all', inplace=True)

# Sort data by Athlete and Year
df = df.sort_values(by=["Athlete", "Year"])

# Find first, last, and peak competition year for each athlete
peak_year = df.loc[df.groupby("Athlete")["Points"].idxmax(), ["Athlete", "Year"]].rename(columns={"Year": "Best_Year"})
first_year = df.loc[df.groupby("Athlete")["Year"].idxmin(), ["Athlete", "Year"]].rename(columns={"Year": "First_Year"})
last_year = df.loc[df.groupby("Athlete")["Year"].idxmax(), ["Athlete", "Year"]].rename(columns={"Year": "Last_Year"})

# Merge feature columns
df = df.merge(first_year, on="Athlete", how="left")
df = df.merge(last_year, on="Athlete", how="left")
df = df.merge(peak_year, on="Athlete", how="left")

# ~ for col in df.columns:
    # ~ print(col)

# Feature Engineering
df["Years_Competing"] = df["Year"] - df["First_Year"]
df["Performance_Growth_Prev_Year"] = df.groupby("Athlete")["Points"].diff().fillna(0)
df["Ranking_Variability_Prev_Year"] = (
    df.groupby("Athlete")["Rank"]
    .rolling(window=2, min_periods=1)
    .std(ddof=0)
    .reset_index(level=0, drop=True)
    .shift(1)
    .fillna(0)
)
df["Years_Since_Last_Best"] = df["Year"] - df["Best_Year"]
df["Years_Until_Peak"] = df["Best_Year"] - df["Year"]

# -----------------------------------------------
# Identify an athlete's last 3 years performance
# -----------------------------------------------
athlete_name = "Alexey Molchanov"  # Athlete name
athlete_data = df[df["Athlete"] == athlete_name].sort_values(by="Year", ascending=False)

athlete_last_3_years = athlete_data.head(6)  # Select last n years

# Select relevant features
selected_features = [
    "Years_Competing",
    "Performance_Growth_Prev_Year",
    "Ranking_Variability_Prev_Year",
    "Years_Since_Last_Best"
]
athlete_last_3_years = athlete_last_3_years[selected_features]

# Save to CSV
output_path = "/home/bernard/Documents/class3/aida ranking project/fim_last_3_years.csv"
athlete_last_3_years.to_csv(output_path, index=False)

# Convert to array for LSTM input
new_athlete_data = athlete_last_3_years.to_numpy()

print(new_athlete_data)

