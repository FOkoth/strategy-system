import streamlit as st
from supabase import create_client
import requests

st.set_page_config(page_title="Connection Test", layout="wide")

st.title("🔧 Supabase Connection Test")

# Get secrets
try:
    URL = st.secrets["SUPABASE_URL"]
    KEY = st.secrets["SUPABASE_KEY"]
    
    st.write("### 📡 Secrets found:")
    st.code(f"SUPABASE_URL = {URL}")
    st.code(f"SUPABASE_KEY = {KEY[:30]}...")
except Exception as e:
    st.error(f"❌ Secrets error: {e}")
    st.stop()

# Test 1: Direct REST API call (bypasses supabase library)
st.write("### Test 1: Direct REST API Call")

headers = {
    "apikey": KEY,
    "Authorization": f"Bearer {KEY}"
}

try:
    response = requests.get(f"{URL}/rest/v1/users?select=*", headers=headers)
    st.write(f"**Status code:** {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        st.success(f"✅ API call successful! Found {len(data)} users")
        if data:
            st.write("Users found:")
            for user in data:
                st.write(f"  - {user.get('username')} (role: {user.get('role')})")
    else:
        st.error(f"❌ API failed: {response.text}")
        
except Exception as e:
    st.error(f"❌ Request error: {e}")

# Test 2: Using supabase library
st.write("### Test 2: Supabase Library Test")

try:
    supabase = create_client(URL, KEY)
    result = supabase.table("users").select("*").execute()
    st.success(f"✅ Library call successful! Found {len(result.data)} users")
    
    if result.data:
        for user in result.data:
            st.write(f"  - {user['username']} (password: {user['password_hash']})")
            
except Exception as e:
    st.error(f"❌ Library error: {e}")

# Test 3: Check if tables exist
st.write("### Test 3: Checking Tables")

try:
    supabase = create_client(URL, KEY)
    
    tables = ["users", "departments", "action_plans", "contracts", "policies"]
    
    for table in tables:
        try:
            result = supabase.table(table).select("*").limit(1).execute()
            st.success(f"✅ Table '{table}' exists")
        except Exception as e:
            st.error(f"❌ Table '{table}' not accessible: {e}")
            
except Exception as e:
    st.error(f"Error: {e}")

# Instructions
st.write("---")
st.write("### What to do next:")

if response.status_code == 200 and len(response.json()) == 0:
    st.warning("Your connection works but the users table is EMPTY. Run this SQL in Supabase:")
    st.code("""
    INSERT INTO users (username, full_name, password_hash, role, department_id) 
    VALUES ('admin', 'System Administrator', 'admin123', 'admin', NULL);
    """)
    
elif response.status_code != 200:
    st.error(f"Your connection is FAILING. Status code: {response.status_code}")
    st.write("Possible issues:")
    st.write("1. Wrong SUPABASE_URL - should be: https://YOUR_PROJECT.supabase.co")
    st.write("2. Wrong SUPABASE_KEY - use the 'anon public' key, NOT the 'secret' key")
    st.write("3. Table doesn't exist - run the database setup script first")
    st.write(f"Your current URL: {URL}")
    
elif response.status_code == 200 and len(response.json()) > 0:
    st.success("Your connection works and you have users! Try logging in with the usernames shown above.")
