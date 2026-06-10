import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
from PIL import Image
import base64
from io import BytesIO
import requests

# ============================================
# HELB BRANDING CONFIGURATION
# ============================================
HELB_GREEN = "#00843D"
HELB_GOLD = "#FFB81C"
HELB_BLUE = "#00529B"
HELB_DARK = "#1F2937"
HELB_WHITE = "#FFFFFF"

st.set_page_config(
    page_title="HELB Strategy Performance System",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# LOAD LOGO
# ============================================
def get_logo():
    try:
        response = requests.get("https://raw.githubusercontent.com/YOUR_USERNAME/strategy-system/main/HELB%20Logo.png", timeout=5)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            img.thumbnail((200, 80))
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            return base64.b64encode(buffered.getvalue()).decode()
    except:
        pass
    return None

LOGO = get_logo()

# ============================================
# FORCE ALL STYLES WITH !important
# ============================================
st.markdown("""
<style>
    /* Force all backgrounds to white */
    .stApp, .main, .stApp > div, .stApp header, .stApp .block-container {
        background-color: #FFFFFF !important;
    }
    
    /* Force all input boxes to have white background and black text */
    input, textarea, select, .stTextInput input, .stSelectbox select, .stTextArea textarea, .stNumberInput input {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 2px solid #00843D !important;
        border-radius: 8px !important;
    }
    
    /* Force all labels to be black */
    label, .stTextInput label, .stSelectbox label, .stTextArea label, .stNumberInput label {
        color: #000000 !important;
        font-weight: 500 !important;
    }
    
    /* Force all buttons to have white text */
    button, .stButton button {
        background: linear-gradient(135deg, #00843D 0%, #00529B 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #00843D !important;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #00843D !important;
    }
    
    /* All text except sidebar */
    p, div, span, li, .stMarkdown {
        color: #1F2937 !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #F0F2F6 !important;
        color: #00843D !important;
        border-radius: 8px !important;
    }
    
    /* Dropdown options */
    ul[role="listbox"] li {
        color: #000000 !important;
        background-color: #FFFFFF !important;
    }
    
    /* Progress bar text */
    .stProgress label {
        color: #000000 !important;
    }
    
    /* Status badges */
    .stAlert {
        color: #1F2937 !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# SUPABASE
# ============================================
@st.cache_resource
def init_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_supabase()

# ============================================
# SESSION STATE
# ============================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_role = None
    st.session_state.user_dept = None
    st.session_state.user_fullname = None
    st.session_state.user_id = None

# ============================================
# HELPER FUNCTIONS
# ============================================
def get_filtered_data(table_name):
    if st.session_state.user_role in ["admin", "management"]:
        return supabase.table(table_name).select("*").execute().data
    else:
        return supabase.table(table_name).select("*").eq("department_id", st.session_state.user_dept).execute().data

def get_department_name(dept_id):
    if not dept_id:
        return "N/A"
    result = supabase.table("departments").select("name").eq("id", dept_id).execute()
    return result.data[0]["name"] if result.data else "Unknown"

def get_all_users():
    return supabase.table("users").select("*").execute().data

def delete_user(username):
    supabase.table("users").delete().eq("username", username).execute()
    return True

def update_user_role(username, new_role, dept_id):
    supabase.table("users").update({"role": new_role, "department_id": dept_id}).eq("username", username).execute()
    return True

def reset_user_password(username, new_password):
    supabase.table("users").update({"password_hash": new_password}).eq("username", username).execute()
    return True

def create_new_user(username, full_name, password, role, dept_id):
    existing = supabase.table("users").select("*").eq("username", username.lower()).execute()
    if existing.data:
        return False, "Username exists"
    supabase.table("users").insert({
        "username": username.lower(),
        "full_name": full_name,
        "password_hash": password,
        "role": role,
        "department_id": dept_id
    }).execute()
    return True, "User created"

# ============================================
# LOGIN PAGE
# ============================================
if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if LOGO:
            st.image(f"data:image/png;base64,{LOGO}", width=180)
        else:
            st.markdown("<h1 style='text-align:center;'>🏦 HELB</h1>", unsafe_allow_html=True)
        
        st.markdown("<h3 style='text-align:center; color:#00843D;'>Strategy Performance Management System</h3>", unsafe_allow_html=True)
        st.markdown("---")
        
        with st.form("login"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", use_container_width=True)
            
            if submitted:
                result = supabase.table("users").select("*").eq("username", username.lower()).execute()
                if result.data and password == result.data[0]["password_hash"]:
                    user = result.data[0]
                    st.session_state.authenticated = True
                    st.session_state.user_role = user["role"]
                    st.session_state.user_dept = user["department_id"]
                    st.session_state.user_fullname = user["full_name"]
                    st.session_state.user_id = user["id"]
                    st.rerun()
                else:
                    st.error("Invalid credentials")
    st.stop()

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    if LOGO:
        st.image(f"data:image/png;base64,{LOGO}", width=120)
    else:
        st.markdown("<h2 style='text-align:center;'>🏦 HELB</h2>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style='background:rgba(255,255,255,0.2); padding:10px; border-radius:10px; margin:10px 0; text-align:center;'>
        <strong>{st.session_state.user_fullname}</strong><br>
        <small>{st.session_state.user_role.replace('_', ' ').title()}</small>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    menu = ["Dashboard", "Action Plans", "Contracts", "Policies"]
    if st.session_state.user_role == "admin":
        menu.append("User Management")
    if st.session_state.user_role in ["admin", "management"]:
        menu.append("Enterprise View")
    
    choice = st.radio("Navigation", menu)
    
    st.markdown("---")
    if st.button("Logout", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# ============================================
# DASHBOARD
# ============================================
if choice == "Dashboard":
    st.title("Dashboard Overview")
    
    plans = get_filtered_data("action_plans")
    contracts = get_filtered_data("contracts")
    policies = get_filtered_data("policies")
    
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        completed = sum(1 for p in plans if p.get("status") == "completed") if plans else 0
        total = len(plans) if plans else 0
        st.metric("Action Plans", f"{completed}/{total}")
    
    with c2:
        expiring = sum(1 for c in contracts if c.get("status") == "expiring_soon") if contracts else 0
        st.metric("Expiring Contracts", expiring)
    
    with c3:
        expiring_policies = 0
        if policies:
            for p in policies:
                expiry = datetime.strptime(p["expiry_date"], "%Y-%m-%d").date()
                if (expiry - datetime.now().date()).days <= 90:
                    expiring_policies += 1
        st.metric("Expiring Policies", expiring_policies)
    
    with c4:
        users = len(get_all_users())
        st.metric("Active Users", users)
    
    st.success(f"Welcome, {st.session_state.user_fullname}!")

# ============================================
# ACTION PLANS
# ============================================
elif choice == "Action Plans":
    st.title("Action Plan Monitor")
    
    with st.expander("➕ Add New Action Item"):
        with st.form("add_action"):
            task = st.text_input("Task Name")
            due = st.date_input("Due Date")
            status = st.selectbox("Status", ["not started", "in progress", "completed", "delayed"])
            progress = st.slider("Progress %", 0, 100)
            if st.form_submit_button("Save Action Item"):
                if task:
                    supabase.table("action_plans").insert({
                        "task_name": task,
                        "due_date": due.isoformat(),
                        "status": status,
                        "progress_percent": progress,
                        "department_id": st.session_state.user_dept,
                        "last_updated_by": st.session_state.user_id
                    }).execute()
                    st.success("Added!")
                    st.rerun()
    
    plans = get_filtered_data("action_plans")
    for plan in plans:
        with st.container():
            st.markdown(f"**{plan['task_name']}**")
            st.caption(f"Due: {plan['due_date']}")
            st.progress(plan["progress_percent"] / 100)
            new_progress = st.slider("Update %", 0, 100, plan["progress_percent"], key=plan["id"])
            if st.button(f"Update", key=f"upd_{plan['id']}"):
                supabase.table("action_plans").update({
                    "progress_percent": new_progress,
                    "status": "completed" if new_progress == 100 else "in progress"
                }).eq("id", plan["id"]).execute()
                st.rerun()
            st.markdown("---")

# ============================================
# CONTRACTS
# ============================================
elif choice == "Contracts":
    st.title("Contract Tracker")
    
    with st.expander("➕ Add New Contract"):
        with st.form("add_contract"):
            title = st.text_input("Contract Title")
            vendor = st.text_input("Vendor")
            end_date = st.date_input("End Date")
            auto_renew = st.checkbox("Auto-renewal")
            if st.form_submit_button("Save Contract"):
                if title and vendor:
                    days_left = (end_date - datetime.now().date()).days
                    status = "expired" if days_left < 0 else ("expiring_soon" if days_left <= 30 else "active")
                    supabase.table("contracts").insert({
                        "contract_title": title,
                        "vendor_name": vendor,
                        "start_date": datetime.now().date().isoformat(),
                        "end_date": end_date.isoformat(),
                        "days_remaining": days_left,
                        "status": status,
                        "auto_renewal": auto_renew,
                        "department_id": st.session_state.user_dept
                    }).execute()
                    st.success("Added!")
                    st.rerun()
    
    contracts = get_filtered_data("contracts")
    for contract in contracts:
        days_left = (datetime.strptime(contract["end_date"], "%Y-%m-%d").date() - datetime.now().date()).days
        if days_left > 30:
            badge = "🟢 Active"
        elif days_left > 0:
            badge = "🟡 Expiring Soon"
        else:
            badge = "🔴 Expired"
        
        st.markdown(f"""
        <div style='border:1px solid #ddd; padding:15px; border-radius:10px; margin:10px 0; background:#FAFAFA;'>
            <b>{badge} {contract['contract_title']}</b><br>
            Vendor: {contract['vendor_name']}<br>
            End Date: {contract['end_date']} ({days_left} days left)<br>
            Auto-renewal: {'Yes' if contract['auto_renewal'] else 'No'}
        </div>
        """, unsafe_allow_html=True)

# ============================================
# POLICIES
# ============================================
elif choice == "Policies":
    st.title("Policy Monitor")
    
    with st.expander("➕ Add New Policy"):
        with st.form("add_policy"):
            name = st.text_input("Policy Name")
            expiry = st.date_input("Expiry Date")
            is_global = st.checkbox("Global Policy")
            if st.form_submit_button("Save Policy"):
                if name:
                    supabase.table("policies").insert({
                        "policy_name": name,
                        "expiry_date": expiry.isoformat(),
                        "department_id": None if is_global else st.session_state.user_dept
                    }).execute()
                    st.success("Added!")
                    st.rerun()
    
    policies = get_filtered_data("policies")
    for policy in policies:
        days_left = (datetime.strptime(policy["expiry_date"], "%Y-%m-%d").date() - datetime.now().date()).days
        if days_left > 90:
            badge = "✅ Active"
        elif days_left > 0:
            badge = "⚠️ Expiring Soon"
        else:
            badge = "❌ Expired"
        
        st.markdown(f"**{badge} {policy['policy_name']}** - Expires: {policy['expiry_date']} ({days_left} days left)")

# ============================================
# USER MANAGEMENT
# ============================================
elif choice == "User Management" and st.session_state.user_role == "admin":
    st.title("User Management")
    
    depts = supabase.table("departments").select("id,name").execute().data
    dept_options = {d["name"]: d["id"] for d in depts}
    
    tab1, tab2, tab3 = st.tabs(["Create User", "Edit User", "Delete User"])
    
    with tab1:
        with st.form("create"):
            username = st.text_input("Username")
            full_name = st.text_input("Full Name")
            role = st.selectbox("Role", ["department_champion", "management", "admin"])
            department = st.selectbox("Department", ["None"] + list(dept_options.keys()))
            password = st.text_input("Password", type="password")
            confirm = st.text_input("Confirm Password", type="password")
            if st.form_submit_button("Create"):
                if password == confirm:
                    dept_id = dept_options.get(department) if department != "None" else None
                    success, msg = create_new_user(username, full_name, password, role, dept_id)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.error("Passwords don't match")
    
    with tab2:
        users = get_all_users()
        user_options = [f"{u['username']} - {u['full_name']}" for u in users if u['username'] != "admin"]
        if user_options:
            selected = st.selectbox("Select User", user_options)
            username = selected.split(" - ")[0]
            current = next(u for u in users if u['username'] == username)
            
            new_role = st.selectbox("New Role", ["department_champion", "management", "admin"], index=["department_champion", "management", "admin"].index(current["role"]))
            current_dept = get_department_name(current["department_id"])
            dept_list = ["None"] + list(dept_options.keys())
            idx = dept_list.index(current_dept) if current_dept in dept_list else 0
            new_dept = st.selectbox("Department", dept_list, index=idx)
            
            reset = st.checkbox("Reset Password")
            new_pwd = None
            if reset:
                new_pwd = st.text_input("New Password", type="password")
                confirm = st.text_input("Confirm Password", type="password")
            
            if st.button("Save Changes"):
                dept_id = dept_options.get(new_dept) if new_dept != "None" else None
                update_user_role(username, new_role, dept_id)
                if reset and new_pwd and new_pwd == confirm:
                    reset_user_password(username, new_pwd)
                st.success("Updated!")
                st.rerun()
    
    with tab3:
        users = get_all_users()
        delete_options = [f"{u['username']} - {u['full_name']}" for u in users if u['username'] != "admin"]
        if delete_options:
            selected = st.selectbox("Select User to Delete", delete_options)
            username = selected.split(" - ")[0]
            confirm = st.checkbox(f"Confirm delete {username}")
            if st.button("Delete"):
                if confirm:
                    delete_user(username)
                    st.success(f"Deleted {username}")
                    st.rerun()
                else:
                    st.error("Confirm deletion")

# ============================================
# ENTERPRISE VIEW
# ============================================
elif choice == "Enterprise View" and st.session_state.user_role in ["admin", "management"]:
    st.title("Enterprise View")
    
    depts = supabase.table("departments").select("*").execute().data
    dept_names = {d["id"]: d["name"] for d in depts}
    
    all_plans = supabase.table("action_plans").select("*").execute().data
    if all_plans:
        df = pd.DataFrame(all_plans)
        df["department"] = df["department_id"].map(dept_names)
        st.dataframe(df[["task_name", "department", "status", "progress_percent", "due_date"]], use_container_width=True)

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown("<p style='text-align:center; color:#666;'>© 2025 HELB - Higher Education Loans Board</p>", unsafe_allow_html=True)
