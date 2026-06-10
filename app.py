import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from supabase import create_client

# Page config
st.set_page_config(page_title="Strategy Performance System", layout="wide")

# Initialize Supabase
def init_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

# Simple login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.user_dept = None
    st.session_state.user_name = None

if not st.session_state.logged_in:
    st.title("Strategy Performance System")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        # For now, use admin account
        if email == "admin@company.com" and password == "Admin123!":
            st.session_state.logged_in = True
            st.session_state.user_role = "admin"
            st.session_state.user_name = "System Admin"
            st.rerun()
        else:
            st.error("Invalid credentials")
else:
    st.sidebar.write(f"Welcome, {st.session_state.user_name}")
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()
    
    st.title("Strategy Performance Management System")
    
    # Simple dashboard
    col1, col2, col3 = st.columns(3)
    col1.metric("Action Plans", "3", "2 in progress")
    col2.metric("Contracts", "3", "1 expiring soon")
    col3.metric("Policies", "3", "2 active")
    
    st.info("✅ Database connected! Full features coming next.")
