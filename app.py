import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
from supabase import create_client
import bcrypt

# Page config
st.set_page_config(page_title="Strategy Performance System", layout="wide")

# Initialize Supabase
@st.cache_resource
def init_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

# Authentication
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user_role = None
        st.session_state.user_dept = None
        st.session_state.user_name = None
        st.session_state.user_id = None
    
    if st.session_state.authenticated:
        return True
    
    st.title("🔐 Strategy Performance System")
    
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            try:
                result = supabase.table("users").select("*").eq("email", email).execute()
                if result.data:
                    user = result.data[0]
                    if bcrypt.checkpw(password.encode('utf-8'), user["password_hash"].encode('utf-8')):
                        st.session_state.authenticated = True
                        st.session_state.user_role = user["role"]
                        st.session_state.user_dept = user["department_id"]
                        st.session_state.user_name = user["name"]
                        st.session_state.user_id = user["id"]
                        st.rerun()
                    else:
                        st.error("Invalid password")
                else:
                    st.error("User not found")
            except Exception as e:
                st.error(f"Login error: {str(e)}")
    
    return False

# Fetch data based on role
def get_filtered_data(table_name):
    if st.session_state.user_role == "admin":
        return supabase.table(table_name).select("*").execute().data
    else:
        return supabase.table(table_name).select("*").eq("department_id", st.session_state.user_dept).execute().data

# Main app
def main():
    if not check_password():
        return
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.user_name}")
        st.markdown(f"**Role:** {st.session_state.user_role}")
        st.markdown("---")
        
        if st.button("🚪 Logout"):
            st.session_state.clear()
            st.rerun()
        
        st.markdown("---")
        menu = st.radio("📋 Navigation", ["Dashboard", "Action Plans", "Contracts", "Policies"])
        
        if st.session_state.user_role in ["admin", "manager"]:
            st.markdown("---")
            if st.button("🏢 Enterprise View"):
                st.session_state.show_management = True
        
        if st.session_state.get("show_management", False):
            menu = "Management View"
    
    st.title("📊 Strategy Performance Management System")
    
    if menu == "Dashboard":
        show_dashboard()
    elif menu == "Action Plans":
        show_action_plans()
    elif menu == "Contracts":
        show_contracts()
    elif menu == "Policies":
        show_policies()
    elif menu == "Management View":
        show_management_view()

def show_dashboard():
    col1, col2, col3, col4 = st.columns(4)
    
    # Get data
    plans = get_filtered_data("action_plans")
    contracts = get_filtered_data("contracts")
    policies = get_filtered_data("policies")
    
    # Calculate metrics
    if plans:
        completed = sum(1 for p in plans if p.get("status") == "completed")
        total = len(plans)
        avg_progress = sum(p.get("progress_percent", 0) for p in plans) / total if total > 0 else 0
        col1.metric("Action Plans", f"{completed}/{total}", f"{avg_progress:.0f}% complete")
        
        overdue = sum(1 for p in plans if p.get("due_date", "") < str(datetime.now().date()) and p.get("status") != "completed")
        col2.metric("Overdue Tasks", overdue, delta="⚠️ Needs attention" if overdue > 0 else None)
    
    if contracts:
        expiring = 0
        for c in contracts:
            end_date = datetime.strptime(c["end_date"], "%Y-%m-%d").date()
            days_left = (end_date - datetime.now().date()).days
            if 0 < days_left <= 30:
                expiring += 1
        col3.metric("Contracts Expiring (30 days)", expiring)
    
    if policies:
        expiring_policies = 0
        for p in policies:
            expiry_date = datetime.strptime(p["expiry_date"], "%Y-%m-%d").date()
            days_left = (expiry_date - datetime.now().date()).days
            if 0 < days_left <= 90:
                expiring_policies += 1
        col4.metric("Policies Expiring Soon", expiring_policies)
    
    # Progress chart
    if plans:
        st.subheader("📈 Action Plan Progress")
        df = pd.DataFrame(plans)
        fig = px.bar(df, x="task_name", y="progress_percent", color="status", title="Progress by Task")
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent contracts
    if contracts:
        st.subheader("📄 Contracts Expiring Soon")
        expiring_contracts = []
        for c in contracts:
            end_date = datetime.strptime(c["end_date"], "%Y-%m-%d").date()
            days_left = (end_date - datetime.now().date()).days
            if 0 < days_left <= 30:
                expiring_contracts.append(c)
        
        if expiring_contracts:
            for c in expiring_contracts:
                st.warning(f"⚠️ **{c['contract_title']}** with {c['vendor_name']} expires in {days_left} days ({c['end_date']})")
        else:
            st.info("No contracts expiring soon")

