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

# Set page config at the top
st.set_page_config(page_title="Credit Scoring App", layout="centered")

# --- Functions ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if os.path.exists("users.csv"):
        return pd.read_csv("users.csv")
    else:
        return pd.DataFrame(columns=["email", "password"])

def save_user(email, password):
    users = load_users()
    if email not in users["email"].values:
        users.loc[len(users)] = [email, hash_password(password)]
        users.to_csv("users.csv", index=False)

def update_user_password(email, new_password):
    users = load_users()
    users.loc[users.email == email, "password"] = hash_password(new_password)
    users.to_csv("users.csv", index=False)

def delete_user_account(email):
    users = load_users()
    users = users[users.email != email]
    users.to_csv("users.csv", index=False)

def generate_pdf_report(
    lender_name, credit_amount, duration, age,
    employment, housing, installment_rate, savings,
    credit_history, telephone_number, result_text
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
        f"Employment          : {employment}",
        f"Housing Type        : {housing}",
        f"Installment Rate    : {installment_rate}%",
        f"Savings Account     : {savings}",
        f"Credit History      : {credit_history}",
        f"Telephone Number    : {telephone_number}",
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

# --- Session State ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = ""

# --- Login/Register ---
if not st.session_state.logged_in:
    st.subheader("🔐 Login")
    tab1, tab2, tab3 = st.tabs(["Login", "Sign Up", "Forgot Password"])

    with tab1:
        login_email = st.text_input("📧 Email")
        login_pw = st.text_input("🔑 Password", type="password")
        if st.button("Login"):
            users_df = load_users()
            if "password" not in users_df.columns:
                st.error("User database is corrupted. No password column found.")
            else:
                user_match = users_df[(users_df["email"] == login_email) & (users_df["password"] == hash_password(login_pw))]
                if not user_match.empty:
                    st.session_state.logged_in = True
                    st.session_state.user_email = login_email
                    st.success(f"Welcome, {login_email}!")
                    st.rerun()
                else:
                    st.error("Invalid email or password. Forgot Password? Go to tab above.")

    with tab2:
        new_email = st.text_input("New Email")
        new_pw = st.text_input("New Password", type="password")
        if st.button("Sign Up"):
            save_user(new_email, new_pw)
            st.success("Account created! Please log in.")

    with tab3:
        reset_email = st.text_input("Enter your registered email")
        new_reset_pw = st.text_input("Enter new password", type="password")
        if st.button("Reset Password"):
            users_df = load_users()
            if reset_email in users_df.email.values:
                update_user_password(reset_email, new_reset_pw)
                st.success("Password reset successfully!")
            else:
                st.error("Email not found.")

else:
    st.sidebar.success(f"Logged in as: {st.session_state.user_email}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.rerun()

    if st.sidebar.button("Delete My Account"):
        confirm = st.sidebar.checkbox("I confirm to delete my account")
        if confirm:
            delete_user_account(st.session_state.user_email)
            st.success("Your account has been deleted.")
            st.session_state.logged_in = False
            st.session_state.user_email = ""
            st.rerun()

    # --- Load model and columns ---
    with open("credit_scoring_model.pkl", "rb") as f:
        model = pickle.load(f)
    with open("credit_model_columns.pkl", "rb") as f:
        column_names = pickle.load(f)

    st.title("💳 Credit Scoring Prediction App")
    st.markdown("Provide customer details below to predict creditworthiness.")

    lender_name = st.text_input("👤 Lender's Name", value="Customer_1")
    telephone_text = st.text_input("📞 Telephone Number")
    telephone = 1 if telephone_text.strip() else 0

    status = st.selectbox("📂 Checking Account Status", ["No Account", "< 0 DM", "0 <= ... < 200 DM", ">= 200 DM"])
    credit_history = st.selectbox("📄 Credit History", ["No Credit", "Paid Back Duly", "Critical Account", "Paid Delayed", "Existing Credit"])
    purpose = st.selectbox("🎯 Loan Purpose", ["New Car", "Used Car", "Furniture", "Radio/TV", "Appliances", "Repairs", "Education", "Vacation", "Retraining", "Business"])
    savings = st.selectbox("🏦 Savings Account", ["None", "< 100 DM", "100 <= ... < 500 DM", "500 <= ... < 1000 DM", ">= 1000 DM"])
    employment = st.selectbox("👨‍💼 Employment Since", ["Unemployed", "< 1 year", "1 <= ... < 4 years", "4 <= ... < 7 years", ">= 7 years"])
    housing = st.selectbox("🏘 Housing Type", ["Own", "Rent", "For Free"])
    foreign_worker = st.selectbox("🌍 Foreign Worker?", ["No", "Yes"])

    duration = st.slider("⏱ Credit Duration (Months)", 4, 72, 24)
    credit_amount = st.number_input("💰 Credit Amount (DM)", 100, 50000, 1500)
    installment_rate = st.slider("💸 Installment Rate (%)", 1, 4, 2)
    personal_status = st.selectbox("👪 Personal Status", ["Male Single", "Female Divorced", "Male Married", "Male Divorced", "Female Single"])
    other_debtors = st.selectbox("🤝 Other Debtors", ["None", "Co-applicant", "Guarantor"])
    residence = st.slider("🏠 Years at Residence", 1, 4, 2)
    property_type = st.selectbox("📜 Property Type", ["Real Estate", "Building Society", "Car", "Unknown"])
    age = st.slider("🎂 Age", 18, 75, 35)
    installment_plans = st.selectbox("📦 Installment Plans", ["None", "Bank", "Stores"])
    num_credits = st.slider("🔁 Number of Existing Credits", 1, 4, 1)
    job = st.selectbox("🛠 Job Type", ["Unemployed", "Unskilled", "Skilled", "Highly Skilled"])
    people_liable = st.selectbox("👥 Number of Liable People", [1, 2])

    # Encoding dictionaries
    encodings = {
        "Checking Account Status": {"No Account": 0, "< 0 DM": 1, "0 <= ... < 200 DM": 2, ">= 200 DM": 3},
        "Credit History": {"No Credit": 0, "Paid Back Duly": 1, "Critical Account": 2, "Paid Delayed": 3, "Existing Credit": 4},
        "Purpose": {"New Car": 0, "Used Car": 1, "Furniture": 2, "Radio/TV": 3, "Appliances": 4, "Repairs": 5, "Education": 6, "Vacation": 7, "Retraining": 8, "Business": 9},
        "Savings": {"None": 0, "< 100 DM": 1, "100 <= ... < 500 DM": 2, "500 <= ... < 1000 DM": 3, ">= 1000 DM": 4},
        "Employment": {"Unemployed": 0, "< 1 year": 1, "1 <= ... < 4 years": 2, "4 <= ... < 7 years": 3, ">= 7 years": 4},
        "Housing": {"Own": 0, "Rent": 1, "For Free": 2},
        "Foreign Worker": {"No": 0, "Yes": 1},
        "Personal Status": {"Male Single": 0, "Female Divorced": 1, "Male Married": 2, "Male Divorced": 3, "Female Single": 4},
        "Other Debtors": {"None": 0, "Co-applicant": 1, "Guarantor": 2},
        "Property Type": {"Real Estate": 0, "Building Society": 1, "Car": 2, "Unknown": 3},
        "Installment Plans": {"None": 0, "Bank": 1, "Stores": 2},
        "Job": {"Unemployed": 0, "Unskilled": 1, "Skilled": 2, "Highly Skilled": 3}
    }

    input_data = np.array([[
        encodings["Checking Account Status"][status],
        duration,
        encodings["Credit History"][credit_history],
        encodings["Purpose"][purpose],
        credit_amount,
        encodings["Savings"][savings],
        encodings["Employment"][employment],
        installment_rate,
        encodings["Personal Status"][personal_status],
        encodings["Other Debtors"][other_debtors],
        residence,
        encodings["Property Type"][property_type],
        age,
        encodings["Installment Plans"][installment_plans],
        encodings["Housing"][housing],
        num_credits,
        encodings["Job"][job],
        people_liable,
        telephone,
        encodings["Foreign Worker"][foreign_worker]
    ]])

    input_df = pd.DataFrame(input_data, columns=column_names)

    if st.button("🚀 Predict Creditworthiness"):
        prediction = model.predict(input_df)
        if prediction[0] == 1:
            result_text = "Credit Approved"
            st.success("✅ " + result_text)
        else:
            result_text = "Credit Rejected"
            st.error("❌ " + result_text)

        pdf = generate_pdf_report(
            lender_name, credit_amount, duration, age,
            employment, housing, installment_rate, savings, credit_history, telephone_text, result_text
        )

        st.download_button("📄 Download Credit Report (PDF)", data=pdf,
                           file_name=f"{lender_name}_credit_report.pdf", mime="application/pdf")
