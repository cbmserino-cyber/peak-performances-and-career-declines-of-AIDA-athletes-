## ---------------------------------------------------------------------
## Predict when a new athlete will peak using LSTM
## ---------------------------------------------------------------------

import os
import pandas as pd
import numpy as np
import random
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Bidirectional
from tensorflow.keras.callbacks import ReduceLROnPlateau, EarlyStopping
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from tensorflow.keras.optimizers import SGD

# set random seed 
SEED = 42
np.random.seed(SEED)
random.seed(SEED)
tf.random.set_seed(SEED)

# for deterministic operations
os.environ["TF_DETERMINISTIC_OPS"] = "1"
os.environ["TF_CUDNN_DETERMINISTIC"] = "1"

df = pd.read_csv("/home/bernard/Documents/class3/aida ranking project/aida_depthrankings_by_years.csv")	# main dataset 

df.replace('-', 0, inplace=True)	# replace '-' with 0

# ensure string in col convert to number, replace invalids with NaN
df["Rank"] = pd.to_numeric(df["Rank"], errors="coerce")
for col in ["CWT", "CWTB", "CNF", "FIM"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df.fillna(0, inplace=True)	# replace NaN with 0
df.dropna(how='all', inplace=True) 

# ~ df = df.sort_values(by=["Year", "Rank"]).groupby("Year").head(10)

df = df.sort_values(by=["Athlete", "Year"]) # sort
df = df.rename(columns={"Total Points": "Total_Points_Current_Year"}) # rename col

# year when each athlete first and recent (last) competed
peak_year = df.loc[df.groupby("Athlete")["Total_Points_Current_Year"].idxmax(), ["Athlete", "Year", "Total_Points_Current_Year"]].rename(columns={"Year": "Best_Year", "Total_Points_Current_Year": "Peak_Total_Points"})
first_year = df.loc[df.groupby("Athlete")["Year"].idxmin(), ["Athlete", "Year"]].rename(columns={"Year": "First_Year"})
last_year = df.loc[df.groupby("Athlete")["Year"].idxmax(), ["Athlete", "Year"]].rename(columns={"Year": "Last_Year"})

# merge into original dataframe
df = df.merge(first_year, on="Athlete", how="left")
df = df.merge(last_year, on="Athlete", how="left")
df = df.merge(peak_year, on="Athlete", how="left")

# select features
df = df.sort_values(by=["Athlete", "Year"])
df["Years_Competing"] = df["Year"] - df.groupby("Athlete")["First_Year"].transform("min")
df["Performance_Growth_Prev_Year"] = (
    df.groupby("Athlete")["Total_Points_Current_Year"]
    .diff()  # difference between consecutive years
    .shift(1)  # shift to align with the previous year
    .fillna(0)
)
df["Ranking_Variability_Prev_Year"] = (
    df.groupby("Athlete")["Rank"]
    .rolling(window=2, min_periods=1)
    .std(ddof=0)
    .reset_index(level=0, drop=True)  # reset index to match df
    .shift(1)
    .fillna(0)
)
df["Years_Since_Last_Best"] = df["Year"] - df.groupby("Athlete")["Best_Year"].transform("max")
df["Years_Until_Peak"] = df["Best_Year"] - df["Year"]

# ~ for col in df.columns:
    # ~ print(col)

# drop non-numeric columns
df = df.drop(columns=["Athlete","First_Year", "Best_Year", "Year"])
    
# binning selected features
for col in ["CWT", "CWTB", "CNF", "FIM"]:
    bins = [0, 30, 60, 90, np.inf]  # discipline score range
    labels = ["Low", "Moderate", "High", "Elite"]
    df[f"{col}"] = pd.cut(df[col], bins=bins, labels=labels)


# one-hot encoding: discipline
df = pd.get_dummies(df, columns=["CWT", "CWTB", "CNF", "FIM"], drop_first=True)

# ~ import csv
# ~ df.to_csv("/home/bernard/Documents/class3/aida ranking project/aida1.csv", index=False)
# ~ exit()

# scale features
scaler = StandardScaler()
scaled_data = scaler.fit_transform(df.drop(columns=["Years_Until_Peak"]))
scaled_target = df["Years_Until_Peak"].values


# reshape for LSTM (samples, timesteps, features)
def create_sequences(data, target, seq_length):
    X, y = [], []
    for i in range(len(data) - seq_length):
        X.append(data[i:i+seq_length])
        y.append(target[i+seq_length])
    return np.array(X), np.array(y)

SEQ_LENGTH = 3 # number of years in sequence
X, y = create_sequences(scaled_data, scaled_target, SEQ_LENGTH)

# train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=SEED)

print(f"Train Shape: {X_train.shape}, Test Shape: {X_test.shape}")

# ----------------------------------------------------------------------
# define LSTM model
#-----------------------------------------------------------------------
# ~ model = Sequential([
    # ~ LSTM(64, activation="relu", input_shape=(SEQ_LENGTH, X_train.shape[2])),
    # ~ Dropout(0.3),
    # ~ Dense(16, activation="relu"),
    # ~ Dense(1)  # output: years until peak
# ~ ])


model = Sequential([
    Bidirectional(LSTM(100, return_sequences=True, activation="relu"), input_shape=(SEQ_LENGTH, X_train.shape[2])),
    Dropout(0.3),
    LSTM(64, return_sequences=True, activation="relu"),
    Dropout(0.3),
    LSTM(40, activation="relu"),
    Dense(20, activation="relu"),
    Dense(1)  # output: years until peak
])

# compile model
# ~ model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.01), loss="mse", metrics=["mae"])
# ~ model.compile(optimizer=SGD(learning_rate=0.0001, momentum=0.9), loss="mse", metrics=["mae"])

# callbacks for optimization
callbacks = [
    ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=5, verbose=1),
    EarlyStopping(monitor="val_loss", patience=10, restore_best_weights=True, verbose=1)
]

# compile model with gradient clipping
optimizer = tf.keras.optimizers.Adam(learning_rate=0.1, clipvalue=1.0) # clipping prevents exploding gradients during backpropagation by capping their size 'clipnorm' or 'clipvalue'
model.compile(optimizer=optimizer, loss="mse", metrics=["mae"])
# ~ model.compile(optimizer=SGD(learning_rate=0.01, momentum=0.9), loss="mse", metrics=["mae"])

# train model
history = model.fit(X_train, y_train, epochs=100, batch_size=16, validation_data=(X_test, y_test), callbacks=callbacks, verbose=1)

# evaluate on test set
test_loss, test_mae = model.evaluate(X_test, y_test)
print(f"Test Mean Absolute Error: {test_mae:.2f} years")	

# ----------------------------------------------------------------------
# Predictions for new athletes
# ----------------------------------------------------------------------

template_df = pd.DataFrame(columns=df.columns)

athlete_last_3_years = pd.read_csv("/home/bernard/Documents/class3/aida ranking project/athlete_last_3_years.csv") # dataset
new_athlete_data = athlete_last_3_years.reindex(columns=df.columns, fill_value=0) # align with the main dataset
new_athlete_data = new_athlete_data.drop(columns=["Years_Until_Peak"], errors="ignore") # drop target variable "Years_Until_Peak"

# scale input
new_athlete_data_scaled = scaler.transform(new_athlete_data)

# reshape for LSTM
new_athlete_data_scaled = np.expand_dims(new_athlete_data_scaled, axis=0)  # shape: (1, SEQ_LENGTH, features)

# predict years until peak
predicted_years_until_peak = model.predict(new_athlete_data_scaled)
print(f"Predicted Years Until Peak: {predicted_years_until_peak[0][0]:.2f} years")
