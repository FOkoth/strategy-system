import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
from supabase import create_client
import bcrypt

# Page config
st.set_page_config(page_title="HELB Strategy System", layout="wide")

# Initialize Supabase
@st.cache_resource
def init_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

# Helper function to hash passwords
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

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
    
    st.title("🔐 HELB Strategy Performance System")
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("### Login")
        with st.form("login_form"):
            username = st.text_input("Username (Email)")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", use_container_width=True)
            
            if submitted:
                try:
                    # Try to login with email
                    result = supabase.table("users").select("*").eq("email", username).execute()
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

# Role-based access control
def check_access(allowed_roles):
    if st.session_state.user_role not in allowed_roles:
        st.error("❌ You don't have permission to access this page")
        return False
    return True

# Fetch data based on role
def get_filtered_data(table_name):
    if st.session_state.user_role in ["admin", "management"]:
        # Management and Admin see everything
        return supabase.table(table_name).select("*").execute().data
    else:
        # Department champions see only their department
        return supabase.table(table_name).select("*").eq("department_id", st.session_state.user_dept).execute().data

# Get department name
def get_department_name(dept_id):
    if dept_id is None:
        return "Global"
    result = supabase.table("departments").select("name").eq("id", dept_id).execute()
    return result.data[0]["name"] if result.data else "Unknown"

# Main app
def main():
    if not check_password():
        return
    
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/150x50?text=HELB", use_column_width=True)
        st.markdown(f"### 👤 {st.session_state.user_name}")
        
        # Show department for non-admin
        if st.session_state.user_role != "admin":
            dept_result = supabase.table("departments").select("name").eq("id", st.session_state.user_dept).execute()
            dept_name = dept_result.data[0]["name"] if dept_result.data else "Unknown"
            st.markdown(f"**Department:** {dept_name}")
        
        st.markdown(f"**Role:** {st.session_state.user_role.upper()}")
        st.markdown("---")
        
        if st.button("🚪 Logout"):
            st.session_state.clear()
            st.rerun()
        
        st.markdown("---")
        
        # Navigation menu
        menu_options = ["Dashboard", "Action Plans", "Contracts", "Policies"]
        
        # Add User Management for Admin only
        if st.session_state.user_role == "admin":
            menu_options.append("👥 User Management")
        
        # Add Management View for Admin and Management
        if st.session_state.user_role in ["admin", "management"]:
            menu_options.append("🏢 Enterprise View")
        
        menu = st.radio("📋 Navigation", menu_options)
    
    st.title("📊 HELB Strategy Performance Management System")
    
    if menu == "Dashboard":
        show_dashboard()
    elif menu == "Action Plans":
        show_action_plans()
    elif menu == "Contracts":
        show_contracts()
    elif menu == "Policies":
        show_policies()
    elif menu == "👥 User Management":
        show_user_management()
    elif menu == "🏢 Enterprise View":
        show_management_view()

