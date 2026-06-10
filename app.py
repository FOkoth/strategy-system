import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="HELB Strategy System", layout="wide")

# Supabase connection
@st.cache_resource
def init_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

# Session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None

# Login page
if not st.session_state.logged_in:
    st.title("HELB Strategy Performance System")
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("### Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login", use_container_width=True):
            result = supabase.table("users").select("*").eq("username", username).execute()
            
            if result.data:
                user = result.data[0]
                if password == user["password_hash"]:
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("Invalid password")
            else:
                st.error(f"User '{username}' not found")
    
    st.stop()

# Main app
with st.sidebar:
    st.markdown("### HELB Strategy System")
    st.markdown("---")
    st.markdown(f"**Welcome, {st.session_state.user['full_name']}**")
    st.markdown(f"**Username:** {st.session_state.user['username']}")
    st.markdown(f"**Role:** {st.session_state.user['role']}")
    st.markdown("---")
    
    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()

st.title("HELB Strategy Performance Management System")
st.success(f"Logged in as {st.session_state.user['full_name']}")

# Dashboard
col1, col2, col3 = st.columns(3)

plans = supabase.table("action_plans").select("*").execute().data
contracts = supabase.table("contracts").select("*").execute().data
policies = supabase.table("policies").select("*").execute().data

col1.metric("Action Plans", len(plans))
col2.metric("Contracts", len(contracts))
col3.metric("Policies", len(policies))

if plans:
    st.subheader("Recent Action Plans")
    df = pd.DataFrame(plans)
    st.dataframe(df[["task_name", "status", "progress_percent", "due_date"]], use_container_width=True)
