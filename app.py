import streamlit as st
st.set_page_config(page_title="Credit Scoring App", layout="centered")

import numpy as np
import pandas as pd
import pickle
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import hashlib
import os
import csv

# ------------------ User Authentication ------------------ #
USER_FILE = "users.csv"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if not os.path.exists(USER_FILE):
        return {}
    with open(USER_FILE, mode="r", newline='') as f:
        reader = csv.reader(f)
        next(reader, None)  # skip header
        return {rows[0]: rows[1] for rows in reader}

def save_user(email, hashed_pw):
    file_exists = os.path.isfile(USER_FILE)
    with open(USER_FILE, mode="a", newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["email", "hashed_password"])
        writer.writerow([email, hashed_pw])

# ------------------ Session State ------------------ #
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = ""

# ------------------ Login / Signup ------------------ #
if not st.session_state.logged_in:
    st.subheader("Login or Sign Up")

    tab1, tab2 = st.tabs(["Log In", "Sign Up"])

    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            users = load_users()
            if email in users and users[email] == hash_password(password):
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.success(f"Welcome, {email}!")
                st.rerun()
            else:
                st.error("❌ Invalid email or password.")
                st.info("🔐 New user? Please switch to the **Sign Up** tab above.")

    with tab2:
        new_email = st.text_input("New Email")
        new_password = st.text_input("New Password", type="password")
        if st.button("Sign Up"):
            users = load_users()
            if new_email in users:
                st.warning("User already exists.")
            else:
                save_user(new_email, hash_password(new_password))
                st.success("Account created! You can now log in.")

# ------------------ Main App ------------------ #
if st.session_state.logged_in:
    st.sidebar.success(f"Logged in as: {st.session_state.user_email}")

    # Load model
    with open("credit_scoring_model.pkl", "rb") as f:
        model = pickle.load(f)

    with open("credit_model_columns.pkl", "rb") as f:
        column_names = pickle.load(f)

    def generate_pdf_report(lender_name, credit_amount, duration, age, employment, housing,
                            installment_rate, savings, credit_history, result_text):
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        c.setFont("Helvetica-Bold", 18)
        c.setFillColor(colors.darkblue)
        c.drawString(40, 760, "Credit Scoring Report")
        c.line(40, 755, 570, 755)

        c.setFont("Helvetica", 12)
        y = 730
        line_gap = 20
        report_lines = [
            f"Lender Name         : {lender_name}",
            f"Credit Amount (DM)  : {credit_amount}",
            f"Duration (Months)   : {duration}",
            f"Age (Years)         : {age}",
            f"Employment (Encoded): {employment}",
            f"Housing Type        : {housing} (",
            f"Installment Rate    : {installment_rate}%",
            f"Savings Account     : {savings} ",
            f"Credit History      : {credit_history} ",
            "",
            f"Prediction Result   : {result_text}"
        ]
        for line in report_lines:
            c.drawString(40, y, line)
            y -= line_gap

        c.setFont("Helvetica-Oblique", 9)
        c.setFillColor(colors.grey)
        c.drawString(40, 50, "This report is system generated and used for credit scoring evaluation only.")
        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer

    st.title("Credit Scoring Prediction App")
    st.markdown("Provide customer details below to predict creditworthiness.")

    lender_name = st.text_input("Lender's Name (used in PDF)", value="Customer_1")

    status = st.selectbox("Status of Checking Account", [0, 1, 2, 3])
    duration = st.slider("Duration of Credit (Months)", 4, 72, 24)
    credit_history = st.selectbox("Credit History", [0, 1, 2, 3, 4])
    purpose = st.selectbox("Purpose of Loan", list(range(10)))
    credit_amount = st.number_input("Credit Amount (DM)", 100, 1000000, 1500)
    savings = st.selectbox("Savings Account", [0, 1, 2, 3, 4])
    employment = st.selectbox("Employment Since", [0, 1, 2, 3, 4])
    installment_rate = st.slider("Installment Rate (% of Income)", 1, 4, 2)
    personal_status = st.selectbox("Personal Status / Sex", [0, 1, 2, 3, 4])
    other_debtors = st.selectbox("Other Debtors/Guarantors", [0, 1, 2])
    residence = st.slider("Years at Residence", 1, 4, 2)
    property_type = st.selectbox("Property Type", [0, 1, 2, 3])
    age = st.slider("Age", 18, 75, 35)
    installment_plans = st.selectbox("Other Installment Plans", [0, 1, 2])
    housing = st.selectbox("Housing Type", [0, 1, 2])
    num_credits = st.slider("Number of Existing Credits", 1, 4, 1)
    job = st.selectbox("Job Type", [0, 1, 2, 3])
    people_liable = st.selectbox("Number of Liable People", [1, 2])
    telephone = st.selectbox("Telephone Available", [0, 1])
    foreign_worker = st.selectbox("Is Foreign Worker?", [0, 1])

    input_data = np.array([[
        status, duration, credit_history, purpose, credit_amount,
        savings, employment, installment_rate, personal_status, other_debtors,
        residence, property_type, age, installment_plans, housing, num_credits,
        job, people_liable, telephone, foreign_worker
    ]])
    input_df = pd.DataFrame(input_data, columns=column_names)

    if st.button("Predict Creditworthiness"):
        prediction = model.predict(input_df)
        if prediction[0] == 1:
            result_text = "Credit Approved (Good Customer)"
            st.success(result_text)
        else:
            result_text = "Credit Rejected (Bad Customer)"
            st.error(result_text)

        pdf = generate_pdf_report(
            lender_name, credit_amount, duration, age,
            employment, housing, installment_rate, savings, credit_history, result_text
        )

        st.download_button(
            label="Download Credit Report (PDF)",
            data=pdf,
            file_name=f"{lender_name}_credit_report.pdf",
            mime="application/pdf"
        )

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.subheader("Delete Account")
    if st.sidebar.checkbox("Yes, I want to delete my account"):
        if st.sidebar.button("Delete My Account"):
            users = load_users()
            updated_users = {email: pw for email, pw in users.items() if email != st.session_state.user_email}

            # Overwrite users.csv with updated users
            with open(USER_FILE, mode="w", newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["email", "hashed_password"])
                for email, pw in updated_users.items():
                    writer.writerow([email, pw])

            st.sidebar.success("Your account has been deleted.")
            st.session_state.logged_in = False
            st.session_state.user_email = ""
            st.rerun()