def show_action_plans():
    st.subheader("✅ Action Plan Monitor")
    
    # Add new form
    with st.expander("➕ Add New Action Item", expanded=False):
        with st.form("new_action"):
            col1, col2 = st.columns(2)
            with col1:
                task_name = st.text_input("Task Name*")
                due_date = st.date_input("Due Date*")
            with col2:
                status = st.selectbox("Status", ["not started", "in progress", "completed", "delayed"])
                progress = st.slider("Progress %", 0, 100)
            
            submitted = st.form_submit_button("Save Action Item")
            if submitted and task_name:
                supabase.table("action_plans").insert({
                    "task_name": task_name,
                    "due_date": due_date.isoformat(),
                    "status": status,
                    "progress_percent": progress,
                    "department_id": st.session_state.user_dept,
                    "last_updated_by": st.session_state.user_id
                }).execute()
                st.success("✅ Action item added!")
                st.rerun()
    
    # Display existing
    plans = get_filtered_data("action_plans")
    if plans:
        for plan in plans:
            due_date = datetime.strptime(plan["due_date"], "%Y-%m-%d").date()
            days_left = (due_date - datetime.now().date()).days
            
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                with col1:
                    st.markdown(f"**{plan['task_name']}**")
                    st.caption(f"Due: {plan['due_date']} ({days_left} days left)")
                with col2:
                    st.progress(plan["progress_percent"] / 100)
                    st.caption(f"{plan['progress_percent']}%")
                with col3:
                    st.markdown(f"Status: {plan['status']}")
                with col4:
                    if st.button(f"Update", key=f"update_{plan['id']}"):
                        new_progress = st.slider("New Progress", 0, 100, plan["progress_percent"], key=f"slider_{plan['id']}")
                        if st.button(f"Save", key=f"save_{plan['id']}"):
                            supabase.table("action_plans").update({
                                "progress_percent": new_progress,
                                "status": "completed" if new_progress == 100 else "in progress"
                            }).eq("id", plan["id"]).execute()
                            st.rerun()
                st.markdown("---")
    else:
        st.info("No action plans. Click 'Add New Action Item' to create one.")

def show_contracts():
    st.subheader("📄 Contract Tracker")
    
    with st.expander("➕ Add New Contract", expanded=False):
        with st.form("new_contract"):
            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input("Contract Title*")
                vendor = st.text_input("Vendor*")
            with col2:
                end_date = st.date_input("End Date*")
                auto_renew = st.checkbox("Auto-renewal")
            
            if st.form_submit_button("Save Contract") and title and vendor:
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
                st.success("Contract added!")
                st.rerun()
    
    contracts = get_filtered_data("contracts")
    if contracts:
        for contract in contracts:
            end_date = datetime.strptime(contract["end_date"], "%Y-%m-%d").date()
            days_left = (end_date - datetime.now().date()).days
            
            if days_left > 30:
                color = "🟢"
                status_text = f"Active - {days_left} days left"
            elif days_left > 0:
                color = "🟡"
                status_text = f"⚠️ Expiring soon - {days_left} days left"
            else:
                color = "🔴"
                status_text = "❌ Expired"
            
            with st.container():
                st.markdown(f"""
                <div style="border:1px solid #ddd; padding:10px; margin:5px 0; border-radius:5px">
                <b>{color} {contract['contract_title']}</b><br>
                Vendor: {contract['vendor_name']}<br>
                {status_text}<br>
                End Date: {contract['end_date']}<br>
                Auto-renewal: {'Yes' if contract['auto_renewal'] else 'No'}
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No contracts found")

def show_policies():
    st.subheader("📋 Policy Monitor")
    
    with st.expander("➕ Add New Policy", expanded=False):
        with st.form("new_policy"):
            policy_name = st.text_input("Policy Name*")
            expiry_date = st.date_input("Expiry Date*")
            is_global = st.checkbox("Global Policy (all departments)")
            
            if st.form_submit_button("Save Policy") and policy_name:
                supabase.table("policies").insert({
                    "policy_name": policy_name,
                    "expiry_date": expiry_date.isoformat(),
                    "department_id": None if is_global else st.session_state.user_dept,
                    "status": "active"
                }).execute()
                st.success("Policy added!")
                st.rerun()
    
    policies = get_filtered_data("policies")
    if policies:
        for policy in policies:
            expiry = datetime.strptime(policy["expiry_date"], "%Y-%m-%d").date()
            days_left = (expiry - datetime.now().date()).days
            
            if days_left > 90:
                alert = "✅ Active"
            elif days_left > 0:
                alert = "⚠️ Expiring soon"
            else:
                alert = "❌ Expired"
            
            st.markdown(f"**{policy['policy_name']}** - Expires: {policy['expiry_date']} - {alert}")
    else:
        st.info("No policies found")

def show_management_view():
    st.subheader("🏢 Enterprise Management View")
    st.warning("You have admin access - viewing ALL departments")
    
    # Get departments mapping
    depts = supabase.table("departments").select("*").execute().data
    dept_names = {d["id"]: d["name"] for d in depts}
    
    tabs = st.tabs(["📋 Action Plans", "📄 Contracts", "📋 Policies"])
    
    with tabs[0]:
        all_plans = supabase.table("action_plans").select("*").execute().data
        if all_plans:
            df = pd.DataFrame(all_plans)
            df["department"] = df["department_id"].map(dept_names)
            st.dataframe(df[["task_name", "department", "status", "progress_percent", "due_date"]], use_container_width=True)
        else:
            st.info("No action plans")
    
    with tabs[1]:
        all_contracts = supabase.table("contracts").select("*").execute().data
        if all_contracts:
            df = pd.DataFrame(all_contracts)
            df["department"] = df["department_id"].map(dept_names)
            st.dataframe(df[["contract_title", "vendor_name", "department", "end_date", "status"]], use_container_width=True)
        else:
            st.info("No contracts")
    
    with tabs[2]:
        all_policies = supabase.table("policies").select("*").execute().data
        if all_policies:
            df = pd.DataFrame(all_policies)
            df["department"] = df["department_id"].map(dept_names).fillna("Global")
            st.dataframe(df[["policy_name", "department", "expiry_date"]], use_container_width=True)
        else:
            st.info("No policies")

if __name__ == "__main__":
    main()
