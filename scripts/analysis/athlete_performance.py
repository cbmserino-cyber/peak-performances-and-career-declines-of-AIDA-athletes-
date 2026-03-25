import pandas as pd
import numpy as np

df = pd.read_csv("/home/bernard/Documents/class3/aida ranking project/aida_rankings_by_years.csv")
df.replace('-', 0, inplace=True)  # replace '-' with 0

# ensure string in col convert to number, replace invalids with NaN
df["Rank"] = pd.to_numeric(df["Rank"], errors="coerce")
for col in ["CWT", "CWTB", "CNF", "FIM"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df.fillna(0, inplace=True)  # replace NaN with 0
df.dropna(how='all', inplace=True) 

# Sort dataset
df = df.sort_values(by=["Athlete", "Year"])

# find first, last, and peak competition year for each athlete
peak_year = df.loc[df.groupby("Athlete")["Total Points"].idxmax(), ["Athlete", "Year"]].rename(columns={"Year": "Best_Year"})
first_year = df.loc[df.groupby("Athlete")["Year"].idxmin(), ["Athlete", "Year"]].rename(columns={"Year": "First_Year"})
last_year = df.loc[df.groupby("Athlete")["Year"].idxmax(), ["Athlete", "Year"]].rename(columns={"Year": "Last_Year"})
df = df.merge(first_year, on="Athlete", how="left")
df = df.merge(last_year, on="Athlete", how="left")
df = df.merge(peak_year, on="Athlete", how="left")

# feature engineering
df["Years_Competing"] = df["Year"] - df["First_Year"]
df["Performance_Growth_Prev_Year"] = df.groupby("Athlete")["Total Points"].diff().fillna(0)
df["Ranking_Variability_Prev_Year"] = (
    df.groupby("Athlete")["Rank"]
    .rolling(window=2, min_periods=1)
    .std(ddof=0)
    .reset_index(level=0, drop=True)  # Reset index to match df
    .shift(1)
    .fillna(0)
)
df["Years_Since_Last_Best"] = df["Year"] - df["Best_Year"]
df["Years_Until_Peak"] = df["Best_Year"] - df["Year"]

# binning selected features
for col in ["CWT", "CWTB", "CNF", "FIM"]:
    bins = [0, 30, 60, 90, np.inf]  # discipline score range
    labels = ["Low", "Moderate", "High", "Elite"]
    df[f"{col}"] = pd.cut(df[col], bins=bins, labels=labels)


# one-hot encoding: discipline
df = pd.get_dummies(df, columns=["CWT", "CWTB", "CNF", "FIM"], drop_first=True)

# --------------------------------------------------
# identify an athlete's last 3 years performance
# --------------------------------------------------

athlete_name = "Marion John Sumalinog (Philippines)"  # athlete name
athlete_data = df[df["Athlete"] == athlete_name].sort_values(by="Year", ascending=False)

athlete_last_3_years = athlete_data.head(3) # select last n years

# ensure competition disciplines exist in the dataframe
disciplines = ["CWT", "CWTB", "CNF", "FIM"]
existing_disciplines = [col for col in disciplines if col in df.columns]

# select features
athlete_last_3_years = athlete_last_3_years[
    ["Years_Competing", "Performance_Growth_Prev_Year", "Ranking_Variability_Prev_Year", "Years_Since_Last_Best"]
    + existing_disciplines
]

# save
athlete_last_3_years.to_csv("/home/bernard/Documents/class3/aida ranking project/athlete_last_3_years.csv", index=False)

# convert to array for LSTM input
new_athlete_data = athlete_last_3_years.to_numpy()

print(new_athlete_data)
