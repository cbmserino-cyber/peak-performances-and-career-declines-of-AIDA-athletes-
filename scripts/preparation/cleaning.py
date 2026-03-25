import pandas as pd
import os

# base paths
base_path = os.path.abspath("/home/bernard/Documents/class3/aida ranking project")

world_ranking_file = os.path.join(base_path, "aida_FIMrankings_by_years.csv")
df_cwt = pd.read_csv(world_ranking_file)

# extract country name from 'Name' column
df_cwt['Country'] = df_cwt['Athlete'].str.extract(r"\(([^()]*)\)$")
df_cwt['Country'] = df_cwt['Country'].str.replace(',', '', regex=True)
df_cwt['Athlete'] = df_cwt['Athlete'].str.replace(r"\s*\([^()]*\)$", "", regex=True)
print(df_cwt[['Athlete', 'Country']].head())

output_file = os.path.join(base_path, "fimranks.csv")
df_cwt.to_csv(output_file, index=False)
