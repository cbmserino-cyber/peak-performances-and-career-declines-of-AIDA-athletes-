# ------------------------------------
# RCF: Super-elite vs average athlete
# ------------------------------------
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

df = pd.read_csv("/home/bernard/Documents/class3/aida ranking project/aida_rankings_by_years.csv")

# features and target
X = df[['years_competing', 'avg_points_per_year', 'ranking_improvement_rate']]
y = df['super_elite']  # 1 = Super Elite, 0 = Not

# split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# train model
model = RandomForestClassifier()
model.fit(X_train, y_train)

# evaluate
y_pred = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))

