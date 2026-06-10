import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

st.set_page_config(page_title="HELB Strategy System", layout="wide")

# Supabase connection
@st.cache_resource
def init_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_supabase()

# Session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.user_role = None
    st.session_state.user_dept = None
    st.session_state.user_name = None
    st.session_state.user_fullname = None
    st.session_state.user_id = None

# ============================================
# HELPER FUNCTIONS
# ============================================
def get_department_name(dept_id):
    if dept_id is None:
        return "N/A"
    try:
        result = supabase.table("departments").select("name").eq("id", dept_id).execute()
        return result.data[0]["name"] if result.data else "Unknown"
    except:
        return "Unknown"

def get_filtered_data(table_name):
    if st.session_state.user_role in ["admin", "management"]:
        return supabase.table(table_name).select("*").execute().data
    else:
        return supabase.table(table_name).select("*").eq("department_id", st.session_state.user_dept).execute().data

# ============================================
# LOGIN
# ============================================
if not st.session_state.logged_in:
    st.title("🔐 HELB Strategy Performance Management System")
    
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
                    st.session_state.user_role = user["role"]
                    st.session_state.user_dept = user["department_id"]
                    st.session_state.user_name = user["username"]
                    st.session_state.user_fullname = user["full_name"]
                    st.session_state.user_id = user["id"]
                    st.rerun()
                else:
                    st.error("Invalid password")
            else:
                st.error("User not found")
    
    st.stop()

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.markdown("### HELB Strategy System")
    st.markdown("---")
    st.markdown(f"**Welcome, {st.session_state.user_fullname}**")
    st.markdown(f"**Role:** {st.session_state.user_role.replace('_', ' ').title()}")
    
    if st.session_state.user_role == "department_champion":
        dept_name = get_department_name(st.session_state.user_dept)
        st.markdown(f"**Department:** {dept_name}")
    
    st.markdown("---")
    
    if st.button("🚪 Logout"):
        st.session_state.clear()
        st.rerun()
    
    st.markdown("---")
    
    # Navigation
    menu = ["Dashboard", "Action Plans", "Contracts", "Policies"]
    if st.session_state.user_role == "admin":
        menu.append("👥 User Management")
    if st.session_state.user_role in ["admin", "management"]:
        menu.append("🏢 Enterprise View")
    
    choice = st.radio("Navigation", menu)

st.title("📊 HELB Strategy Performance Management System")

