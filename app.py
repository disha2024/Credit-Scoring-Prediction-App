import streamlit as st
import numpy as np
import pickle
import pandas as pd

# Load model and columns
with open("credit_scoring_model.pkl", "rb") as f:
    model = pickle.load(f)

with open("credit_model_columns.pkl", "rb") as f:
    column_names = pickle.load(f)

st.set_page_config(page_title="Credit Scoring", layout="centered")
st.title("💳 Credit Scoring Prediction")
st.markdown("Fill the customer details below to predict creditworthiness.")

with st.expander("ℹ️ Feature Descriptions"):
    st.markdown("""
    - **Status_Checking_Account**: 0 = none, 1 = <0 DM, 2 = 0–200 DM, 3 = ≥200 DM  
    - **Duration**: Loan duration in months  
    - **Credit_History**: 0 = critical, 1 = paid, 2 = delay, etc.  
    - **Purpose**: 0 = car, 1 = furniture, ..., 9 = business  
    - **Savings_Account_Bonds**: 0 = <100 DM, 1 = 100–500, 2 = 500–1000, 3 = ≥1000  
    - **Employment_Since**: 0 = unemployed, 1 = <1yr, ..., 4 = ≥7yrs  
    - **Installment_Rate**: Installment as % of income (1 to 4)  
    - **Personal_Status_Sex**: 0 = male-div, 1 = female-div, 2 = male-single, 3 = male-married, 4 = female-single  
    - **Other_Debtors**: 0 = none, 1 = guarantor, 2 = co-applicant  
    - **Property**: 0 = real estate, 1 = insurance, 2 = car, 3 = none  
    - **Housing**: 0 = rent, 1 = own, 2 = free  
    - **Other_Installment_Plans**: 0 = bank, 1 = store, 2 = none  
    - **Job**: 0 = unemployed, 1 = unskilled, 2 = skilled, 3 = high skill  
    - **People_Liable**: 1 = only applicant, 2 = applicant and others  
    """)

# Input fields with help descriptions
status = st.selectbox("Status of Checking Account", [0,1,2,3], help="0 = none, 1 = <0 DM, 2 = 0–200 DM, 3 = ≥200 DM")
duration = st.slider("Duration of Credit (Months)", 4, 72, 24, help="Loan duration")
credit_history = st.selectbox("Credit History", [0,1,2,3,4], help="0 = critical, 1 = paid, 2 = delay, etc.")
purpose = st.selectbox("Purpose of Loan", list(range(10)), help="0 = car, 1 = furniture, 2 = radio/TV, ..., 9 = business")
credit_amount = st.number_input("Credit Amount", 100, 50000, 1500, help="Requested loan amount in Deutsche Mark")
savings = st.selectbox("Savings Account Balance", [0,1,2,3,4], help="0 = <100 DM, 1 = 100–500, etc.")
employment = st.selectbox("Employment Since (Years)", [0,1,2,3,4], help="0 = unemployed, ..., 4 = ≥7yrs")
installment_rate = st.slider("Installment Rate (% of income)", 1, 4, 2)
personal_status = st.selectbox("Personal Status / Sex", [0,1,2,3,4], help="0 = male-div, 1 = female-div, 2 = male-single, etc.")
other_debtors = st.selectbox("Other Debtors/Guarantors", [0,1,2], help="0 = none, 1 = guarantor, 2 = co-applicant")
residence = st.slider("Years at Residence", 1, 4, 2)
property_type = st.selectbox("Property Type", [0,1,2,3], help="0 = real estate, 1 = insurance, etc.")
age = st.slider("Age", 18, 75, 35)
installment_plans = st.selectbox("Other Installment Plans", [0,1,2], help="0 = bank, 1 = store, 2 = none")
housing = st.selectbox("Housing Type", [0,1,2], help="0 = rent, 1 = own, 2 = free")
num_credits = st.slider("Number of Existing Credits", 1, 4, 1)
job = st.selectbox("Job Type", [0,1,2,3], help="0 = unemployed, ..., 3 = highly skilled")
people_liable = st.selectbox("Number of Liable People", [1,2], help="1 = only applicant, 2 = applicant + others")
telephone = st.selectbox("Telephone Available", [0,1], help="0 = no, 1 = yes")
foreign_worker = st.selectbox("Is Foreign Worker?", [0,1], help="0 = no, 1 = yes")

# Create input array
input_data = np.array([[
    status, duration, credit_history, purpose, credit_amount,
    savings, employment, installment_rate, personal_status, other_debtors,
    residence, property_type, age, installment_plans, housing, num_credits,
    job, people_liable, telephone, foreign_worker
]])

input_df = pd.DataFrame(input_data, columns=column_names)

# Prediction
if st.button("Predict Creditworthiness"):
    prediction = model.predict(input_df)
    if prediction[0] == 1:
        st.success("✅ Credit Approved (Good Customer)")
    else:
        st.error("❌ Credit Rejected (Bad Customer)")
