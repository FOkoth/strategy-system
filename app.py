import streamlit as st
from supabase import create_client
from datetime import datetime
import pandas as pd
import plotly.express as px

# Page config
st.set_page_config(page_title="HELB Strategy System", layout="wide")

# Supabase connection
@st.cache_resource
def init_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.full_name = None
    st.session_state.role = None
    st.session_state.dept_id = None

# Login page
if not st.session_state.logged_in:
    st.title("🔐 HELB Strategy System")
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("### Login")
        
        with st.form("login"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                try:
                    # Query user
                    result = supabase.table("users").select("*").eq("username", username).execute()
                    
                    if result.data:
                        user = result.data[0]
                        # Simple password check
                        if password == user["password_hash"]:
                            st.session_state.logged_in = True
                            st.session_state.username = user["username"]
                            st.session_state.full_name = user["full_name"]
                            st.session_state.role = user["role"]
                            st.session_state.dept_id = user["department_id"]
                            st.rerun()
                        else:
                            st.error("Wrong password")
                    else:
                        st.error(f"User '{username}' not found")
                        
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    st.stop()

# Main app after login
st.sidebar.write(f"Welcome, **{st.session_state.full_name}**")
st.sidebar.write(f"Role: {st.session_state.role}")
st.sidebar.write(f"Username: {st.session_state.username}")

if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()

st.title("📊 HELB Strategy Performance Management System")

# Simple dashboard
st.write("### Dashboard")

col1, col2, col3 = st.columns(3)

# Get counts
try:
    plans_count = len(supabase.table("action_plans").select("*").execute().data)
    contracts_count = len(supabase.table("contracts").select("*").execute().data)
    policies_count = len(supabase.table("policies").select("*").execute().data)
    
    col1.metric("Action Plans", plans_count)
    col2.metric("Contracts", contracts_count)
    col3.metric("Policies", policies_count)
except:
    col1.metric("Action Plans", "?")
    col2.metric("Contracts", "?")
    col3.metric("Policies", "?")

st.success(f"✅ You are logged in as {st.session_state.full_name} ({st.session_state.role})")

# Show action plans
st.write("### Recent Action Plans")
try:
    plans = supabase.table("action_plans").select("*").limit(5).execute().data
    if plans:
        df = pd.DataFrame(plans)
        st.dataframe(df[["task_name", "status", "progress_percent", "due_date"]])
    else:
        st.info("No action plans yet")
except:
    st.info("No data found")
