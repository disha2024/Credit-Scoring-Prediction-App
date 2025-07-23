import streamlit as st
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

st.set_page_config(page_title="Credit Scoring App", layout="centered")

# --- User File ---
USER_FILE = "users.csv"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    users = {}
    if os.path.exists(USER_FILE):
        with open(USER_FILE, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                users[row['email']] = row['password']
    return users

def save_user(email, password_hash):
    new_user = {'email': email, 'password': password_hash}
    file_exists = os.path.isfile(USER_FILE)
    with open(USER_FILE, 'a', newline='') as csvfile:
        fieldnames = ['email', 'password']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(new_user)

# --- Load Users ---
users = load_users()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = ""
    st.session_state.show_signup = False

# --- Authentication UI ---
if not st.session_state.logged_in:
    st.subheader("🔐 Authentication")

    if not st.session_state.show_signup:
        st.info("Don't have an account? [Sign Up](#)", icon="ℹ️")
        with st.form("login_form"):
            email = st.text_input("📧 Email")
            password = st.text_input("🔑 Password", type="password")
            submit = st.form_submit_button("Login")

            if submit:
                if email in users and hash_password(password) == users[email]:
                    st.session_state.logged_in = True
                    st.session_state.user_email = email
                    st.success(f"Welcome, {email}!")
                    st.rerun()
                else:
                    st.error("Invalid email or password.")

        if st.button("Sign Up Instead"):
            st.session_state.show_signup = True
            st.rerun()

    else:
        st.info("Already have an account? [Log In](#)", icon="ℹ️")
        with st.form("signup_form"):
            new_email = st.text_input("📧 New Email")
            new_password = st.text_input("🔑 New Password", type="password")
            submit_signup = st.form_submit_button("Register")

            if submit_signup:
                if new_email in users:
                    st.warning("User already exists.")
                else:
                    save_user(new_email, hash_password(new_password))
                    st.success("Registration successful. Please log in.")
                    st.session_state.show_signup = False
                    st.rerun()

        if st.button("Back to Login"):
            st.session_state.show_signup = False
            st.rerun()

# --- Main App ---
if st.session_state.logged_in:
    st.sidebar.success(f"Logged in as: {st.session_state.user_email}")

    # Load model and columns
    with open("credit_scoring_model.pkl", "rb") as f:
        model = pickle.load(f)

    with open("credit_model_columns.pkl", "rb") as f:
        column_names = pickle.load(f)

    def generate_pdf_report(
        lender_name, credit_amount, duration, age,
        employment, housing, installment_rate, savings, credit_history, result_text
    ):
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        c.setFont("Helvetica-Bold", 18)
        c.setFillColor(colors.darkblue)
        c.drawString(40, 760, "Credit Scoring Report")
        c.setStrokeColor(colors.grey)
        c.line(40, 755, 570, 755)

        c.setFont("Helvetica", 12)
        c.setFillColor(colors.black)
        y = 730
        line_gap = 20

        report_lines = [
            f"Lender Name         : {lender_name}",
            f"Credit Amount (DM)  : {credit_amount}",
            f"Duration (Months)   : {duration}",
            f"Age (Years)         : {age}",
            f"Employment (Encoded): {employment}",
            f"Housing Type        : {housing} (Encoded)",
            f"Installment Rate    : {installment_rate}%",
            f"Savings Account     : {savings} (Encoded)",
            f"Credit History      : {credit_history} (Encoded)",
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

   
    st.title("\U0001F4B3 Credit Scoring Prediction App")
    st.markdown("Provide customer details below to predict creditworthiness.")

    lender_name = st.text_input("\U0001F464 Lender's Name (used in PDF)", value="Customer_1")
    status = st.selectbox("\U0001F4C2 Status of Checking Account", [0,1,2,3])
    duration = st.slider("\u23F1\ufe0f Duration of Credit (Months)", 4, 72, 24)
    credit_history = st.selectbox("\U0001F4DC Credit History", [0,1,2,3,4])
    purpose = st.selectbox("\U0001F3AF Purpose of Loan", list(range(10)))
    credit_amount = st.number_input("\U0001F4B0 Credit Amount (DM)", 100, 50000, 1500)
    savings = st.selectbox("\U0001F3E6 Savings Account", [0,1,2,3,4])
    employment = st.selectbox("\U0001F9D1‍\U0001F4BC Employment Since", [0,1,2,3,4])
    installment_rate = st.slider("\U0001F4B8 Installment Rate (% of Income)", 1, 4, 2)
    personal_status = st.selectbox("\U0001F46A Personal Status / Sex", [0,1,2,3,4])
    other_debtors = st.selectbox("\U0001F91D Other Debtors/Guarantors", [0,1,2])
    residence = st.slider("\U0001F3E0 Years at Residence", 1, 4, 2)
    property_type = st.selectbox("\U0001F4C4 Property Type", [0,1,2,3])
    age = st.slider("\U0001F382 Age", 18, 75, 35)
    installment_plans = st.selectbox("\U0001F4E6 Other Installment Plans", [0,1,2])
    housing = st.selectbox("\U0001F3D8 Housing Type", [0,1,2])
    num_credits = st.slider("\U0001F501 Number of Existing Credits", 1, 4, 1)
    job = st.selectbox("\U0001F6E0 Job Type", [0,1,2,3])
    people_liable = st.selectbox("\U0001F465 Number of Liable People", [1,2])
    telephone = st.selectbox("\U0001F4DE Telephone Available", [0,1])
    foreign_worker = st.selectbox("\U0001F30D Is Foreign Worker?", [0,1])

    input_data = np.array([[
        status, duration, credit_history, purpose, credit_amount,
        savings, employment, installment_rate, personal_status, other_debtors,
        residence, property_type, age, installment_plans, housing, num_credits,
        job, people_liable, telephone, foreign_worker
    ]])
    input_df = pd.DataFrame(input_data, columns=column_names)

    if st.button("\U0001F680 Predict Creditworthiness"):
        prediction = model.predict(input_df)
        if prediction[0] == 1:
            result_text = "Credit Approved (Good Customer)"
            st.success("\u2705 " + result_text)
        else:
            result_text = "Credit Rejected (Bad Customer)"
            st.error("\u274C " + result_text)

        pdf = generate_pdf_report(
            lender_name, credit_amount, duration, age,
            employment, housing, installment_rate, savings, credit_history, result_text
        )

        st.download_button(
            label="\U0001F4C4 Download Credit Report (PDF)",
            data=pdf,
            file_name=f"{lender_name}_credit_report.pdf",
            mime="application/pdf"
        )

    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.session_state.show_signup = False
        st.rerun()
