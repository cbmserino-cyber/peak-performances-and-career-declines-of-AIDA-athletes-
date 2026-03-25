import pandas as pd
import matplotlib.pyplot as plt
import os

my_path = os.path.abspath("/home/bernard/Documents/class3/aida ranking project")  # gets absolute path

# ---------------------------------------------
# Find peak year and decline performance
# ---------------------------------------------

df = pd.read_csv("/home/bernard/Documents/class3/aida ranking project/aida_rankings_by_years.csv")
df.replace('-', 0, inplace=True)
list(df.columns.values)

df["Year"] = df["Year"].astype(int)
df["Total Points"] = df["Total Points"].astype(float)

df = df.sort_values(by=["Athlete", "Year"]) # sort data by athlete and year

'''
# year when each athlete had their highest total points
peak_years = df.loc[df.groupby("Athlete")["Total Points"].idxmax(), ["Athlete", "Year", "Total Points"]] # idxmax
print(peak_years.head())

df = df.merge(peak_years, on="Athlete", suffixes=("", "_Peak")) # merge peak year data into the main dataframe

# flag if an athlete's points decline after their peak year
df["Declining"] = df["Year"] > df["Year_Peak"]
df["Point Drop"] = df["Total Points_Peak"] - df["Total Points"]

# filter rows where the athlete is past their peak
declining_df = df[df["Declining"]].sort_values(by=["Athlete", "Year"])

print(declining_df.head())


def plot_athlete_performance(athlete_name):
    athlete_data = df[df["Athlete"] == athlete_name]

    plt.figure(figsize=(8, 5))
    plt.plot(athlete_data["Year"], athlete_data["Total Points"], marker="o", linestyle="-", label="Total Points")

    peak_year = athlete_data["Year_Peak"].iloc[0]
    peak_points = athlete_data["Total Points_Peak"].iloc[0]

    plt.axvline(x=peak_year, color='r', linestyle='--', label="Peak Year")
    plt.scatter(peak_year, peak_points, color='red', s=100, label=f"Peak: {peak_points}")

    plt.xlabel("Year")
    plt.ylabel("Total Points")
    plt.title(f"Performance Trend: {athlete_name}")
    plt.legend()
    plt.grid(True)
    plt.show()

# plot an athlete's performance : Name

plot_athlete_performance("Alexey Molchanov (International)")

df["Rolling_Avg"] = df.groupby("Athlete")["Total Points"].transform(lambda x: x.rolling(2, min_periods=1).mean())

# Plot with smoothed trend
def plot_moving_avg(athlete_name):
    athlete_data = df[df["Athlete"] == athlete_name]

    plt.figure(figsize=(8, 5))
    plt.plot(athlete_data["Year"], athlete_data["Rolling_Avg"], marker="o", linestyle="-", label="Rolling Avg (3yr)")

    plt.xlabel("Year")
    plt.ylabel("Total Points (3yr Avg)")
    plt.title(f"Smoothed Performance Trend: {athlete_name}")
    plt.legend()
    plt.grid(True)
    plt.show()

plot_moving_avg("Alexey Molchanov (International)")

exit()

'''

# ----------------------------------------------------------
# How long it takes to reach peak and decline in performance
# ----------------------------------------------------------

df["Year"] = df["Year"].astype(int)
df["Total Points"] = df["Total Points"].astype(float)

df = df.sort_values(by=["Athlete", "Year"]) # sort data by athlete and year

# first recorded year for each athlete
first_years = df.groupby("Athlete")["Year"].min().reset_index()
first_years.rename(columns={"Year": "First_Year"}, inplace=True)

# peak year for each athlete
peak_years = df.loc[df.groupby("Athlete")["Total Points"].idxmax(), ["Athlete", "Year"]]
peak_years.rename(columns={"Year": "Peak_Year"}, inplace=True)

df = df.merge(first_years, on="Athlete", how="left")
df = df.merge(peak_years, on="Athlete", how="left")

# "Years Until Peak"
df["Years_Until_Peak"] = df["Peak_Year"] - df["First_Year"]

# years after peak where performance declines
df["Declining"] = df["Year"] > df["Peak_Year"]
df["Point Drop"] = df["Total Points"] - df.groupby("Athlete")["Total Points"].shift(1)

# first year of decline
decline_years = df[df["Declining"] & (df["Point Drop"] < 0)].groupby("Athlete")["Year"].min().reset_index()
decline_years.rename(columns={"Year": "Decline_Year"}, inplace=True)

df = df.merge(decline_years, on="Athlete", how="left")

# "Years Before Decline"
df["Years_Before_Decline"] = df["Decline_Year"] - df["Peak_Year"]

# averages
avg_years_until_peak = df["Years_Until_Peak"].mean()
avg_years_before_decline = df["Years_Before_Decline"].mean()

# median
median_years_until_peak = df["Years_Until_Peak"].median()
median_years_before_decline = df["Years_Before_Decline"].median()

# mean by career length
df["Career_Length"] = df["Decline_Year"] - df["First_Year"]
career_length_summary = df.groupby(pd.cut(df["Career_Length"], bins=[0, 5, 10, 15, 20], labels=["0-5", "6-10", "11-15", "16+"]))[
    ["Years_Until_Peak", "Years_Before_Decline"]
].mean()

print(f"Average years until peak: {avg_years_until_peak:.2f} years")
print(f"Average years before decline: {avg_years_before_decline:.2f} years")

print(f"Average years until peak: {median_years_until_peak:.2f} years")
print(f"Average years before decline: {median_years_before_decline:.2f} years")

print(career_length_summary)
