# -*- coding: utf-8 -*-
"""Credit_scoring.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Y2xLmHK32I81ie1y3fzgTr_KMLuaS_l9
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import matplotlib.pyplot as plt
import seaborn as sns
from imblearn.over_sampling import SMOTE

column_names = [
    'Status_Checking_Account', 'Duration', 'Credit_History', 'Purpose', 'Credit_Amount',
    'Savings_Account_Bonds', 'Employment_Since', 'Installment_Rate', 'Personal_Status_Sex',
    'Other_Debtors', 'Residence_Since', 'Property', 'Age', 'Other_Installment_Plans',
    'Housing', 'Number_Credits', 'Job', 'People_Liable', 'Telephone', 'Foreign_Worker',
    'Creditability'  # Target variable (1 = good, 2 = bad)
]

df=pd.read_csv("/content/german.data", delim_whitespace=True, header=None, names=column_names)

print(df.shape)

df.head()

label_enc = LabelEncoder()
for col in df.columns:
    if df[col].dtype == 'object':
        df[col] = label_enc.fit_transform(df[col])

df.head()

X = df.drop('Creditability', axis=1)
y = df['Creditability']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 6. Apply SMOTE on training data
sm = SMOTE(random_state=42)
X_resampled, y_resampled = sm.fit_resample(X_train, y_train)

model = RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42)
model.fit(X_resampled, y_resampled)

y_pred = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nConfusion Matrix:\n", confusion_matrix(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))

# 9. Feature Importance Plot
importances = model.feature_importances_
features = X.columns
indices = np.argsort(importances)[::-1]
for f, i in zip(features, importances):
    print(f"{f}: {i:.4f}")

new_customer = np.array([[2, 24, 1, 3, 1500, 4, 3, 4, 2, 0, 3, 2, 35, 0, 1, 1, 2, 1, 1, 1]])
prediction = model.predict(new_customer)
if prediction[0] == 1:
    print("✅ Credit Approved (Good Customer)")
else:
    print("❌ Credit Rejected (Bad Customer)")

new_customer= np.array([[0,4,0,4,200,0,0,1,3,1,1,0,18,2,0,1,3,2,0,0]])
prediction = model.predict(new_customer)
print(prediction)
if prediction[0] == 1:
    print("✅ Credit Approved (Good Customer)")
else:
    print("❌ Credit Rejected (Bad Customer)")

import pickle
with open("credit_scoring_model.pkl", "wb") as f:
    pickle.dump(model, f)
with open("credit_model_columns.pkl", "wb") as f:
    pickle.dump(X.columns.tolist(), f)