def show_dashboard():
    col1, col2, col3, col4 = st.columns(4)
    
    # Get data based on role
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
        col2.metric("Overdue Tasks", overdue, delta="⚠️" if overdue > 0 else None)
    
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
        st.subheader("📈 Department Action Plan Progress")
        df = pd.DataFrame(plans)
        if st.session_state.user_role in ["admin", "management"]:
            # Add department names for management view
            depts = supabase.table("departments").select("id,name").execute().data
            dept_map = {d["id"]: d["name"] for d in depts}
            df["department"] = df["department_id"].map(dept_map)
            fig = px.bar(df, x="task_name", y="progress_percent", color="department", title="Progress by Task")
        else:
            fig = px.bar(df, x="task_name", y="progress_percent", color="status", title="Progress by Task")
        st.plotly_chart(fig, use_container_width=True)
    
    # Welcome message based on role
    if st.session_state.user_role == "admin":
        st.info("👑 **Admin Access:** You can manage users and view all departments")
    elif st.session_state.user_role == "management":
        st.info("📊 **Management Access:** You can view all departments but only edit your own")
    else:
        st.info(f"📋 **Department Champion:** You can manage {get_department_name(st.session_state.user_dept)} department data")

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
            
            # Show department name for management
            if st.session_state.user_role in ["admin", "management"]:
                dept_name = get_department_name(plan["department_id"])
                st.markdown(f"**Department:** {dept_name}")
            
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
            
            # Show department for management
            dept_info = ""
            if st.session_state.user_role in ["admin", "management"]:
                dept_info = f"<br>Department: {get_department_name(contract['department_id'])}"
            
            with st.container():
                st.markdown(f"""
                <div style="border:1px solid #ddd; padding:10px; margin:5px 0; border-radius:5px">
                <b>{color} {contract['contract_title']}</b><br>
                Vendor: {contract['vendor_name']}{dept_info}<br>
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
            
            dept_info = ""
            if policy["department_id"] is None:
                dept_info = " (Global Policy)"
            elif st.session_state.user_role in ["admin", "management"]:
                dept_info = f" ({get_department_name(policy['department_id'])})"
            
            st.markdown(f"**{policy['policy_name']}**{dept_info} - Expires: {policy['expiry_date']} - {alert}")
    else:
        st.info("No policies found")

def show_user_management():
    if not check_access(["admin"]):
        return
    
    st.subheader("👥 User Management")
    st.markdown("### Create New User Account")
    
    # Get departments for dropdown
    depts = supabase.table("departments").select("id,name").execute().data
    dept_options = {d["name"]: d["id"] for d in depts}
    
    with st.form("create_user"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name*")
            email = st.text_input("Email (Username)*")
        with col2:
            role = st.selectbox("Role*", ["department_champion", "management", "admin"])
            department = st.selectbox("Department*", list(dept_options.keys()))
        
        password = st.text_input("Temporary Password*", type="password")
        confirm_password = st.text_input("Confirm Password*", type="password")
        
        if st.form_submit_button("Create User"):
            if password != confirm_password:
                st.error("Passwords don't match")
            elif all([name, email, password]):
                # Check if user exists
                existing = supabase.table("users").select("*").eq("email", email).execute()
                if existing.data:
                    st.error("User with this email already exists")
                else:
                    # Create user
                    hashed = hash_password(password)
                    supabase.table("users").insert({
                        "name": name,
                        "email": email,
                        "password_hash": hashed,
                        "role": role,
                        "department_id": dept_options[department]
                    }).execute()
                    st.success(f"✅ User {name} created successfully!")
                    st.info(f"Email: {email} | Temporary Password: {password}")
                    st.warning("Please share the password securely with the user")
            else:
                st.error("Please fill all required fields")
    
    # Display existing users
    st.markdown("---")
    st.markdown("### Existing Users")
    
    users = supabase.table("users").select("*").execute().data
    if users:
        user_data = []
        for user in users:
            dept_name = get_department_name(user["department_id"]) if user["department_id"] else "N/A"
            user_data.append({
                "Name": user["name"],
                "Email": user["email"],
                "Role": user["role"],
                "Department": dept_name
            })
        
        df = pd.DataFrame(user_data)
        st.dataframe(df, use_container_width=True)
        
        # Delete user option
        st.markdown("### Delete User")
        user_to_delete = st.selectbox("Select user to delete", [f"{u['name']} ({u['email']})" for u in users if u["email"] != "admin@company.com"])
        if st.button("Delete User", type="secondary"):
            email_to_delete = user_to_delete.split("(")[1].rstrip(")")
            supabase.table("users").delete().eq("email", email_to_delete).execute()
            st.success("User deleted!")
            st.rerun()

def show_management_view():
    if not check_access(["admin", "management"]):
        return
    
    st.subheader("🏢 Enterprise Management View")
    st.markdown("### Cross-Department Performance Overview")
    
    # Get departments
    depts = supabase.table("departments").select("*").execute().data
    dept_names = {d["id"]: d["name"] for d in depts}
    
    # Department performance summary
    st.markdown("#### Department Performance Summary")
    
    performance_data = []
    for dept in depts:
        plans = supabase.table("action_plans").select("*").eq("department_id", dept["id"]).execute().data
        if plans:
            avg_progress = sum(p.get("progress_percent", 0) for p in plans) / len(plans)
            completed = sum(1 for p in plans if p.get("status") == "completed")
            performance_data.append({
                "Department": dept["name"],
                "Total Tasks": len(plans),
                "Completed": completed,
                "Avg Progress %": f"{avg_progress:.0f}%"
            })
        else:
            performance_data.append({
                "Department": dept["name"],
                "Total Tasks": 0,
                "Completed": 0,
                "Avg Progress %": "N/A"
            })
    
    if performance_data:
        df = pd.DataFrame(performance_data)
        st.dataframe(df, use_container_width=True)
    
    tabs = st.tabs(["📋 All Action Plans", "📄 All Contracts", "📋 All Policies"])
    
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
