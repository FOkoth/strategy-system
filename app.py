import streamlit as st
from supabase import create_client

st.set_page_config(page_title="HELB System", layout="wide")

# Supabase connection
supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

st.title("HELB Strategy System")

# Simple login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        # Query users
        result = supabase.table("users").select("*").eq("username", username).execute()
        
        st.write(f"Debug: Query returned {len(result.data)} users")
        
        if result.data:
            user = result.data[0]
            st.write(f"Debug: Found user {user['username']} with password {user['password_hash']}")
            
            if password == user["password_hash"]:
                st.session_state.logged_in = True
                st.session_state.user = user
                st.rerun()
            else:
                st.error("Wrong password")
        else:
            st.error(f"User '{username}' not found")
            # Show all users for debugging
            all_users = supabase.table("users").select("username").execute()
            if all_users.data:
                st.write("Available users:", [u["username"] for u in all_users.data])
    
    st.stop()

# Logged in
st.success(f"Welcome {st.session_state.user['full_name']}!")
if st.button("Logout"):
    st.session_state.clear()
    st.rerun()

st.write("### Dashboard")
st.write(f"Role: {st.session_state.user['role']}")
