
import streamlit as st
import pandas as pd
import joblib

# Dummy user database
USERS = {
    'admin': {'password': 'admin123', 'role': 'admin'},
    'auditor': {'password': 'audit123', 'role': 'auditor'},
    'user1': {'password': 'user123', 'role': 'user'}
}

# Session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ''
    st.session_state.role = ''

model = joblib.load('fraud_model.pkl')

def login():
    st.title("🔐 Login to Fraud Detection System")

    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    if st.button("Login"):
        if username in USERS and USERS[username]['password'] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = USERS[username]['role']
            st.success(f"Welcome, {username} ({st.session_state.role})")
            st.rerun()
        else:
            st.error("Invalid username or password")

def admin_dashboard():
    st.title("👨‍💼 Admin Panel")
    uploaded_file = st.file_uploader("Upload transaction CSV (exclude 'Class')", type='csv')
    if uploaded_file:
        data = pd.read_csv(uploaded_file)
        st.write("Data Preview:")
        st.dataframe(data.head())

        # Match columns with model features
        expected_features = model.feature_names_in_

        # Filter to expected columns only (handle missing columns if any)
        missing_cols = [col for col in expected_features if col not in data.columns]
        if missing_cols:
            st.error(f"The uploaded file is missing these required columns: {missing_cols}")
            return

        data = data[expected_features]

        # Fill any missing values
        data = data.fillna(data.mean())

        predictions = model.predict(data)
        data['Fraud Prediction'] = predictions
        st.success("Fraud predictions complete.")
        st.dataframe(data)

        # Save to CSV for auditor
        data.to_csv('predictions.csv', index=False)


def auditor_dashboard():
    st.title("📋 Auditor Panel")
    try:
        with open("predictions.csv", "rb") as file:
            btn = st.download_button(
                label="📥 Download Latest Fraud Predictions",
                data=file,
                file_name="fraud_predictions.csv",
                mime="text/csv"
            )
    except FileNotFoundError:
        st.warning("No predictions found. Ask admin to upload and predict first.")

def user_dashboard():
    st.title("👩‍💻 User Dashboard")
    st.info("You are logged in as a user. No admin privileges.")
    st.write("Contact your admin or auditor for fraud reports.")

# App Routing
if not st.session_state.logged_in:
    login()
else:
    st.sidebar.write(f"Logged in as: **{st.session_state.username}** ({st.session_state.role})")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    role = st.session_state.role
    if role == 'admin':
        admin_dashboard()
    elif role == 'auditor':
        auditor_dashboard()
    elif role == 'user':
        user_dashboard()
