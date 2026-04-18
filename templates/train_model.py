import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import pickle

data = pd.read_csv("dataset.csv")

# IMPORTANT: sirf numeric columns
X = data.select_dtypes(include=['int64','float64']).drop('label', axis=1)
y = data['label']

X = X.fillna(0)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# IMPORTANT change
model = RandomForestClassifier(n_estimators=200)

model.fit(X_train, y_train)

pickle.dump(model, open("model.pkl", "wb"))

print("Model trained properly")