# ============================================
# DASHBOARD
# ============================================
if choice == "Dashboard":
    st.subheader("Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    
    plans = get_filtered_data("action_plans")
    contracts = get_filtered_data("contracts")
    policies = get_filtered_data("policies")
    
    if plans:
        completed = sum(1 for p in plans if p.get("status") == "completed")
        total = len(plans)
        avg_progress = sum(p.get("progress_percent", 0) for p in plans) / total if total > 0 else 0
        col1.metric("Action Plans", f"{completed}/{total}", f"{avg_progress:.0f}%")
        
        overdue = sum(1 for p in plans if p.get("due_date", "") < str(datetime.now().date()) and p.get("status") != "completed")
        col2.metric("Overdue Tasks", overdue)
    else:
        col1.metric("Action Plans", "0")
        col2.metric("Overdue Tasks", "0")
    
    if contracts:
        expiring = sum(1 for c in contracts if c.get("status") == "expiring_soon")
        col3.metric("Expiring Contracts", expiring)
    else:
        col3.metric("Expiring Contracts", "0")
    
    if policies:
        expiring_policies = sum(1 for p in policies if p.get("expiry_date", "") and (datetime.strptime(p["expiry_date"], "%Y-%m-%d").date() - datetime.now().date()).days <= 90)
        col4.metric("Policies Expiring", expiring_policies)
    else:
        col4.metric("Policies Expiring", "0")
    
    # Chart
    if plans:
        st.subheader("Action Plan Progress")
        df = pd.DataFrame(plans)
        fig = px.bar(df, x="task_name", y="progress_percent", color="status")
        st.plotly_chart(fig, use_container_width=True)

# ============================================
# ACTION PLANS
# ============================================
elif choice == "Action Plans":
    st.subheader("Action Plan Monitor")
    
    with st.expander("➕ Add New Action Item"):
        with st.form("new_plan"):
            task_name = st.text_input("Task Name")
            due_date = st.date_input("Due Date")
            status = st.selectbox("Status", ["not started", "in progress", "completed", "delayed"])
            progress = st.slider("Progress %", 0, 100)
            
            if st.form_submit_button("Save"):
                supabase.table("action_plans").insert({
                    "task_name": task_name,
                    "due_date": due_date.isoformat(),
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
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"**{plan['task_name']}**")
                st.caption(f"Due: {plan['due_date']}")
            with col2:
                st.progress(plan["progress_percent"] / 100)
            with col3:
                if st.button(f"Update", key=f"p_{plan['id']}"):
                    new_progress = st.number_input("Progress", 0, 100, plan["progress_percent"], key=f"np_{plan['id']}")
                    if st.button(f"Save", key=f"s_{plan['id']}"):
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
    st.subheader("Contract Tracker")
    
    with st.expander("➕ Add New Contract"):
        with st.form("new_contract"):
            title = st.text_input("Contract Title")
            vendor = st.text_input("Vendor")
            end_date = st.date_input("End Date")
            auto_renew = st.checkbox("Auto-renewal")
            
            if st.form_submit_button("Save"):
                start_date = datetime.now().date()
                days_left = (end_date - start_date).days
                status = "expired" if days_left < 0 else ("expiring_soon" if days_left <= 30 else "active")
                
                supabase.table("contracts").insert({
                    "contract_title": title,
                    "vendor_name": vendor,
                    "start_date": start_date.isoformat(),
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
        end_date = datetime.strptime(contract["end_date"], "%Y-%m-%d").date()
        days_left = (end_date - datetime.now().date()).days
        
        if days_left > 30:
            color = "🟢"
        elif days_left > 0:
            color = "🟡"
        else:
            color = "🔴"
        
        st.markdown(f"""
        <div style="border:1px solid #ddd; padding:10px; margin:5px 0; border-radius:5px">
        <b>{color} {contract['contract_title']}</b><br>
        Vendor: {contract['vendor_name']}<br>
        End Date: {contract['end_date']} ({days_left} days left)
        </div>
        """, unsafe_allow_html=True)

# ============================================
# POLICIES
# ============================================
elif choice == "Policies":
    st.subheader("Policy Monitor")
    
    with st.expander("➕ Add New Policy"):
        with st.form("new_policy"):
            policy_name = st.text_input("Policy Name")
            expiry_date = st.date_input("Expiry Date")
            is_global = st.checkbox("Global Policy")
            
            if st.form_submit_button("Save"):
                supabase.table("policies").insert({
                    "policy_name": policy_name,
                    "expiry_date": expiry_date.isoformat(),
                    "department_id": None if is_global else st.session_state.user_dept
                }).execute()
                st.success("Added!")
                st.rerun()
    
    policies = get_filtered_data("policies")
    for policy in policies:
        expiry = datetime.strptime(policy["expiry_date"], "%Y-%m-%d").date()
        days_left = (expiry - datetime.now().date()).days
        
        if days_left > 90:
            alert = "✅"
        elif days_left > 0:
            alert = "⚠️"
        else:
            alert = "❌"
        
        st.markdown(f"{alert} **{policy['policy_name']}** - Expires: {policy['expiry_date']}")

# ============================================
# USER MANAGEMENT
# ============================================
elif choice == "👥 User Management" and st.session_state.user_role == "admin":
    st.subheader("User Management")
    
    with st.expander("➕ Create New User"):
        with st.form("new_user"):
            username = st.text_input("Username")
            full_name = st.text_input("Full Name")
            role = st.selectbox("Role", ["admin", "management", "department_champion"])
            depts = supabase.table("departments").select("id,name").execute().data
            dept_options = {d["name"]: d["id"] for d in depts}
            department = st.selectbox("Department", ["None"] + list(dept_options.keys()))
            password = st.text_input("Password", type="password")
            
            if st.form_submit_button("Create"):
                supabase.table("users").insert({
                    "username": username.lower(),
                    "full_name": full_name,
                    "password_hash": password,
                    "role": role,
                    "department_id": dept_options.get(department) if department != "None" else None
                }).execute()
                st.success(f"User {username} created!")
                st.rerun()
    
    users = supabase.table("users").select("*").execute().data
    st.dataframe(pd.DataFrame(users)[["username", "full_name", "role", "department_id"]])

# ============================================
# ENTERPRISE VIEW
# ============================================
elif choice == "🏢 Enterprise View" and st.session_state.user_role in ["admin", "management"]:
    st.subheader("Enterprise View - All Departments")
    
    depts = supabase.table("departments").select("*").execute().data
    dept_names = {d["id"]: d["name"] for d in depts}
    
    all_plans = supabase.table("action_plans").select("*").execute().data
    if all_plans:
        df = pd.DataFrame(all_plans)
        df["department"] = df["department_id"].map(dept_names)
        st.dataframe(df[["task_name", "department", "status", "progress_percent", "due_date"]], use_container_width=True)

st.success(f"✅ Logged in as {st.session_state.user_fullname}")
