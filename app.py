import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import base64
from io import BytesIO
import requests
import re
import json

# ============================================
# HELB BRANDING CONFIGURATION
# ============================================
HELB_GREEN = "#00843D"
HELB_GOLD = "#FFB81C"
HELB_BLUE = "#00529B"
HELB_DARK = "#1F2937"
HELB_WHITE = "#FFFFFF"
HELB_GRAY = "#F9FAFB"
HELB_BLACK = "#000000"

# ============================================
# THEME MANAGEMENT
# ============================================
if "theme" not in st.session_state:
    st.session_state.theme = "light"

def toggle_theme():
    if st.session_state.theme == "light":
        st.session_state.theme = "dark"
    else:
        st.session_state.theme = "light"
    st.rerun()

st.set_page_config(
    page_title="HELB Strategy Performance System",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# LOAD HELB LOGO
# ============================================
@st.cache_data(ttl=3600)
def get_logo_base64():
    try:
        logo_url = st.secrets.get("HELB_LOGO_URL", "https://raw.githubusercontent.com/YOUR_USERNAME/strategy-system/main/HELB%20Logo.png")
        response = requests.get(logo_url, timeout=10)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            transparent = Image.new('RGBA', img.size, (0, 0, 0, 0))
            transparent.paste(img, (0, 0), img)
            buffered = BytesIO()
            transparent.save(buffered, format="PNG")
            return base64.b64encode(buffered.getvalue()).decode()
    except:
        pass
    
    try:
        with open("HELB Logo.png", "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return None

LOGO_BASE64 = get_logo_base64()

# ============================================
# CONSTANTS
# ============================================
STRATEGIC_PILLARS = [
    "1. Customer Excellence",
    "2. Financial Sustainability and Stewardship",
    "3. Innovation & Digital Transformation",
    "4. Our People Centricity and Compliance",
    "5. Strategy"
]

ACTIVITY_CATEGORIES = ["SP Deliverable", "PC Deliverable"]

POLICY_CATEGORIES = [
    "HR", "Finance", "ICT", "Operations", 
    "Governance", "Compliance", "Risk Management", 
    "Procurement", "Legal", "Other"
]

POLICY_SCOPE = ["Institution-Wide", "Department-Specific", "Committee"]

# Payment terms with descriptions
PAYMENT_TERMS = [
    "Monthly Retainer",
    "Quarterly Retainer", 
    "Bi-annually",
    "Annually",
    "Milestone-based",
    "One-time Payment"
]

QUARTER_MONTHS = {
    "Q1 (Jul-Sep)": ["July", "August", "September"],
    "Q2 (Oct-Dec)": ["October", "November", "December"],
    "Q3 (Jan-Mar)": ["January", "February", "March"],
    "Q4 (Apr-Jun)": ["April", "May", "June"]
}

ALL_MONTHS = ["January", "February", "March", "April", "May", "June", 
              "July", "August", "September", "October", "November", "December"]

def get_financial_years():
    current_year = datetime.now().year
    years = []
    for i in range(-2, 3):
        start_year = current_year + i
        years.append(f"{start_year}/{start_year + 1}")
    return years

def get_quarter_from_month(month):
    if month in [7, 8, 9]:
        return "Q1 (Jul-Sep)"
    elif month in [10, 11, 12]:
        return "Q2 (Oct-Dec)"
    elif month in [1, 2, 3]:
        return "Q3 (Jan-Mar)"
    else:
        return "Q4 (Apr-Jun)"

def get_months_for_quarter(quarter):
    if quarter == "All":
        return ALL_MONTHS
    return QUARTER_MONTHS.get(quarter, ALL_MONTHS)

# ============================================
# SESSION STATE FOR FILTERS
# ============================================
if "filter_financial_year" not in st.session_state:
    st.session_state.filter_financial_year = "All"
if "filter_quarter" not in st.session_state:
    st.session_state.filter_quarter = "All"
if "filter_month" not in st.session_state:
    st.session_state.filter_month = "All"

# ============================================
# HELPER FUNCTIONS
# ============================================
def calculate_progress_from_actual(annual_target, actual_achievement):
    if not annual_target or actual_achievement is None:
        return 0
    try:
        target_match = re.search(r'[\d.]+', str(annual_target))
        if not target_match:
            return 0
        target_num = float(target_match.group())
        actual_num = float(actual_achievement) if actual_achievement else 0
        if target_num == 0:
            return 0
        progress = (actual_num / target_num) * 100
        return min(progress, 100)
    except:
        return 0

def is_target_exceeded(actual_achievement, annual_target):
    if not actual_achievement or not annual_target:
        return False
    try:
        target_match = re.search(r'[\d.]+', str(annual_target))
        if not target_match:
            return False
        target_num = float(target_match.group())
        actual_num = float(actual_achievement) if actual_achievement else 0
        return actual_num > target_num
    except:
        return False

def filter_work_plans_by_date(df, financial_year, quarter, month):
    if df.empty:
        return df
    
    df = df.copy()
    df['due_date_dt'] = pd.to_datetime(df['due_date'])
    df['due_month'] = df['due_date_dt'].dt.month
    df['due_year'] = df['due_date_dt'].dt.year
    
    if financial_year and financial_year != "All":
        start_year = int(financial_year.split('/')[0])
        end_year = int(financial_year.split('/')[1])
        mask = ((df['due_year'] == start_year) & (df['due_month'] >= 7)) | \
               ((df['due_year'] == end_year) & (df['due_month'] <= 6))
        df = df[mask]
    
    if quarter and quarter != "All":
        if quarter == "Q1 (Jul-Sep)":
            df = df[df['due_month'].isin([7, 8, 9])]
        elif quarter == "Q2 (Oct-Dec)":
            df = df[df['due_month'].isin([10, 11, 12])]
        elif quarter == "Q3 (Jan-Mar)":
            df = df[df['due_month'].isin([1, 2, 3])]
        elif quarter == "Q4 (Apr-Jun)":
            df = df[df['due_month'].isin([4, 5, 6])]
    
    if month and month != "All":
        month_num = {
            "January": 1, "February": 2, "March": 3, "April": 4,
            "May": 5, "June": 6, "July": 7, "August": 8,
            "September": 9, "October": 10, "November": 11, "December": 12
        }.get(month, 0)
        if month_num:
            df = df[df['due_month'] == month_num]
    
    return df

def filter_contracts_by_date(df, financial_year, quarter, month):
    if df.empty:
        return df
    
    df = df.copy()
    df['end_date_dt'] = pd.to_datetime(df['end_date'])
    df['end_month'] = df['end_date_dt'].dt.month
    df['end_year'] = df['end_date_dt'].dt.year
    
    if financial_year and financial_year != "All":
        start_year = int(financial_year.split('/')[0])
        end_year = int(financial_year.split('/')[1])
        mask = ((df['end_year'] == start_year) & (df['end_month'] >= 7)) | \
               ((df['end_year'] == end_year) & (df['end_month'] <= 6))
        df = df[mask]
    
    if quarter and quarter != "All":
        if quarter == "Q1 (Jul-Sep)":
            df = df[df['end_month'].isin([7, 8, 9])]
        elif quarter == "Q2 (Oct-Dec)":
            df = df[df['end_month'].isin([10, 11, 12])]
        elif quarter == "Q3 (Jan-Mar)":
            df = df[df['end_month'].isin([1, 2, 3])]
        elif quarter == "Q4 (Apr-Jun)":
            df = df[df['end_month'].isin([4, 5, 6])]
    
    if month and month != "All":
        month_num = {
            "January": 1, "February": 2, "March": 3, "April": 4,
            "May": 5, "June": 6, "July": 7, "August": 8,
            "September": 9, "October": 10, "November": 11, "December": 12
        }.get(month, 0)
        if month_num:
            df = df[df['end_month'] == month_num]
    
    return df

def filter_policies_by_date(df, financial_year, quarter, month):
    if df.empty:
        return df
    
    df = df.copy()
    df['expiry_date_dt'] = pd.to_datetime(df['expiry_date'])
    df['expiry_month'] = df['expiry_date_dt'].dt.month
    df['expiry_year'] = df['expiry_date_dt'].dt.year
    
    if financial_year and financial_year != "All":
        start_year = int(financial_year.split('/')[0])
        end_year = int(financial_year.split('/')[1])
        mask = ((df['expiry_year'] == start_year) & (df['expiry_month'] >= 7)) | \
               ((df['expiry_year'] == end_year) & (df['expiry_month'] <= 6))
        df = df[mask]
    
    if quarter and quarter != "All":
        if quarter == "Q1 (Jul-Sep)":
            df = df[df['expiry_month'].isin([7, 8, 9])]
        elif quarter == "Q2 (Oct-Dec)":
            df = df[df['expiry_month'].isin([10, 11, 12])]
        elif quarter == "Q3 (Jan-Mar)":
            df = df[df['expiry_month'].isin([1, 2, 3])]
        elif quarter == "Q4 (Apr-Jun)":
            df = df[df['expiry_month'].isin([4, 5, 6])]
    
    if month and month != "All":
        month_num = {
            "January": 1, "February": 2, "March": 3, "April": 4,
            "May": 5, "June": 6, "July": 7, "August": 8,
            "September": 9, "October": 10, "November": 11, "December": 12
        }.get(month, 0)
        if month_num:
            df = df[df['expiry_month'] == month_num]
    
    return df

# ============================================
# DATABASE FUNCTIONS
# ============================================
@st.cache_resource
def init_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

# ============================================
# AUDIT LOG FUNCTIONS
# ============================================
def add_audit_log(action, entity_type, entity_id, details):
    try:
        audit_data = {
            "user_id": st.session_state.user_id,
            "username": st.session_state.user_name,
            "action": action,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "details": details,
            "ip_address": "web_app",
            "created_at": datetime.now().isoformat()
        }
        supabase.table("audit_logs").insert(audit_data).execute()
    except Exception as e:
        print(f"Audit log error: {e}")

def get_audit_logs(limit=500):
    try:
        result = supabase.table("audit_logs").select("*").order("created_at", desc=True).limit(limit).execute()
        return result.data
    except:
        return []

# ============================================
# DIRECTORATE FUNCTIONS
# ============================================
@st.cache_data(ttl=3600)
def get_cached_directorates():
    try:
        result = supabase.table("directorates").select("*").order("name").execute()
        return result.data
    except:
        return []

def get_all_directorates():
    return get_cached_directorates()

def get_directorate_by_id(directorate_id):
    if not directorate_id:
        return None
    directorates = get_cached_directorates()
    for d in directorates:
        if d["id"] == directorate_id:
            return d
    return None

def get_directorate_for_department(department_id):
    if not department_id:
        return None
    dept = get_department_by_id(department_id)
    if dept and dept.get("directorate_name"):
        return dept["directorate_name"]
    return None

def add_directorate(name, director_name):
    try:
        supabase.table("directorates").insert({"name": name, "director_name": director_name}).execute()
        st.cache_data.clear()
        add_audit_log("CREATE", "directorate", None, f"Added directorate: {name}")
        return True, "Directorate added successfully"
    except Exception as e:
        return False, str(e)

def update_directorate(directorate_id, name, director_name):
    try:
        supabase.table("directorates").update({
            "name": name, 
            "director_name": director_name,
            "updated_at": datetime.now().isoformat()
        }).eq("id", directorate_id).execute()
        st.cache_data.clear()
        add_audit_log("UPDATE", "directorate", directorate_id, f"Updated directorate: {name}")
        return True, "Directorate updated successfully"
    except Exception as e:
        return False, str(e)

def delete_directorate(directorate_id):
    try:
        depts = supabase.table("departments").select("id").eq("directorate_id", directorate_id).execute()
        if depts.data:
            return False, "Cannot delete directorate that has departments. Move departments first."
        supabase.table("directorates").delete().eq("id", directorate_id).execute()
        st.cache_data.clear()
        add_audit_log("DELETE", "directorate", directorate_id, f"Deleted directorate ID: {directorate_id}")
        return True, "Directorate deleted successfully"
    except Exception as e:
        return False, str(e)

# ============================================
# DEPARTMENT FUNCTIONS
# ============================================
@st.cache_data(ttl=3600)
def get_cached_departments():
    try:
        result = supabase.table("departments").select("*").order("name").execute()
        depts = result.data
        dir_result = supabase.table("directorates").select("*").execute()
        directorates = {d["id"]: d for d in dir_result.data}
        
        for dept in depts:
            if dept.get("directorate_id") and dept["directorate_id"] in directorates:
                dept["directorate_name"] = directorates[dept["directorate_id"]]["name"]
                dept["director_name"] = directorates[dept["directorate_id"]]["director_name"]
        return depts
    except:
        return []

def get_all_departments():
    return get_cached_departments()

def get_department_by_id(dept_id):
    if not dept_id:
        return None
    departments = get_cached_departments()
    for d in departments:
        if d["id"] == dept_id:
            return d
    return None

def add_department(dept_name, directorate_id, deputy_director_name):
    try:
        supabase.table("departments").insert({
            "name": dept_name, 
            "directorate_id": directorate_id if directorate_id else None,
            "deputy_director_name": deputy_director_name
        }).execute()
        st.cache_data.clear()
        add_audit_log("CREATE", "department", None, f"Added department: {dept_name}")
        return True, "Department added successfully"
    except Exception as e:
        return False, str(e)

def update_department(dept_id, name, directorate_id, deputy_director_name):
    try:
        supabase.table("departments").update({
            "name": name,
            "directorate_id": directorate_id if directorate_id else None,
            "deputy_director_name": deputy_director_name,
            "updated_at": datetime.now().isoformat()
        }).eq("id", dept_id).execute()
        st.cache_data.clear()
        add_audit_log("UPDATE", "department", dept_id, f"Updated department: {name}")
        return True, "Department updated successfully"
    except Exception as e:
        return False, str(e)

def delete_department(dept_id):
    try:
        users = supabase.table("users").select("id").eq("department_id", dept_id).execute()
        if users.data:
            return False, "Cannot delete department that has users. Reassign users first."
        supabase.table("departments").delete().eq("id", dept_id).execute()
        st.cache_data.clear()
        add_audit_log("DELETE", "department", dept_id, f"Deleted department ID: {dept_id}")
        return True, "Department deleted successfully"
    except Exception as e:
        return False, str(e)

def get_department_name(dept_id):
    if dept_id is None:
        return "No Department"
    dept = get_department_by_id(dept_id)
    return dept["name"] if dept else "Unknown Department"

# ============================================
# WORK PLAN FUNCTIONS
# ============================================
@st.cache_data(ttl=60)
def get_cached_work_plans(user_role, user_dept):
    try:
        if user_role in ["admin", "management"]:
            result = supabase.table("work_plan").select("*").order("created_at", desc=True).execute()
        else:
            result = supabase.table("work_plan").select("*").eq("department_id", user_dept).order("created_at", desc=True).execute()
        return result.data
    except:
        return []

@st.cache_data(ttl=60)
def get_cached_contracts(user_role, user_dept):
    try:
        if user_role in ["admin", "management"]:
            result = supabase.table("contracts").select("*").execute()
        else:
            result = supabase.table("contracts").select("*").eq("department_id", user_dept).execute()
        return result.data
    except:
        return []

@st.cache_data(ttl=60)
def get_cached_policies(user_role, user_dept):
    try:
        if user_role in ["admin", "management"]:
            result = supabase.table("policies").select("*").execute()
        else:
            result = supabase.table("policies").select("*").eq("department_id", user_dept).execute()
        return result.data
    except:
        return []

def get_work_plans():
    return get_cached_work_plans(st.session_state.user_role, st.session_state.user_dept)

def add_work_plan(data):
    try:
        supabase.table("work_plan").insert(data).execute()
        st.cache_data.clear()
        add_audit_log("CREATE", "work_plan", None, f"Added work plan: {data.get('planned_activity', '')[:50]}")
        return True
    except:
        return False

def update_work_plan_progress(plan_id, actual_achievement, progress_percent, status):
    try:
        progress_int = int(progress_percent) if progress_percent else 0
        
        update_data = {
            "actual_achievement": float(actual_achievement) if actual_achievement else 0,
            "progress_percent": progress_int,
            "status": status,
            "updated_at": datetime.now().isoformat()
        }
        supabase.table("work_plan").update(update_data).eq("id", plan_id).execute()
        st.cache_data.clear()
        add_audit_log("UPDATE", "work_plan", plan_id, f"Updated progress to {progress_percent}%")
        return True
    except Exception as e:
        st.error(f"Update error: {e}")
        return False

def update_work_plan_due_date(plan_id, new_due_date):
    try:
        update_data = {
            "due_date": new_due_date.isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        supabase.table("work_plan").update(update_data).eq("id", plan_id).execute()
        st.cache_data.clear()
        add_audit_log("UPDATE", "work_plan", plan_id, f"Updated due date to {new_due_date}")
        return True
    except:
        return False

def delete_work_plan(plan_id):
    try:
        supabase.table("work_plan").delete().eq("id", plan_id).execute()
        st.cache_data.clear()
        add_audit_log("DELETE", "work_plan", plan_id, "Deleted work plan")
        return True
    except:
        return False

def update_work_plan_admin(plan_id, data):
    try:
        supabase.table("work_plan").update(data).eq("id", plan_id).execute()
        st.cache_data.clear()
        add_audit_log("UPDATE", "work_plan", plan_id, "Admin updated work plan")
        return True
    except Exception as e:
        return False

# ============================================
# CONTRACT YEAR FUNCTIONS
# ============================================
def get_contract_years(contract_id):
    try:
        result = supabase.table("contract_years").select("*").eq("contract_id", contract_id).order("year_number").execute()
        return result.data
    except:
        return []

def add_multi_year_contract(contract_data, years_data):
    try:
        result = supabase.table("contracts").insert(contract_data).execute()
        if not result.data:
            return False, "Failed to create contract"
        
        contract_id = result.data[0]['id']
        
        for year_data in years_data:
            year_data['contract_id'] = contract_id
            supabase.table("contract_years").insert(year_data).execute()
        
        st.cache_data.clear()
        add_audit_log("CREATE", "contract", contract_id, f"Added multi-year contract with {len(years_data)} years")
        return True, f"Contract added successfully with {len(years_data)} years"
    except Exception as e:
        return False, str(e)

def update_contract_year_spending(year_id, amount_spent):
    try:
        result = supabase.table("contract_years").select("*").eq("id", year_id).execute()
        if not result.data:
            return False
        
        year = result.data[0]
        annual_value = year.get("annual_value", 0)
        utilization_rate = (amount_spent / annual_value * 100) if annual_value > 0 else 0
        budget_alert = utilization_rate >= 80
        
        supabase.table("contract_years").update({
            "amount_spent_to_date": amount_spent,
            "utilization_rate": utilization_rate,
            "budget_alert": budget_alert,
            "updated_at": datetime.now().isoformat()
        }).eq("id", year_id).execute()
        
        all_years = get_contract_years(year['contract_id'])
        total_spent = sum(y.get('amount_spent_to_date', 0) for y in all_years)
        
        supabase.table("contracts").update({
            "amount_spent_to_date": total_spent,
            "updated_at": datetime.now().isoformat()
        }).eq("id", year['contract_id']).execute()
        
        st.cache_data.clear()
        return True
    except Exception as e:
        return False

# ============================================
# ENHANCED CONTRACT FUNCTIONS
# ============================================
def add_enhanced_contract(data):
    try:
        end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").date()
        days_left = (end_date - datetime.now().date()).days
        
        if days_left < 0:
            status = "expired"
        elif days_left <= 30:
            status = "expiring_soon"
        else:
            status = "active"
        
        contract_value = data.get("contract_value", 0)
        amount_spent = data.get("amount_spent_to_date", 0)
        utilization_rate = (amount_spent / contract_value * 100) if contract_value > 0 else 0
        
        if utilization_rate >= 80:
            data["budget_alert"] = True
        else:
            data["budget_alert"] = False
        
        data["days_remaining"] = days_left
        data["status"] = status
        data["utilization_rate"] = utilization_rate
        
        supabase.table("contracts").insert(data).execute()
        st.cache_data.clear()
        add_audit_log("CREATE", "contract", None, f"Added contract: {data.get('contract_title', '')}")
        return True, "Contract added successfully"
    except Exception as e:
        return False, str(e)

def update_contract_spending(contract_id, amount_spent):
    try:
        result = supabase.table("contracts").select("*").eq("id", contract_id).execute()
        if not result.data:
            return False
        
        contract = result.data[0]
        contract_value = contract.get("contract_value", 0)
        
        utilization_rate = (amount_spent / contract_value * 100) if contract_value > 0 else 0
        budget_alert = utilization_rate >= 80
        
        supabase.table("contracts").update({
            "amount_spent_to_date": amount_spent,
            "utilization_rate": utilization_rate,
            "budget_alert": budget_alert,
            "updated_at": datetime.now().isoformat()
        }).eq("id", contract_id).execute()
        
        st.cache_data.clear()
        add_audit_log("UPDATE", "contract", contract_id, f"Updated spending to {amount_spent}")
        return True
    except Exception as e:
        return False

def update_vendor_performance(contract_id, performance_rating, compliance_status, breach_notes=None):
    try:
        update_data = {
            "vendor_performance": performance_rating,
            "compliance_status": compliance_status,
            "updated_at": datetime.now().isoformat()
        }
        if breach_notes:
            update_data["breach_notes"] = breach_notes
        
        supabase.table("contracts").update(update_data).eq("id", contract_id).execute()
        st.cache_data.clear()
        add_audit_log("UPDATE", "contract", contract_id, f"Updated vendor performance to {performance_rating}")
        return True
    except Exception as e:
        return False

def update_contract_user(contract_id, data):
    try:
        supabase.table("contracts").update(data).eq("id", contract_id).execute()
        st.cache_data.clear()
        add_audit_log("UPDATE", "contract", contract_id, "User updated contract")
        return True
    except Exception as e:
        return False

def update_contract_admin(contract_id, data):
    try:
        supabase.table("contracts").update(data).eq("id", contract_id).execute()
        st.cache_data.clear()
        add_audit_log("UPDATE", "contract", contract_id, "Admin updated contract")
        return True
    except Exception as e:
        return False

def delete_contract(contract_id):
    try:
        supabase.table("contract_years").delete().eq("contract_id", contract_id).execute()
        supabase.table("contracts").delete().eq("id", contract_id).execute()
        st.cache_data.clear()
        add_audit_log("DELETE", "contract", contract_id, "Deleted contract")
        return True
    except:
        return False

# ============================================
# ENHANCED POLICY FUNCTIONS
# ============================================
def add_enhanced_policy(data):
    try:
        expiry_date = datetime.strptime(data["expiry_date"], "%Y-%m-%d").date()
        days_left = (expiry_date - datetime.now().date()).days
        
        if days_left < 0:
            status = "expired"
        elif days_left <= 90:
            status = "expiring_soon"
        else:
            status = "active"
        
        data["days_remaining"] = days_left
        data["status"] = status
        
        supabase.table("policies").insert(data).execute()
        st.cache_data.clear()
        add_audit_log("CREATE", "policy", None, f"Added policy: {data.get('policy_name', '')}")
        return True, "Policy added successfully"
    except Exception as e:
        return False, str(e)

def update_policy_admin(policy_id, data):
    try:
        supabase.table("policies").update(data).eq("id", policy_id).execute()
        st.cache_data.clear()
        add_audit_log("UPDATE", "policy", policy_id, "Admin updated policy")
        return True
    except Exception as e:
        return False

def delete_policy(policy_id):
    try:
        supabase.table("policy_acknowledgments").delete().eq("policy_id", policy_id).execute()
        supabase.table("policies").delete().eq("id", policy_id).execute()
        st.cache_data.clear()
        add_audit_log("DELETE", "policy", policy_id, "Deleted policy")
        return True
    except:
        return False

def get_policy_acknowledgments(policy_id):
    try:
        result = supabase.table("policy_acknowledgments").select("*")\
            .eq("policy_id", policy_id).execute()
        return result.data
    except:
        return []

# ============================================
# USER MANAGEMENT FUNCTIONS
# ============================================
def get_all_users():
    try:
        result = supabase.table("users").select("*").execute()
        return result.data
    except:
        return []

def delete_user(username):
    try:
        supabase.table("users").delete().eq("username", username).execute()
        st.cache_data.clear()
        add_audit_log("DELETE", "user", None, f"Deleted user: {username}")
        return True
    except:
        return False

def update_user_role(username, new_role, department_id):
    try:
        supabase.table("users").update({
            "role": new_role,
            "department_id": department_id if department_id != "None" else None
        }).eq("username", username).execute()
        st.cache_data.clear()
        add_audit_log("UPDATE", "user", None, f"Updated user {username} role to {new_role}")
        return True
    except:
        return False

def reset_user_password(username, new_password):
    try:
        supabase.table("users").update({
            "password_hash": new_password
        }).eq("username", username).execute()
        st.cache_data.clear()
        add_audit_log("UPDATE", "user", None, f"Reset password for user: {username}")
        return True
    except:
        return False

def create_new_user(username, full_name, password, role, department_id):
    try:
        existing = supabase.table("users").select("*").eq("username", username.lower()).execute()
        if existing.data:
            return False, "Username already exists"
        
        supabase.table("users").insert({
            "username": username.lower(),
            "full_name": full_name,
            "password_hash": password,
            "role": role,
            "department_id": department_id if department_id != "None" else None
        }).execute()
        st.cache_data.clear()
        add_audit_log("CREATE", "user", None, f"Created user: {username}")
        return True, "User created successfully"
    except Exception as e:
        return False, str(e)

# ============================================
# SESSION STATE INITIALIZATION
# ============================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.user_role = None
    st.session_state.user_dept = None
    st.session_state.user_name = None
    st.session_state.user_fullname = None
    st.session_state.user_id = None
    st.session_state.user_dept_name = ""

# ============================================
# CUSTOM CSS - FIXED
# ============================================
if st.session_state.theme == "light":
    THEME_CSS = f"""
    <style>
        /* Main app styling */
        .stApp {{
            background-color: {HELB_WHITE};
        }}
        
        /* Headers */
        h1, h2, h3, h4, h5, h6 {{
            color: {HELB_GREEN} !important;
        }}
        
        /* Login page styling */
        .login-wrapper {{
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 80vh;
        }}
        .login-box {{
            background: linear-gradient(135deg, {HELB_GREEN} 0%, {HELB_BLUE} 100%);
            border-radius: 20px;
            padding: 2.5rem;
            text-align: center;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            max-width: 450px;
            margin: 0 auto;
        }}
        .login-logo {{
            margin-bottom: 1.5rem;
        }}
        .login-title {{
            color: white !important;
            font-size: 1.8rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }}
        .login-subtitle {{
            color: {HELB_GOLD} !important;
            font-size: 0.9rem;
            margin-bottom: 2rem;
        }}
        
        /* KPI Cards */
        .kpi-card {{
            background: linear-gradient(135deg, {HELB_GREEN} 0%, {HELB_BLUE} 100%) !important;
            border-radius: 12px !important;
            padding: 1rem !important;
            text-align: center !important;
        }}
        .kpi-card .kpi-label {{
            font-size: 0.7rem !important;
            text-transform: uppercase !important;
            color: {HELB_GOLD} !important;
            font-weight: 600 !important;
            letter-spacing: 0.5px !important;
        }}
        .kpi-card .kpi-value {{
            font-size: 1.5rem !important;
            font-weight: 700 !important;
            margin: 0.2rem 0 !important;
            color: #FFFFFF !important;
        }}
        .kpi-card .kpi-sub {{
            font-size: 0.55rem !important;
            color: #FFFFFF !important;
            margin-top: 0.2rem !important;
            opacity: 0.9 !important;
        }}
        
        /* Contract and Policy Cards */
        .contract-card, .policy-card {{
            background: #ffffff !important;
            border: 1px solid #e5e7eb !important;
            border-radius: 12px !important;
            padding: 1rem !important;
            margin-bottom: 0.75rem !important;
            transition: all 0.2s ease !important;
        }}
        .contract-card:hover, .policy-card:hover {{
            box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
        }}
        .contract-title, .policy-title {{
            font-size: 1rem !important;
            font-weight: 700 !important;
            color: {HELB_GREEN} !important;
            margin-bottom: 0.5rem !important;
        }}
        .contract-detail, .policy-detail {{
            font-size: 0.75rem !important;
            color: #4b5563 !important;
            margin: 0.25rem 0 !important;
        }}
        .status-badge {{
            display: inline-block !important;
            padding: 0.2rem 0.6rem !important;
            border-radius: 20px !important;
            font-size: 0.7rem !important;
            font-weight: 600 !important;
        }}
        .status-active {{ background-color: #10b981 !important; color: white !important; }}
        .status-expiring {{ background-color: #f59e0b !important; color: white !important; }}
        .status-expired {{ background-color: #ef4444 !important; color: white !important; }}
        
        /* Sidebar */
        [data-testid="stSidebar"] {{ 
            background: linear-gradient(180deg, {HELB_GREEN} 0%, {HELB_BLUE} 100%) !important;
            padding-top: 1rem; 
        }}
        [data-testid="stSidebar"] * {{ color: white !important; }}
        
        .sidebar-user-info {{
            background: rgba(255,255,255,0.15);
            padding: 0.8rem;
            border-radius: 10px;
            margin: 0.5rem 0;
            text-align: center;
        }}
        
        /* Buttons */
        .stButton > button {{
            background: linear-gradient(135deg, {HELB_GREEN} 0%, {HELB_BLUE} 100%) !important;
            color: white !important;
            border-radius: 8px !important;
            padding: 8px 16px !important;
            font-weight: 600 !important;
            border: none !important;
        }}
        
        .stButton > button:hover {{
            opacity: 0.9 !important;
        }}
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            background: {HELB_GRAY};
            padding: 0.3rem;
            border-radius: 10px;
            gap: 0.3rem;
        }}
        .stTabs [data-baseweb="tab"] {{
            font-size: 0.75rem;
            padding: 0.3rem 1rem;
            color: #000000 !important;
        }}
        .stTabs [aria-selected="true"] {{
            background-color: {HELB_GOLD} !important;
            color: #1F2937 !important;
        }}
        
        /* Footer */
        .footer {{
            text-align: center;
            padding: 1rem;
            color: #6B7280;
            font-size: 0.6rem;
            border-top: 1px solid #E5E7EB;
            margin-top: 1.5rem;
        }}
        
        /* Dashboard Header */
        .dashboard-header {{
            background: linear-gradient(135deg, {HELB_GREEN} 0%, {HELB_BLUE} 100%);
            padding: 0.8rem 1.5rem;
            border-radius: 12px;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .dashboard-header h1 {{ color: white !important; margin: 0; font-size: 1.2rem; border-bottom: none; }}
        .dashboard-header p {{ color: {HELB_GOLD} !important; margin: 0; font-size: 0.7rem; font-weight: 500; }}
        
        /* Input fields */
        .stTextInput input, .stSelectbox div, .stDateInput input, 
        .stNumberInput input, .stTextArea textarea {{
            background-color: white !important;
            color: #000000 !important;
            border: 1px solid #D1D5DB !important;
            border-radius: 8px !important;
        }}
        
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        .stAppDeployButton {{display: none;}}
        
        .dataframe th {{ background-color: {HELB_GREEN} !important; color: white !important; font-size: 0.7rem; }}
        .dataframe td {{ color: #000000 !important; font-size: 0.7rem; }}
    </style>
    """
else:
    THEME_CSS = f"""
    <style>
        .stApp {{ background-color: #1a1a2e !important; }}
        
        h1, h2, h3, h4, h5, h6 {{ color: {HELB_GOLD} !important; }}
        
        .login-box {{
            background: linear-gradient(135deg, #0f3460 0%, #16213e 100%);
            border-radius: 20px;
            padding: 2.5rem;
            text-align: center;
            box-shadow: 0 20px 40px rgba(0,0,0,0.3);
            max-width: 450px;
            margin: 0 auto;
        }}
        .login-title {{ color: white !important; }}
        .login-subtitle {{ color: {HELB_GOLD} !important; }}
        
        .kpi-card {{
            background: linear-gradient(135deg, #0f3460 0%, #16213e 100%) !important;
            border-radius: 12px !important;
            padding: 1rem !important;
            text-align: center !important;
        }}
        .kpi-card .kpi-label {{ color: {HELB_GOLD} !important; }}
        .kpi-card .kpi-value {{ color: #FFFFFF !important; }}
        .kpi-card .kpi-sub {{ color: #FFFFFF !important; }}
        
        .contract-card, .policy-card {{
            background: #1e293b !important;
            border: 1px solid #334155 !important;
            border-radius: 12px !important;
            padding: 1rem !important;
            margin-bottom: 0.75rem !important;
        }}
        .contract-title, .policy-title {{ color: {HELB_GOLD} !important; }}
        .contract-detail, .policy-detail {{ color: #cbd5e1 !important; }}
        
        [data-testid="stSidebar"] {{ background: linear-gradient(180deg, #0f3460 0%, #16213e 100%) !important; }}
        [data-testid="stSidebar"] * {{ color: white !important; }}
        
        .stButton > button {{
            background: linear-gradient(135deg, #0f3460 0%, #16213e 100%) !important;
            color: white !important;
            border-radius: 8px !important;
            padding: 8px 16px !important;
            font-weight: 600 !important;
        }}
        
        .stTabs [data-baseweb="tab-list"] {{ background: #2d2d44; }}
        .stTabs [data-baseweb="tab"] {{ color: #FFFFFF !important; }}
        .stTabs [aria-selected="true"] {{ background-color: {HELB_GOLD} !important; color: #1F2937 !important; }}
        
        .dashboard-header {{
            background: linear-gradient(135deg, #0f3460 0%, #16213e 100%);
            padding: 0.8rem 1.5rem;
            border-radius: 12px;
            margin-bottom: 1.5rem;
        }}
        .dashboard-header h1 {{ color: white !important; }}
        .dashboard-header p {{ color: {HELB_GOLD} !important; }}
        
        .footer {{ color: #6B7280; border-top: 1px solid #2d2d44; }}
        
        .stTextInput input, .stSelectbox div, .stDateInput input, 
        .stNumberInput input, .stTextArea textarea {{
            background-color: #2d2d44 !important;
            color: #FFFFFF !important;
            border: 1px solid #4a4a6a !important;
        }}
        
        .dataframe th {{ background-color: {HELB_GREEN} !important; color: white !important; }}
        .dataframe td {{ color: #FFFFFF !important; }}
    </style>
    """

st.markdown(THEME_CSS, unsafe_allow_html=True)

# ============================================
# ENHANCED LOGIN PAGE
# ============================================
if not st.session_state.authenticated:
    st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Logo display
        if LOGO_BASE64:
            logo_html = f'<div class="login-logo"><img src="data:image/png;base64,{LOGO_BASE64}" style="width: 180px; height: auto;"></div>'
        else:
            logo_html = '<div class="login-logo" style="font-size: 4rem;">🏦</div>'
        
        st.markdown(f"""
        <div class="login-box">
            {logo_html}
            <h1 class="login-title">HIGHER EDUCATION LOANS BOARD</h1>
            <p class="login-subtitle">Strategy Performance Management System</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username", key="login_username")
            password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_password")
            
            col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
            with col_btn2:
                submitted = st.form_submit_button("🔐 Login", use_container_width=True)
            
            if submitted:
                if username and password:
                    result = supabase.table("users").select("*").eq("username", username.lower()).execute()
                    if result.data:
                        user = result.data[0]
                        if password == user["password_hash"]:
                            dept_name = get_department_name(user["department_id"])
                            
                            st.session_state.authenticated = True
                            st.session_state.user = user
                            st.session_state.user_role = user["role"]
                            st.session_state.user_dept = user["department_id"]
                            st.session_state.user_name = user["username"]
                            st.session_state.user_fullname = user["full_name"]
                            st.session_state.user_id = user["id"]
                            st.session_state.user_dept_name = dept_name
                            add_audit_log("LOGIN", "session", None, f"User logged in")
                            st.rerun()
                        else:
                            st.error("❌ Invalid password")
                    else:
                        st.error("❌ User not found")
                else:
                    st.warning("⚠️ Please enter both username and password")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ============================================
# MAIN APPLICATION HEADER
# ============================================
col_header, col_theme, col_refresh = st.columns([5, 1, 1])
with col_header:
    if LOGO_BASE64:
        logo_html = f'<img src="data:image/png;base64,{LOGO_BASE64}" style="width: 40px; height: auto; background: transparent; margin-right: 10px;">'
    else:
        logo_html = '<span style="font-size: 1.5rem; margin-right: 10px;">🏦</span>'
    
    st.markdown(f"""
    <div class="dashboard-header">
        <div style="display: flex; align-items: center; gap: 15px;">
            {logo_html}
            <div>
                <h1>HELB Strategy Performance Management System</h1>
                <p>Real-time monitoring | Work Plans | Contracts | Policies</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_theme:
    theme_icon = "🌙" if st.session_state.theme == "light" else "☀️"
    theme_label = "Dark" if st.session_state.theme == "light" else "Light"
    if st.button(f"{theme_icon} {theme_label}", key="theme_toggle"):
        toggle_theme()

with col_refresh:
    if st.button("🔄 Refresh", key="global_refresh"):
        st.cache_data.clear()
        st.rerun()

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    if LOGO_BASE64:
        st.markdown(f'<div style="text-align: center; padding: 0.5rem 0;"><img src="data:image/png;base64,{LOGO_BASE64}" style="width: 120px; height: auto; background: transparent;"></div>', unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='text-align: center; padding: 0.5rem 0;'>
            <div style='font-size: 2rem;'>🏦</div>
            <p style='color: white; font-weight: 700; margin: 0; font-size: 0.9rem;'>HELB</p>
        </div>
        """, unsafe_allow_html=True)
    
    role_display = st.session_state.user_role.replace('_', ' ').title() if st.session_state.user_role else "User"
    
    dept_details = get_department_by_id(st.session_state.user_dept) if st.session_state.user_dept else None
    if dept_details:
        if dept_details.get("directorate_name"):
            dept_display = f"{dept_details['name']} ({dept_details['directorate_name']})"
        else:
            dept_display = dept_details['name']
    else:
        dept_display = st.session_state.user_dept_name if st.session_state.user_dept_name else "No Department"
    
    st.markdown(f"""
    <div class='sidebar-user-info'>
        <strong>{st.session_state.user_fullname or "User"}</strong>
        <div class='dept' style='font-size: 0.7rem; margin-top: 5px;'>{dept_display}</div>
        <div class='role' style='font-size: 0.65rem; margin-top: 3px; opacity: 0.8;'>{role_display}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    menu_options = ["📊 Dashboard", "📋 Work Plans", "📄 Contracts", "📋 Policies"]
    if st.session_state.user_role == "admin":
        menu_options.append("⚙️ Admin Panel")
    if st.session_state.user_role in ["admin", "management"]:
        menu_options.append("🏢 Enterprise View")
    
    choice = st.radio("📋 Navigation", menu_options, label_visibility="collapsed")
    
    st.markdown("---")
    
    if st.button("🚪 Logout", use_container_width=True):
        add_audit_log("LOGOUT", "session", None, f"User logged out")
        st.session_state.clear()
        st.cache_data.clear()
        st.rerun()

# ============================================
# WORK PLANS MODULE (User View)
# ============================================
if choice == "📋 Work Plans":
    if st.session_state.user_role in ["admin", "management"]:
        st.markdown("<h2>📋 Institution-Wide Work Plan</h2>", unsafe_allow_html=True)
    else:
        st.markdown(f"<h2>📋 {st.session_state.user_dept_name} Department Work Plan</h2>", unsafe_allow_html=True)
    
    st.markdown("### 📅 Period Filters")
    col_fy, col_q, col_m = st.columns(3)
    with col_fy:
        financial_years = ["All"] + get_financial_years()
        selected_fy = st.selectbox("Financial Year", financial_years, key="fy_filter_workplan", index=0)
    with col_q:
        quarters = ["All", "Q1 (Jul-Sep)", "Q2 (Oct-Dec)", "Q3 (Jan-Mar)", "Q4 (Apr-Jun)"]
        selected_q = st.selectbox("Quarter", quarters, key="q_filter_workplan", index=0)
    with col_m:
        available_months = get_months_for_quarter(selected_q)
        selected_m = st.selectbox("Month", ["All"] + available_months, key="m_filter_workplan", index=0)
    
    st.markdown("---")
    
    work_plans = get_work_plans()
    
    if work_plans:
        df_plans = pd.DataFrame(work_plans)
        filtered_df = filter_work_plans_by_date(df_plans, selected_fy, selected_q, selected_m)
        filtered_plans = filtered_df.to_dict('records')
    else:
        filtered_plans = work_plans
    
    tab_add, tab_view, tab_dashboard = st.tabs(["➕ Add Work Plan Activity", "📊 View All Activities", "📈 Performance Dashboard"])
    
    with tab_add:
        st.markdown("### Add New Work Plan Activity")
        user_directorate = get_directorate_for_department(st.session_state.user_dept)
        
        with st.form("add_work_plan_form"):
            col1, col2 = st.columns(2)
            with col1:
                strategic_pillar = st.selectbox("Strategic Issue (Pillar)*", STRATEGIC_PILLARS)
                strategy = st.text_area("Strategy", placeholder="e.g., Enhance customer service through digital platforms", height=80)
                key_result_area = st.text_input("Key Result Area*")
                planned_activity = st.text_area("Planned Activity*")
                performance_indicator = st.text_input("Performance Indicator*")
            with col2:
                budget_allocation = st.number_input("Budget Allocation (KShs.)", min_value=0.0, step=10000.0, format="%.2f")
                annual_target = st.text_input("Annual Target*", placeholder="e.g., 90% or 5 reports")
                due_date = st.date_input("Due Date*")
                activity_category = st.selectbox("Activity Category*", ACTIVITY_CATEGORIES)
                dept_name = st.session_state.user_dept_name if st.session_state.user_dept_name else "Current Department"
                st.text_input("Department", value=dept_name, disabled=True)
                st.text_input("Directorate", value=user_directorate or "Not assigned", disabled=True)
            
            if st.form_submit_button("Save Work Plan Activity", use_container_width=True):
                if not key_result_area or not planned_activity or not performance_indicator or not annual_target:
                    st.error("Please fill all required fields (*)")
                else:
                    work_plan_data = {
                        "strategic_pillar": strategic_pillar,
                        "strategy": strategy if strategy else None,
                        "key_result_area": key_result_area,
                        "planned_activity": planned_activity,
                        "performance_indicator": performance_indicator,
                        "budget_allocation": budget_allocation if budget_allocation > 0 else None,
                        "annual_target": annual_target,
                        "actual_achievement": 0,
                        "due_date": due_date.isoformat(),
                        "activity_category": activity_category,
                        "status": "Pending",
                        "progress_percent": 0,
                        "department_id": st.session_state.user_dept,
                        "department_name": st.session_state.user_dept_name,
                        "created_by": st.session_state.user_id if st.session_state.user_id else None,
                        "created_at": datetime.now().isoformat()
                    }
                    if add_work_plan(work_plan_data):
                        st.success("✅ Work plan activity added successfully!")
                        st.balloons()
                        st.rerun()
    
    with tab_view:
        if filtered_plans:
            filter_summary = []
            if selected_fy != "All":
                filter_summary.append(f"FY: {selected_fy}")
            if selected_q != "All":
                filter_summary.append(f"Quarter: {selected_q}")
            if selected_m != "All":
                filter_summary.append(f"Month: {selected_m}")
            if filter_summary:
                st.info(f"📊 Showing activities for: {' | '.join(filter_summary)} | Total: {len(filtered_plans)} activities")
            
            col_filter1, col_filter2, col_filter3 = st.columns(3)
            with col_filter1:
                pillar_filter = st.multiselect("Filter by Pillar", STRATEGIC_PILLARS, default=[])
            with col_filter2:
                status_filter = st.multiselect("Filter by Status", ["Pending", "In Progress", "Done"], default=[])
            with col_filter3:
                category_filter = st.multiselect("Filter by Category", ACTIVITY_CATEGORIES, default=[])
            
            if st.session_state.user_role in ["admin", "management"]:
                with col_filter1:
                    departments_list = list(set([p.get("department_name", "Unknown") for p in filtered_plans if p.get("department_name")]))
                    dept_filter = st.multiselect("Filter by Department", departments_list, default=[])
            else:
                dept_filter = []
            
            final_plans = filtered_plans
            if pillar_filter:
                final_plans = [p for p in final_plans if p.get("strategic_pillar") in pillar_filter]
            if status_filter:
                final_plans = [p for p in final_plans if p.get("status") in status_filter]
            if category_filter:
                final_plans = [p for p in final_plans if p.get("activity_category") in category_filter]
            if dept_filter:
                final_plans = [p for p in final_plans if p.get("department_name") in dept_filter]
            
            st.markdown(f"**Showing {len(final_plans)} activities**")
            
            for plan in final_plans:
                due_date = datetime.strptime(plan["due_date"], "%Y-%m-%d").date()
                days_left = (due_date - datetime.now().date()).days
                
                current_actual = plan.get("actual_achievement", 0)
                annual_target = plan.get("annual_target", "0")
                progress_percent = calculate_progress_from_actual(annual_target, current_actual)
                exceeded = is_target_exceeded(current_actual, annual_target)
                
                if current_actual == 0 or current_actual is None:
                    badge = '<span class="badge-pending">🔴 Pending</span>'
                elif progress_percent >= 100:
                    if exceeded:
                        badge = '<span class="badge-exceeded">✅ Done (Exceeded Target!)</span>'
                    else:
                        badge = '<span class="badge-active">✅ Done</span>'
                elif progress_percent > 0:
                    badge = '<span class="badge-inprogress">🟡 In Progress</span>'
                else:
                    badge = '<span class="badge-pending">🔴 Pending</span>'
                
                if days_left < 0:
                    days_indicator = "🔴 (EXPIRED)"
                elif days_left <= 7:
                    days_indicator = f"🔴 ({days_left} days left - URGENT)"
                elif days_left <= 30:
                    days_indicator = f"🟡 ({days_left} days left)"
                else:
                    days_indicator = f"🟢 ({days_left} days left)"
                
                expander_title = f"📌 {plan['planned_activity'][:60]}... - {plan.get('strategic_pillar', 'N/A')} {days_indicator} - Progress: {progress_percent:.0f}%"
                
                with st.expander(expander_title, expanded=False):
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.markdown(f"**Strategic Pillar:** {plan.get('strategic_pillar', 'N/A')}")
                        if plan.get('strategy'):
                            st.markdown(f"**Strategy:** {plan.get('strategy', 'N/A')}")
                        st.markdown(f"**Key Result Area:** {plan.get('key_result_area', 'N/A')}")
                        st.markdown(f"**Planned Activity:** {plan.get('planned_activity', 'N/A')}")
                        st.markdown(f"**Performance Indicator:** {plan.get('performance_indicator', 'N/A')}")
                        st.markdown(f"**Annual Target:** {plan.get('annual_target', 'N/A')}")
                        st.markdown(f"**Due Date:** {plan['due_date']} ({days_left} days left)")
                        st.markdown(f"**Activity Category:** {plan.get('activity_category', 'N/A')}")
                        st.markdown(f"**Department:** {plan.get('department_name', 'N/A')}")
                    with col2:
                        st.markdown(f"**Status:** {badge}", unsafe_allow_html=True)
                        if plan.get('budget_allocation') and plan.get('budget_allocation') > 0:
                            st.markdown(f"**Budget:** KES {plan.get('budget_allocation', 0):,.2f}")
                        st.markdown(f"**Progress:** {progress_percent:.1f}%")
                        st.progress(progress_percent / 100)
                        if exceeded:
                            st.success(f"🎉 Target exceeded! Actual: {current_actual} vs Target: {annual_target}")
                        
                        st.markdown("---")
                        st.markdown("**Update Achievement**")
                        actual_input = st.number_input("Actual Achievement", min_value=0.0, step=1.0, value=float(current_actual) if current_actual else 0.0, key=f"actual_{plan['id']}")
                        new_progress = calculate_progress_from_actual(annual_target, actual_input)
                        st.caption(f"📊 Calculated Progress: {new_progress:.1f}%")
                        
                        if st.session_state.user_role == "admin":
                            st.markdown("---")
                            st.markdown("**📅 Admin: Edit Due Date**")
                            new_due_date = st.date_input("New Due Date", value=due_date, key=f"duedate_{plan['id']}")
                            if st.button(f"Update Due Date", key=f"updatedate_{plan['id']}"):
                                if update_work_plan_due_date(plan['id'], new_due_date):
                                    st.success("✅ Due date updated!")
                                    st.rerun()
                        
                        col_update, col_delete = st.columns(2)
                        with col_update:
                            if st.button(f"Update Achievement", key=f"update_{plan['id']}"):
                                if actual_input == 0:
                                    new_status = "Pending"
                                elif new_progress >= 100:
                                    new_status = "Done"
                                elif new_progress > 0:
                                    new_status = "In Progress"
                                else:
                                    new_status = "Pending"
                                if update_work_plan_progress(plan['id'], actual_input, new_progress, new_status):
                                    st.success("✅ Achievement updated successfully!")
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to update. Please try again.")
                        with col_delete:
                            if st.session_state.user_role == "admin":
                                if st.button(f"🗑️ Delete", key=f"delete_{plan['id']}"):
                                    if delete_work_plan(plan['id']):
                                        st.success("✅ Deleted successfully!")
                                        st.rerun()
        else:
            st.info("No work plan activities found. Click 'Add Work Plan Activity' to get started.")
    
    with tab_dashboard:
        if filtered_plans:
            df = pd.DataFrame(filtered_plans)
            df['calculated_progress'] = df.apply(lambda x: calculate_progress_from_actual(x.get('annual_target', '0'), x.get('actual_achievement', 0)), axis=1)
            df['exceeded'] = df.apply(lambda x: is_target_exceeded(x.get('actual_achievement', 0), x.get('annual_target', '0')), axis=1)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-label'>📋 TOTAL ACTIVITIES</div>
                    <div class='kpi-value'>{len(df)}</div>
                    <div class='kpi-sub'>Total Activities</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                completed = len(df[df['calculated_progress'] >= 100])
                rate = (completed/len(df)*100) if len(df)>0 else 0
                st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-label'>✅ COMPLETION RATE</div>
                    <div class='kpi-value'>{rate:.0f}%</div>
                    <div class='progress-bar'><div class='progress-fill' style='width:{rate}%;'></div></div>
                    <div class='kpi-sub'>Completion Rate</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                total_budget = df['budget_allocation'].fillna(0).sum()
                st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-label'>💰 TOTAL BUDGET</div>
                    <div class='kpi-value'>KES {total_budget/1e6:.1f}M</div>
                    <div class='kpi-sub'>Total Budget</div>
                </div>
                """, unsafe_allow_html=True)
            with col4:
                exceeded_count = len(df[df['exceeded'] == True])
                st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-label'>🏆 TARGETS EXCEEDED</div>
                    <div class='kpi-value'>{exceeded_count}</div>
                    <div class='kpi-sub'>Exceeded Targets</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No data available for the selected period.")

# ============================================
# DASHBOARD
# ============================================
elif choice == "📊 Dashboard":
    st.markdown("### Performance Dashboard")
    
    work_plans = get_work_plans()
    contracts = get_cached_contracts(st.session_state.user_role, st.session_state.user_dept)
    policies = get_cached_policies(st.session_state.user_role, st.session_state.user_dept)
    
    col_fy_dash, col_q_dash, col_m_dash = st.columns(3)
    with col_fy_dash:
        financial_years = ["All"] + get_financial_years()
        selected_fy = st.selectbox("Financial Year", financial_years, 
                                   index=financial_years.index(st.session_state.filter_financial_year) if st.session_state.filter_financial_year in financial_years else 0,
                                   key="fy_filter_dash")
        st.session_state.filter_financial_year = selected_fy
    with col_q_dash:
        quarters = ["All", "Q1 (Jul-Sep)", "Q2 (Oct-Dec)", "Q3 (Jan-Mar)", "Q4 (Apr-Jun)"]
        selected_q = st.selectbox("Quarter", quarters,
                                   index=quarters.index(st.session_state.filter_quarter) if st.session_state.filter_quarter in quarters else 0,
                                   key="q_filter_dash")
        st.session_state.filter_quarter = selected_q
    with col_m_dash:
        available_months = get_months_for_quarter(st.session_state.filter_quarter)
        selected_m = st.selectbox("Month", ["All"] + available_months,
                                   index=0 if st.session_state.filter_month == "All" or st.session_state.filter_month not in available_months else available_months.index(st.session_state.filter_month) + 1,
                                   key="m_filter_dash")
        st.session_state.filter_month = selected_m
    
    if work_plans:
        df_plans = pd.DataFrame(work_plans)
        df_plans['due_date_dt'] = pd.to_datetime(df_plans['due_date'])
        df_plans['due_month'] = df_plans['due_date_dt'].dt.month
        df_plans['due_year'] = df_plans['due_date_dt'].dt.year
        df_plans['quarter'] = df_plans['due_month'].apply(get_quarter_from_month)
        df_plans['calculated_progress'] = df_plans.apply(
            lambda x: calculate_progress_from_actual(x.get('annual_target', '0'), x.get('actual_achievement', 0)), axis=1
        )
        df_plans['exceeded'] = df_plans.apply(
            lambda x: is_target_exceeded(x.get('actual_achievement', 0), x.get('annual_target', '0')), axis=1
        )
        df_plans['days_left'] = (df_plans['due_date_dt'] - pd.Timestamp.now()).dt.days
        df_plans['status_group'] = df_plans['calculated_progress'].apply(
            lambda x: 'Completed' if x >= 100 else ('In Progress' if x > 0 else 'Not Started')
        )
        
        filtered_work_df = filter_work_plans_by_date(df_plans, selected_fy, selected_q, selected_m)
        
        if st.session_state.user_role in ["admin", "management"]:
            departments_list = filtered_work_df['department_name'].unique().tolist() if not filtered_work_df.empty else []
            if departments_list:
                selected_dept_filter = st.multiselect("Filter by Department", departments_list, default=[])
                if selected_dept_filter:
                    filtered_work_df = filtered_work_df[filtered_work_df['department_name'].isin(selected_dept_filter)]
    else:
        filtered_work_df = pd.DataFrame()
    
    if contracts:
        df_contracts_raw = pd.DataFrame(contracts)
        filtered_contracts_df = filter_contracts_by_date(df_contracts_raw, selected_fy, selected_q, selected_m)
    else:
        filtered_contracts_df = pd.DataFrame()
    
    if policies:
        df_policies_raw = pd.DataFrame(policies)
        filtered_policies_df = filter_policies_by_date(df_policies_raw, selected_fy, selected_q, selected_m)
    else:
        filtered_policies_df = pd.DataFrame()
    
    tab_work, tab_contracts, tab_policies = st.tabs(["📋 Work Plans Analytics", "📄 Contracts Analytics", "📜 Policies Analytics"])
    
    with tab_work:
        if not filtered_work_df.empty:
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-label'>📋 TOTAL</div>
                    <div class='kpi-value'>{len(filtered_work_df)}</div>
                    <div class='kpi-sub'>Activities</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                completed = len(filtered_work_df[filtered_work_df['calculated_progress'] >= 100])
                rate = (completed/len(filtered_work_df)*100) if len(filtered_work_df)>0 else 0
                st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-label'>✅ COMPLETED</div>
                    <div class='kpi-value'>{rate:.0f}%</div>
                    <div class='progress-bar'><div class='progress-fill' style='width:{rate}%;'></div></div>
                    <div class='kpi-sub'>Completion Rate</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                avg_progress = filtered_work_df['calculated_progress'].mean()
                st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-label'>📈 AVG PROGRESS</div>
                    <div class='kpi-value'>{avg_progress:.0f}%</div>
                    <div class='kpi-sub'>Average Progress</div>
                </div>
                """, unsafe_allow_html=True)
            with col4:
                total_budget = filtered_work_df['budget_allocation'].fillna(0).sum()
                st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-label'>💰 BUDGET</div>
                    <div class='kpi-value'>KES {total_budget/1e6:.1f}M</div>
                    <div class='kpi-sub'>Total Budget</div>
                </div>
                """, unsafe_allow_html=True)
            with col5:
                exceeded = len(filtered_work_df[filtered_work_df['exceeded'] == True])
                st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-label'>🏆 EXCEEDED</div>
                    <div class='kpi-value'>{exceeded}</div>
                    <div class='kpi-sub'>Targets Exceeded</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            col_chart1, col_chart2 = st.columns(2)
            with col_chart1:
                st.markdown("#### Status Distribution")
                status_counts = filtered_work_df['status_group'].value_counts().reset_index()
                status_counts.columns = ['Status', 'Count']
                color_map = {'Completed': '#00843D', 'In Progress': '#FFB81C', 'Not Started': '#dc2626'}
                fig = go.Figure(data=[go.Pie(
                    labels=status_counts['Status'],
                    values=status_counts['Count'],
                    hole=0.4,
                    marker=dict(colors=[color_map.get(s, '#808080') for s in status_counts['Status']]),
                    textinfo='label+percent',
                    textposition='auto'
                )])
                fig.update_layout(height=350, margin=dict(l=20, r=20, t=30, b=20))
                st.plotly_chart(fig, use_container_width=True)
            
            with col_chart2:
                st.markdown("#### Progress by Strategic Pillar")
                pillar_progress = filtered_work_df.groupby('strategic_pillar')['calculated_progress'].mean().reset_index()
                pillar_progress.columns = ['Pillar', 'Progress %']
                pillar_progress = pillar_progress.sort_values('Progress %', ascending=True)
                fig = px.bar(pillar_progress, y='Pillar', x='Progress %', orientation='h',
                            color='Progress %', color_continuous_scale='Greens',
                            text='Progress %')
                fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                fig.update_layout(height=350, xaxis_title="Progress %", yaxis_title="", margin=dict(l=20, r=20, t=30, b=20))
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("#### Department Performance")
            dept_progress = filtered_work_df.groupby('department_name')['calculated_progress'].mean().reset_index()
            dept_progress.columns = ['Department', 'Progress %']
            dept_progress = dept_progress.sort_values('Progress %', ascending=True)
            fig = px.bar(dept_progress, y='Department', x='Progress %', orientation='h',
                        color='Progress %', color_continuous_scale='Greens',
                        text='Progress %')
            fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig.update_layout(height=max(400, len(dept_progress) * 30), xaxis_title="Progress %", yaxis_title="", margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig, use_container_width=True)
            
            col_chart3, col_chart4 = st.columns(2)
            with col_chart3:
                st.markdown("#### Activity Category Breakdown")
                category_stats = filtered_work_df['activity_category'].value_counts().reset_index()
                category_stats.columns = ['Category', 'Count']
                fig = px.bar(category_stats, x='Category', y='Count',
                            color='Count', color_discrete_sequence=[HELB_GREEN],
                            text='Count')
                fig.update_traces(textposition='outside')
                fig.update_layout(height=350, margin=dict(l=20, r=20, t=30, b=20))
                st.plotly_chart(fig, use_container_width=True)
            
            with col_chart4:
                st.markdown("#### Quarterly Performance Trend")
                quarterly_data = filtered_work_df.groupby('quarter').agg({
                    'id': 'count',
                    'calculated_progress': 'mean'
                }).reset_index()
                quarterly_data.columns = ['Quarter', 'Activities', 'Avg Progress %']
                quarter_order = ["Q1 (Jul-Sep)", "Q2 (Oct-Dec)", "Q3 (Jan-Mar)", "Q4 (Apr-Jun)"]
                quarterly_data['Quarter'] = pd.Categorical(quarterly_data['Quarter'], categories=quarter_order, ordered=True)
                quarterly_data = quarterly_data.sort_values('Quarter')
                
                fig = go.Figure()
                fig.add_trace(go.Bar(x=quarterly_data['Quarter'], y=quarterly_data['Activities'],
                                     name='Activities', marker_color=HELB_GREEN,
                                     text=quarterly_data['Activities'], textposition='outside'))
                fig.add_trace(go.Scatter(x=quarterly_data['Quarter'], y=quarterly_data['Avg Progress %'],
                                         name='Avg Progress %', marker_color=HELB_GOLD,
                                         line=dict(width=3), yaxis='y2'))
                fig.update_layout(
                    height=350,
                    yaxis_title="Number of Activities",
                    yaxis2=dict(title="Avg Progress %", overlaying='y', side='right'),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
                    margin=dict(l=20, r=60, t=30, b=20)
                )
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("### ⚠️ Priority Alerts")
            col_alert1, col_alert2 = st.columns(2)
            
            overdue_df = filtered_work_df[(filtered_work_df['days_left'] < 0) & (filtered_work_df['calculated_progress'] < 100)]
            urgent_df = filtered_work_df[(filtered_work_df['days_left'] >= 0) & (filtered_work_df['days_left'] <= 14) & (filtered_work_df['calculated_progress'] < 80)]
            
            with col_alert1:
                if not overdue_df.empty:
                    st.error(f"🔴 **{len(overdue_df)} Overdue Activities**")
                    for _, row in overdue_df.head(5).iterrows():
                        st.markdown(f"- {row['planned_activity'][:50]}... (Due: {row['due_date']})")
                else:
                    st.success("✅ No overdue activities")
            
            with col_alert2:
                if not urgent_df.empty:
                    st.warning(f"🟡 **{len(urgent_df)} Urgent Activities**")
                    for _, row in urgent_df.head(5).iterrows():
                        st.markdown(f"- {row['planned_activity'][:50]}... ({row['days_left']} days left)")
                else:
                    st.success("✅ No urgent at-risk activities")
            
            with st.expander("📥 Export Data", expanded=False):
                csv = filtered_work_df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download Work Plan Data", csv, f"work_plan_data_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")
        else:
            st.info("No work plan data available for the selected filters.")
    
    with tab_contracts:
        if not filtered_contracts_df.empty:
            df_contracts = filtered_contracts_df.copy()
            
            df_contracts['contract_value'] = pd.to_numeric(df_contracts.get('contract_value', 0), errors='coerce').fillna(0)
            df_contracts['amount_spent_to_date'] = pd.to_numeric(df_contracts.get('amount_spent_to_date', 0), errors='coerce').fillna(0)
            df_contracts['vendor_performance'] = pd.to_numeric(df_contracts.get('vendor_performance', 0), errors='coerce').fillna(0)
            df_contracts['utilization_rate'] = pd.to_numeric(df_contracts.get('utilization_rate', 0), errors='coerce').fillna(0)
            
            departments = get_cached_departments()
            dept_map = {d['id']: d['name'] for d in departments}
            df_contracts['department_name'] = df_contracts['department_id'].map(dept_map).fillna("Unknown")
            
            total_value = df_contracts['contract_value'].sum()
            total_spent = df_contracts['amount_spent_to_date'].sum()
            utilization = (total_spent/total_value*100) if total_value > 0 else 0
            active = len(df_contracts[df_contracts['status'] == 'active'])
            expiring = len(df_contracts[df_contracts['status'] == 'expiring_soon'])
            avg_performance = df_contracts[df_contracts['vendor_performance'] > 0]['vendor_performance'].mean()
            
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-label'>💰 TOTAL VALUE</div>
                    <div class='kpi-value'>KES {total_value/1e6:.1f}M</div>
                    <div class='kpi-sub'>Total Contract Value</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-label'>💸 TOTAL SPENT</div>
                    <div class='kpi-value'>KES {total_spent/1e6:.1f}M</div>
                    <div class='progress-bar'><div class='progress-fill' style='width:{utilization}%;'></div></div>
                    <div class='kpi-sub'>{utilization:.0f}% utilized</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-label'>✅ ACTIVE</div>
                    <div class='kpi-value'>{active}</div>
                    <div class='kpi-sub'>Active Contracts</div>
                </div>
                """, unsafe_allow_html=True)
            with col4:
                st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-label'>⚠️ EXPIRING SOON</div>
                    <div class='kpi-value'>{expiring}</div>
                    <div class='kpi-sub'>Within 30 days</div>
                </div>
                """, unsafe_allow_html=True)
            with col5:
                st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-label'>⭐ AVG RATING</div>
                    <div class='kpi-value'>{avg_performance:.1f}/5</div>
                    <div class='kpi-sub'>Vendor Performance</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Filters for contracts list
            st.markdown("#### 🔍 Filter Contracts")
            col_filter1, col_filter2, col_filter3, col_filter4 = st.columns(4)
            with col_filter1:
                status_filter_contract = st.multiselect("Status", ["active", "expiring_soon", "expired"], default=[])
            with col_filter2:
                compliance_filter = st.multiselect("Compliance", ["Fully Compliant", "Partially Compliant", "Non-Compliant"], default=[])
            with col_filter3:
                if 'payment_terms' in df_contracts.columns:
                    payment_filter = st.multiselect("Payment Terms", df_contracts['payment_terms'].dropna().unique().tolist(), default=[])
                else:
                    payment_filter = []
            with col_filter4:
                dept_filter_contract = st.multiselect("Department", df_contracts['department_name'].unique().tolist(), default=[])
            
            filtered_contracts_list = df_contracts.copy()
            if status_filter_contract:
                filtered_contracts_list = filtered_contracts_list[filtered_contracts_list['status'].isin(status_filter_contract)]
            if compliance_filter:
                filtered_contracts_list = filtered_contracts_list[filtered_contracts_list['compliance_status'].isin(compliance_filter)]
            if payment_filter:
                filtered_contracts_list = filtered_contracts_list[filtered_contracts_list['payment_terms'].isin(payment_filter)]
            if dept_filter_contract:
                filtered_contracts_list = filtered_contracts_list[filtered_contracts_list['department_name'].isin(dept_filter_contract)]
            
            st.markdown(f"**Showing {len(filtered_contracts_list)} contracts**")
            
            for _, contract in filtered_contracts_list.iterrows():
                end_date = datetime.strptime(contract["end_date"], "%Y-%m-%d").date()
                days_left = (end_date - datetime.now().date()).days
                
                if days_left > 30:
                    status_class = "status-active"
                    status_text = "Active"
                elif days_left > 0:
                    status_class = "status-expiring"
                    status_text = f"Expiring in {days_left} days"
                else:
                    status_class = "status-expired"
                    status_text = "Expired"
                
                budget_alert_badge = '⚠️' if contract.get('budget_alert', False) else ''
                
                # Get multi-year breakdown if applicable
                multi_year_info = ""
                if contract.get('is_multi_year', False):
                    years = get_contract_years(contract['id'])
                    if years:
                        multi_year_info = f'<div class="contract-detail" style="margin-top: 0.5rem;"><strong>Yearly Breakdown:</strong><br>'
                        for year in years:
                            year_status = "✅" if year.get('status') == 'completed' else "🟢" if year.get('status') == 'active' else "🟡"
                            multi_year_info += f'&nbsp;&nbsp;{year_status} Year {year["year_number"]}: KES {year["annual_value"]:,.0f} (Spent: KES {year.get("amount_spent_to_date", 0):,.0f} - {year.get("utilization_rate", 0):.0f}%)<br>'
                        multi_year_info += '</div>'
                
                # Format payment term nicely
                payment_term_display = contract.get('payment_terms', 'N/A')
                if payment_term_display == "Monthly Retainer":
                    payment_term_display = "💰 Monthly Retainer"
                elif payment_term_display == "Quarterly Retainer":
                    payment_term_display = "📅 Quarterly Retainer"
                elif payment_term_display == "Bi-annually":
                    payment_term_display = "📆 Bi-annual Payment"
                elif payment_term_display == "Annually":
                    payment_term_display = "📅 Annual Payment"
                elif payment_term_display == "Milestone-based":
                    payment_term_display = "🎯 Milestone-based Payment"
                elif payment_term_display == "One-time Payment":
                    payment_term_display = "💵 One-time Payment"
                
                st.markdown(f"""
                <div class='contract-card'>
                    <div style='display: flex; justify-content: space-between; align-items: flex-start;'>
                        <div style='flex: 1;'>
                            <div class='contract-title'>📄 {contract['contract_title']} {budget_alert_badge}</div>
                            <div class='contract-detail'><strong>Vendor:</strong> {contract['vendor_name']}</div>
                            <div class='contract-detail'><strong>Duration:</strong> {contract.get('contract_duration', 'N/A')} | <strong>Total Value:</strong> KES {contract.get('total_contract_value', contract.get('contract_value', 0)):,.0f}</div>
                            <div class='contract-detail'><strong>Spent to Date:</strong> KES {contract.get('amount_spent_to_date', 0):,.0f} ({contract.get('utilization_rate', 0):.0f}%)</div>
                            <div class='contract-detail'><strong>End Date:</strong> {contract['end_date']} | <strong>Payment:</strong> {payment_term_display}</div>
                            <div class='contract-detail'><strong>Compliance:</strong> {contract.get('compliance_status', 'N/A')} | <strong>Performance:</strong> ⭐ {contract.get('vendor_performance', 0)}/5</div>
                            {multi_year_info}
                            <div class='contract-detail'><strong>Auto-renewal:</strong> {'Yes' if contract.get('auto_renewal', False) else 'No'}</div>
                        </div>
                        <div style='text-align: right;'>
                            <span class='status-badge {status_class}'>{status_text}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No contracts found for the selected filters.")
    
    with tab_policies:
        if not filtered_policies_df.empty:
            df_policies = filtered_policies_df.copy()
            
            total_policies = len(df_policies)
            active_policies = len(df_policies[df_policies['status'] == 'active'])
            expiring_soon = len(df_policies[df_policies['status'] == 'expiring_soon'])
            expired_policies = len(df_policies[df_policies['status'] == 'expired'])
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-label'>📜 TOTAL POLICIES</div>
                    <div class='kpi-value'>{total_policies}</div>
                    <div class='kpi-sub'>All Policies</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-label'>✅ ACTIVE</div>
                    <div class='kpi-value'>{active_policies}</div>
                    <div class='kpi-sub'>Currently Active</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-label'>⚠️ EXPIRING SOON</div>
                    <div class='kpi-value'>{expiring_soon}</div>
                    <div class='kpi-sub'>Within 90 days</div>
                </div>
                """, unsafe_allow_html=True)
            with col4:
                st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-label'>🔴 EXPIRED</div>
                    <div class='kpi-value'>{expired_policies}</div>
                    <div class='kpi-sub'>Needs Review</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            col_chart1, col_chart2 = st.columns(2)
            with col_chart1:
                if 'category' in df_policies.columns:
                    st.markdown("#### Policies by Category")
                    category_counts = df_policies['category'].value_counts().reset_index()
                    category_counts.columns = ['Category', 'Count']
                    fig = px.pie(category_counts, values='Count', names='Category', hole=0.4,
                                color_discrete_sequence=[HELB_GREEN, HELB_GOLD, HELB_BLUE, "#8B5CF6", "#10B981"])
                    fig.update_layout(height=350)
                    st.plotly_chart(fig, use_container_width=True)
            
            with col_chart2:
                if 'policy_scope' in df_policies.columns:
                    st.markdown("#### Policy Scope Distribution")
                    scope_counts = df_policies['policy_scope'].value_counts().reset_index()
                    scope_counts.columns = ['Scope', 'Count']
                    fig = px.bar(scope_counts, x='Scope', y='Count', color='Count',
                               color_discrete_sequence=[HELB_GREEN], text='Count')
                    fig.update_traces(textposition='outside')
                    fig.update_layout(height=350)
                    st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            st.markdown("#### 🔍 Filter Policies")
            col_filter1, col_filter2, col_filter3 = st.columns(3)
            with col_filter1:
                status_filter_policy = st.multiselect("Status", ["active", "expiring_soon", "expired"], default=[], key="policy_status_filter")
            with col_filter2:
                if 'category' in df_policies.columns:
                    category_filter_policy = st.multiselect("Category", df_policies['category'].unique().tolist(), default=[], key="policy_category_filter")
                else:
                    category_filter_policy = []
            with col_filter3:
                if 'policy_scope' in df_policies.columns:
                    scope_filter_policy = st.multiselect("Scope", df_policies['policy_scope'].unique().tolist(), default=[], key="policy_scope_filter")
                else:
                    scope_filter_policy = []
            
            filtered_policies_list = df_policies.copy()
            if status_filter_policy:
                filtered_policies_list = filtered_policies_list[filtered_policies_list['status'].isin(status_filter_policy)]
            if category_filter_policy:
                filtered_policies_list = filtered_policies_list[filtered_policies_list['category'].isin(category_filter_policy)]
            if scope_filter_policy:
                filtered_policies_list = filtered_policies_list[filtered_policies_list['policy_scope'].isin(scope_filter_policy)]
            
            st.markdown(f"**Showing {len(filtered_policies_list)} policies**")
            
            for _, policy in filtered_policies_list.iterrows():
                expiry = datetime.strptime(policy["expiry_date"], "%Y-%m-%d").date()
                days_left = (expiry - datetime.now().date()).days
                
                if days_left > 90:
                    status_class = "status-active"
                    status_text = "Active"
                elif days_left > 0:
                    status_class = "status-expiring"
                    status_text = f"Expires in {days_left} days"
                else:
                    status_class = "status-expired"
                    status_text = "Expired"
                
                category = policy.get('category', 'Uncategorized')
                policy_scope = policy.get('policy_scope', 'Not specified')
                version = policy.get('version', 'v1.0')
                owner = policy.get('policy_owner', 'Not assigned')
                review_date = policy.get('review_date', 'Not scheduled')
                
                st.markdown(f"""
                <div class='policy-card'>
                    <div style='display: flex; justify-content: space-between; align-items: flex-start;'>
                        <div style='flex: 1;'>
                            <div class='policy-title'>📜 {policy['policy_name']} (v{version})</div>
                            <div class='policy-detail'><strong>Category:</strong> {category} | <strong>Scope:</strong> {policy_scope}</div>
                            <div class='policy-detail'><strong>Owner:</strong> {owner} | <strong>Next Review:</strong> {review_date}</div>
                            <div class='policy-detail'><strong>Effective:</strong> {policy.get('effective_date', 'N/A')} | <strong>Expires:</strong> {policy['expiry_date']}</div>
                            <div class='policy-detail'><strong>Affected:</strong> {policy.get('affected_entities', 'N/A')}</div>
                        </div>
                        <div style='text-align: right;'>
                            <span class='status-badge {status_class}'>{status_text}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No policies found for the selected filters.")
    
    st.success(f"👋 Welcome, {st.session_state.user_fullname}!")

# ============================================
# CONTRACTS SECTION (User View)
# ============================================
elif choice == "📄 Contracts":
    st.subheader("Contract Management")
    
    tab_overview, tab_active, tab_expiring, tab_add, tab_update = st.tabs(["📊 Overview & Analytics", "✅ Active Contracts", "⚠️ Expiring & Expired", "➕ New Contract", "✏️ Update Contract"])
    
    with tab_overview:
        contracts = get_cached_contracts(st.session_state.user_role, st.session_state.user_dept)
        if contracts:
            df_contracts = pd.DataFrame(contracts)
            
            df_contracts['contract_value'] = pd.to_numeric(df_contracts.get('contract_value', 0), errors='coerce').fillna(0)
            df_contracts['amount_spent_to_date'] = pd.to_numeric(df_contracts.get('amount_spent_to_date', 0), errors='coerce').fillna(0)
            
            total_value = df_contracts['contract_value'].sum()
            total_spent = df_contracts['amount_spent_to_date'].sum()
            overall_utilization = (total_spent/total_value*100) if total_value > 0 else 0
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("💰 Total Contract Value", f"KES {total_value:,.0f}")
            with col2:
                st.metric("💸 Total Spent", f"KES {total_spent:,.0f}", delta=f"{overall_utilization:.0f}% utilized")
            with col3:
                active_count = len(df_contracts[df_contracts['status'] == 'active'])
                st.metric("✅ Active Contracts", active_count)
            with col4:
                st.metric("📄 Total Contracts", len(df_contracts))
        else:
            st.info("No contracts found.")
    
    with tab_active:
        contracts = get_cached_contracts(st.session_state.user_role, st.session_state.user_dept)
        if contracts:
            active_contracts = [c for c in contracts if c.get('status') == 'active']
            if active_contracts:
                for contract in active_contracts:
                    end_date = datetime.strptime(contract["end_date"], "%Y-%m-%d").date()
                    days_left = (end_date - datetime.now().date()).days
                    
                    payment_term_display = contract.get('payment_terms', 'N/A')
                    if payment_term_display == "Monthly Retainer":
                        payment_term_display = "💰 Monthly Retainer"
                    elif payment_term_display == "Quarterly Retainer":
                        payment_term_display = "📅 Quarterly Retainer"
                    elif payment_term_display == "Bi-annually":
                        payment_term_display = "📆 Bi-annual Payment"
                    elif payment_term_display == "Annually":
                        payment_term_display = "📅 Annual Payment"
                    elif payment_term_display == "Milestone-based":
                        payment_term_display = "🎯 Milestone-based Payment"
                    elif payment_term_display == "One-time Payment":
                        payment_term_display = "💵 One-time Payment"
                    
                    st.markdown(f"""
                    <div class='contract-card'>
                        <div style='display: flex; justify-content: space-between; align-items: flex-start;'>
                            <div style='flex: 1;'>
                                <div class='contract-title'>📄 {contract['contract_title']}</div>
                                <div class='contract-detail'><strong>Vendor:</strong> {contract['vendor_name']}</div>
                                <div class='contract-detail'><strong>Duration:</strong> {contract.get('contract_duration', 'N/A')} | <strong>Value:</strong> KES {contract.get('contract_value', 0):,.0f}</div>
                                <div class='contract-detail'><strong>End Date:</strong> {contract['end_date']} ({days_left} days left)</div>
                                <div class='contract-detail'><strong>Payment:</strong> {payment_term_display} | <strong>Compliance:</strong> {contract.get('compliance_status', 'N/A')}</div>
                            </div>
                            <div style='text-align: right;'>
                                <span class='status-badge status-active'>Active</span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No active contracts.")
        else:
            st.info("No contracts found.")
    
    with tab_expiring:
        contracts = get_cached_contracts(st.session_state.user_role, st.session_state.user_dept)
        if contracts:
            expiring_contracts = [c for c in contracts if c.get('status') in ['expiring_soon', 'expired']]
            if expiring_contracts:
                for contract in expiring_contracts:
                    end_date = datetime.strptime(contract["end_date"], "%Y-%m-%d").date()
                    days_left = (end_date - datetime.now().date()).days
                    status_class = "status-expiring" if days_left > 0 else "status-expired"
                    status_text = f"Expires in {days_left} days" if days_left > 0 else "Expired"
                    
                    st.markdown(f"""
                    <div class='contract-card'>
                        <div style='display: flex; justify-content: space-between; align-items: flex-start;'>
                            <div style='flex: 1;'>
                                <div class='contract-title'>📄 {contract['contract_title']}</div>
                                <div class='contract-detail'><strong>Vendor:</strong> {contract['vendor_name']}</div>
                                <div class='contract-detail'><strong>Duration:</strong> {contract.get('contract_duration', 'N/A')} | <strong>Value:</strong> KES {contract.get('contract_value', 0):,.0f}</div>
                                <div class='contract-detail'><strong>End Date:</strong> {contract['end_date']} ({abs(days_left)} days {'overdue' if days_left < 0 else 'left'})</div>
                                <div class='contract-detail'><strong>Compliance:</strong> {contract.get('compliance_status', 'N/A')}</div>
                            </div>
                            <div style='text-align: right;'>
                                <span class='status-badge {status_class}'>{status_text}</span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("No expiring or expired contracts!")
        else:
            st.info("No contracts found.")
    
    with tab_add:
        st.markdown("### Add New Contract")
        
        contract_type = st.radio("Contract Type", ["Single Year Contract", "Multi-Year Contract"], horizontal=True)
        
        with st.form("new_contract_enhanced"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Basic Information")
                contract_title = st.text_input("Contract Title*")
                vendor_name = st.text_input("Vendor Name*")
                contract_duration = st.selectbox("Contract Duration*", ["3 months", "6 months", "1 year", "2 years", "3 years", "4 years", "5 years"])
                
            with col2:
                st.markdown("#### Dates & Terms")
                start_date = st.date_input("Start Date*", value=datetime.now().date())
                end_date = st.date_input("End Date*")
                signed_date = st.date_input("Signed Date", value=datetime.now().date())
                payment_terms = st.selectbox("Payment Terms*", PAYMENT_TERMS)
                auto_renewal = st.checkbox("Auto-renewal")
            
            if contract_type == "Multi-Year Contract":
                st.markdown("---")
                st.markdown("#### 📅 Contract Years Breakdown")
                st.info("For multi-year contracts, please specify the value for each year")
                
                num_years = 1
                if "2 years" in contract_duration:
                    num_years = 2
                elif "3 years" in contract_duration:
                    num_years = 3
                elif "4 years" in contract_duration:
                    num_years = 4
                elif "5 years" in contract_duration:
                    num_years = 5
                
                years_data = []
                total_value = 0
                
                for year_num in range(1, num_years + 1):
                    st.markdown(f"**Year {year_num}**")
                    col_y1, col_y2, col_y3 = st.columns(3)
                    with col_y1:
                        year_value = st.number_input(f"Annual Value - Year {year_num} (KES)", 
                                                      min_value=0.0, step=10000.0, format="%.2f", 
                                                      key=f"year_value_{year_num}")
                    with col_y2:
                        year_start = st.date_input(f"Year {year_num} Start Date", 
                                                   value=start_date if year_num == 1 else None,
                                                   key=f"year_start_{year_num}")
                    with col_y3:
                        year_end = st.date_input(f"Year {year_num} End Date", 
                                                 value=None,
                                                 key=f"year_end_{year_num}")
                    
                    if year_value > 0:
                        total_value += year_value
                        years_data.append({
                            "year_number": year_num,
                            "year_start_date": year_start.isoformat() if year_start else None,
                            "year_end_date": year_end.isoformat() if year_end else None,
                            "annual_value": year_value,
                            "amount_spent_to_date": 0,
                            "status": "active"
                        })
                
                st.info(f"💰 **Total Contract Value: KES {total_value:,.2f}**")
            else:
                contract_value = st.number_input("Contract Value (KES)*", min_value=0.0, step=10000.0, format="%.2f")
                amount_spent_to_date = st.number_input("Amount Spent to Date (KES)", min_value=0.0, step=10000.0, format="%.2f", value=0.0)
            
            col3, col4 = st.columns(2)
            
            with col3:
                st.markdown("#### Compliance & Performance")
                compliance_status = st.selectbox("Compliance Status", ["Fully Compliant", "Partially Compliant", "Non-Compliant"])
                vendor_performance = st.slider("Vendor Performance Rating", 0.0, 5.0, 3.0, 0.5)
                contract_url = st.text_input("Contract Document URL", placeholder="https://...")
                
            with col4:
                st.markdown("#### Additional Details")
                department_id = st.selectbox("Department", ["None"] + [d["name"] for d in get_cached_departments()])
                breach_notes = st.text_area("Breach/Compliance Notes", height=80)
            
            if st.form_submit_button("Save Contract", use_container_width=True):
                if contract_title and vendor_name and contract_duration:
                    if contract_type == "Multi-Year Contract" and not years_data:
                        st.error("Please add at least one year with valid value")
                    elif contract_type == "Single Year Contract" and contract_value <= 0:
                        st.error("Please enter a valid contract value")
                    else:
                        if contract_type == "Multi-Year Contract":
                            total_value = sum(y['annual_value'] for y in years_data)
                            total_spent = sum(y.get('amount_spent_to_date', 0) for y in years_data)
                            utilization = (total_spent / total_value * 100) if total_value > 0 else 0
                            
                            contract_data = {
                                "contract_title": contract_title,
                                "vendor_name": vendor_name,
                                "contract_duration": contract_duration,
                                "contract_value": total_value,
                                "total_contract_value": total_value,
                                "amount_spent_to_date": total_spent,
                                "utilization_rate": utilization,
                                "start_date": start_date.isoformat(),
                                "end_date": end_date.isoformat(),
                                "signed_date": signed_date.isoformat(),
                                "payment_terms": payment_terms,
                                "auto_renewal": auto_renewal,
                                "compliance_status": compliance_status,
                                "vendor_performance": vendor_performance,
                                "contract_url": contract_url if contract_url else None,
                                "breach_notes": breach_notes if breach_notes else None,
                                "is_multi_year": True,
                                "department_id": st.session_state.user_dept
                            }
                            
                            success, message = add_multi_year_contract(contract_data, years_data)
                        else:
                            end_date_obj = end_date
                            days_left = (end_date_obj - datetime.now().date()).days
                            status = "active" if days_left > 30 else ("expiring_soon" if days_left > 0 else "expired")
                            utilization = (amount_spent_to_date / contract_value * 100) if contract_value > 0 else 0
                            
                            contract_data = {
                                "contract_title": contract_title,
                                "vendor_name": vendor_name,
                                "contract_duration": contract_duration,
                                "contract_value": contract_value,
                                "total_contract_value": contract_value,
                                "amount_spent_to_date": amount_spent_to_date,
                                "utilization_rate": utilization,
                                "start_date": start_date.isoformat(),
                                "end_date": end_date.isoformat(),
                                "signed_date": signed_date.isoformat(),
                                "payment_terms": payment_terms,
                                "auto_renewal": auto_renewal,
                                "compliance_status": compliance_status,
                                "vendor_performance": vendor_performance,
                                "contract_url": contract_url if contract_url else None,
                                "breach_notes": breach_notes if breach_notes else None,
                                "is_multi_year": False,
                                "status": status,
                                "days_remaining": days_left,
                                "budget_alert": utilization >= 80,
                                "department_id": st.session_state.user_dept
                            }
                            success, message = add_enhanced_contract(contract_data)
                        
                        if success:
                            st.success(f"✅ {message}")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
                else:
                    st.error("Please fill all required fields (*)")
    
    with tab_update:
        st.markdown("### Update Existing Contract")
        st.info("You can update active contracts and contracts that are expiring soon. Expired contracts cannot be modified.")
        
        contracts = get_cached_contracts(st.session_state.user_role, st.session_state.user_dept)
        if contracts:
            updatable_contracts = [c for c in contracts if c.get('status') in ['active', 'expiring_soon']]
            
            if updatable_contracts:
                contract_options = {c["id"]: f"{c['contract_title']} - {c['vendor_name']} ({c.get('status', 'unknown')})" for c in updatable_contracts}
                selected_contract_id = st.selectbox("Select Contract to Update", list(contract_options.keys()), format_func=lambda x: contract_options[x])
                
                if selected_contract_id:
                    selected_contract = next((c for c in updatable_contracts if c["id"] == selected_contract_id), None)
                    
                    if selected_contract:
                        with st.form("update_contract_form"):
                            st.markdown(f"#### Updating: {selected_contract['contract_title']}")
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                new_amount_spent = st.number_input("Amount Spent to Date (KES)", 
                                                                  min_value=0.0, 
                                                                  value=float(selected_contract.get('amount_spent_to_date', 0)),
                                                                  step=10000.0, 
                                                                  format="%.2f")
                                new_compliance = st.selectbox("Compliance Status", 
                                                             ["Fully Compliant", "Partially Compliant", "Non-Compliant"],
                                                             index=["Fully Compliant", "Partially Compliant", "Non-Compliant"].index(selected_contract.get('compliance_status', 'Fully Compliant')))
                                new_performance = st.slider("Vendor Performance Rating", 0.0, 5.0, 
                                                           value=float(selected_contract.get('vendor_performance', 3.0)), 
                                                           step=0.5)
                            
                            with col2:
                                new_breach_notes = st.text_area("Breach/Compliance Notes", 
                                                                value=selected_contract.get('breach_notes', ''),
                                                                height=100)
                                st.caption(f"Current Status: {selected_contract.get('status', 'unknown')}")
                                st.caption(f"Current Utilization: {selected_contract.get('utilization_rate', 0):.1f}%")
                            
                            if st.form_submit_button("Update Contract", use_container_width=True):
                                contract_value = selected_contract.get('contract_value', 0)
                                new_utilization = (new_amount_spent / contract_value * 100) if contract_value > 0 else 0
                                new_budget_alert = new_utilization >= 80
                                
                                update_data = {
                                    "amount_spent_to_date": new_amount_spent,
                                    "utilization_rate": new_utilization,
                                    "budget_alert": new_budget_alert,
                                    "compliance_status": new_compliance,
                                    "vendor_performance": new_performance,
                                    "breach_notes": new_breach_notes if new_breach_notes else None,
                                    "updated_at": datetime.now().isoformat()
                                }
                                
                                if update_contract_user(selected_contract_id, update_data):
                                    st.success("✅ Contract updated successfully!")
                                    add_audit_log("UPDATE", "contract", selected_contract_id, f"User updated contract: spent={new_amount_spent}, compliance={new_compliance}")
                                    st.rerun()
                                else:
                                    st.error("Failed to update contract")
            else:
                st.info("No updatable contracts found. Only active and expiring soon contracts can be updated.")
        else:
            st.info("No contracts found.")

# ============================================
# POLICIES SECTION (User View)
# ============================================
elif choice == "📋 Policies":
    st.subheader("Policy Management")
    
    tab_add, tab_view, tab_analytics = st.tabs(["➕ Add New Policy", "📋 View All Policies", "📊 Analytics Dashboard"])
    
    with tab_add:
        st.markdown("### Add New Policy")
        
        departments = get_cached_departments()
        dept_options = [d["name"] for d in departments]
        
        with st.form("user_add_policy_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                policy_name = st.text_input("Policy Name*")
                category = st.selectbox("Policy Category*", POLICY_CATEGORIES)
                version = st.text_input("Version*", value="v1.0")
                policy_scope = st.selectbox("Policy Scope*", POLICY_SCOPE)
                policy_owner = st.text_input("Policy Owner*")
                
            with col2:
                effective_date = st.date_input("Effective Date*", value=datetime.now().date())
                expiry_date = st.date_input("Expiry Date*")
                review_date = st.date_input("Next Review Date*")
                policy_url = st.text_input("Policy Document URL", placeholder="https://...")
            
            st.markdown("#### Scope Details")
            if policy_scope == "Institution-Wide":
                st.info("This policy applies to the entire institution")
                affected_entities = "All Departments"
            elif policy_scope == "Committee":
                committee_name = st.text_input("Committee Name")
                affected_entities = f"Committee: {committee_name}" if committee_name else "Committee"
            else:
                affected_depts = st.multiselect("Affected Departments", dept_options)
                affected_entities = ", ".join(affected_depts) if affected_depts else "Not specified"
            
            st.markdown("#### Compliance Tracking")
            requires_acknowledgment = st.checkbox("Requires Staff Acknowledgment", value=True)
            requires_sensitization = st.checkbox("Requires Sensitization", value=True)
            change_log = st.text_area("Change Log / Summary", height=80)
            
            if st.form_submit_button("Save Policy", use_container_width=True):
                if policy_name and category and policy_owner and expiry_date:
                    policy_data = {
                        "policy_name": policy_name,
                        "category": category,
                        "version": version,
                        "policy_scope": policy_scope,
                        "affected_entities": affected_entities,
                        "policy_owner": policy_owner,
                        "effective_date": effective_date.isoformat(),
                        "expiry_date": expiry_date.isoformat(),
                        "review_date": review_date.isoformat(),
                        "policy_url": policy_url if policy_url else None,
                        "requires_acknowledgment": requires_acknowledgment,
                        "requires_sensitization": requires_sensitization,
                        "change_log": change_log,
                        "department_id": st.session_state.user_dept,
                        "created_by": st.session_state.user_id
                    }
                    
                    success, message = add_enhanced_policy(policy_data)
                    if success:
                        st.success(f"✅ {message}")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
                else:
                    st.error("Please fill all required fields (*)")
    
    with tab_view:
        policies = get_cached_policies(st.session_state.user_role, st.session_state.user_dept)
        if policies:
            for policy in policies:
                expiry = datetime.strptime(policy["expiry_date"], "%Y-%m-%d").date()
                days_left = (expiry - datetime.now().date()).days
                
                if days_left > 90:
                    status_class = "status-active"
                    status_text = "Active"
                elif days_left > 0:
                    status_class = "status-expiring"
                    status_text = f"Expires in {days_left} days"
                else:
                    status_class = "status-expired"
                    status_text = "Expired"
                
                category = policy.get('category', 'Uncategorized')
                policy_scope = policy.get('policy_scope', 'Not specified')
                version = policy.get('version', 'v1.0')
                owner = policy.get('policy_owner', 'Not assigned')
                review_date = policy.get('review_date', 'Not scheduled')
                
                st.markdown(f"""
                <div class='policy-card'>
                    <div style='display: flex; justify-content: space-between; align-items: flex-start;'>
                        <div style='flex: 1;'>
                            <div class='policy-title'>📜 {policy['policy_name']} (v{version})</div>
                            <div class='policy-detail'><strong>Category:</strong> {category} | <strong>Scope:</strong> {policy_scope}</div>
                            <div class='policy-detail'><strong>Owner:</strong> {owner} | <strong>Next Review:</strong> {review_date}</div>
                            <div class='policy-detail'><strong>Effective:</strong> {policy.get('effective_date', 'N/A')} | <strong>Expires:</strong> {policy['expiry_date']}</div>
                            {f'<div class="policy-detail"><strong>Summary:</strong> {policy.get("change_log", "")[:100]}...</div>' if policy.get('change_log') else ''}
                        </div>
                        <div style='text-align: right;'>
                            <span class='status-badge {status_class}'>{status_text}</span>
                            {f'<div style="margin-top: 0.5rem;"><a href="{policy["policy_url"]}" target="_blank" style="font-size: 0.7rem;">📄 View Document</a></div>' if policy.get('policy_url') else ''}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No policies found. Click 'Add New Policy' to get started.")
    
    with tab_analytics:
        policies = get_cached_policies(st.session_state.user_role, st.session_state.user_dept)
        if policies:
            df = pd.DataFrame(policies)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-label'>📜 TOTAL POLICIES</div>
                    <div class='kpi-value'>{len(df)}</div>
                    <div class='kpi-sub'>All Policies</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                active = len(df[df['status'] == 'active'])
                st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-label'>✅ ACTIVE</div>
                    <div class='kpi-value'>{active}</div>
                    <div class='kpi-sub'>Currently Active</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                expiring = len(df[df['status'] == 'expiring_soon'])
                st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-label'>⚠️ EXPIRING SOON</div>
                    <div class='kpi-value'>{expiring}</div>
                    <div class='kpi-sub'>Within 90 days</div>
                </div>
                """, unsafe_allow_html=True)
            with col4:
                expired = len(df[df['status'] == 'expired'])
                st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-label'>🔴 EXPIRED</div>
                    <div class='kpi-value'>{expired}</div>
                    <div class='kpi-sub'>Needs Review</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            col_chart1, col_chart2 = st.columns(2)
            with col_chart1:
                if 'category' in df.columns:
                    st.markdown("#### Policies by Category")
                    category_counts = df['category'].value_counts().reset_index()
                    category_counts.columns = ['Category', 'Count']
                    fig = px.pie(category_counts, values='Count', names='Category', hole=0.4,
                                color_discrete_sequence=[HELB_GREEN, HELB_GOLD, HELB_BLUE, "#8B5CF6", "#10B981"])
                    fig.update_layout(height=350)
                    st.plotly_chart(fig, use_container_width=True)
            
            with col_chart2:
                if 'policy_scope' in df.columns:
                    st.markdown("#### Policy Scope Distribution")
                    scope_counts = df['policy_scope'].value_counts().reset_index()
                    scope_counts.columns = ['Scope', 'Count']
                    fig = px.bar(scope_counts, x='Scope', y='Count', color='Count',
                               color_discrete_sequence=[HELB_GREEN], text='Count')
                    fig.update_traces(textposition='outside')
                    fig.update_layout(height=350)
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No policy data available for analytics.")

# ============================================
# ADMIN PANEL (Admin Only)
# ============================================
elif choice == "⚙️ Admin Panel" and st.session_state.user_role == "admin":
    st.markdown("<h2>⚙️ Administration Panel</h2>", unsafe_allow_html=True)
    st.markdown("Manage users, policies, contracts, work plans, departments, and directorates from one central location.")
    
    admin_tabs = st.tabs([
        "👥 User Management", 
        "📜 Policy Management", 
        "📄 Contract Management", 
        "📋 Work Plan Management",
        "🏢 Department Management",
        "🏛️ Directorate Management",
        "📋 Audit Log"
    ])
    
    # ========== TAB 1: USER MANAGEMENT ==========
    with admin_tabs[0]:
        st.markdown("### 👥 User Management")
        
        directorates = get_cached_directorates()
        directorate_options = {d["name"]: d["id"] for d in directorates}
        departments = get_cached_departments()
        dept_options = {d["name"]: d["id"] for d in departments}
        users = get_all_users()
        
        col1, col2 = st.columns(2)
        
        with col1:
            with st.expander("➕ Create New User", expanded=False):
                with st.form("admin_create_user"):
                    st.markdown("#### Create User Account")
                    new_username = st.text_input("Username*")
                    new_full_name = st.text_input("Full Name*")
                    new_role = st.selectbox("Role*", ["department_champion", "management", "admin"])
                    new_department = st.selectbox("Department", ["None"] + list(dept_options.keys()))
                    new_password = st.text_input("Password*", type="password")
                    confirm_password = st.text_input("Confirm Password*", type="password")
                    
                    if st.form_submit_button("Create User", use_container_width=True):
                        if new_password != confirm_password:
                            st.error("Passwords don't match")
                        elif not all([new_username, new_full_name, new_password]):
                            st.error("Please fill all required fields")
                        else:
                            dept_id = dept_options.get(new_department) if new_department != "None" else None
                            success, message = create_new_user(new_username, new_full_name, new_password, new_role, dept_id)
                            if success:
                                st.success(f"✅ {message}")
                                st.info(f"Username: {new_username} | Password: {new_password}")
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")
        
        with col2:
            with st.expander("✏️ Edit User", expanded=False):
                st.markdown("#### Edit User Role and Department")
                if users:
                    user_options = [f"{u['username']} - {u['full_name']}" for u in users if u['username'] != "admin"]
                    if user_options:
                        selected_user_str = st.selectbox("Select User to Edit", user_options, key="admin_edit_user")
                        selected_username = selected_user_str.split(" - ")[0]
                        
                        current_user = next((u for u in users if u['username'] == selected_username), None)
                        if current_user:
                            new_role = st.selectbox("New Role", ["department_champion", "management", "admin"], 
                                                   index=["department_champion", "management", "admin"].index(current_user['role']))
                            current_dept = get_department_name(current_user['department_id'])
                            dept_list = ["None"] + list(dept_options.keys())
                            default_index = dept_list.index(current_dept) if current_dept in dept_list else 0
                            new_department = st.selectbox("Department", dept_list, index=default_index)
                            
                            reset_password = st.checkbox("Reset Password")
                            new_password = None
                            if reset_password:
                                new_password = st.text_input("New Password", type="password")
                                confirm_new = st.text_input("Confirm New Password", type="password")
                            
                            if st.button("Save Changes", use_container_width=True):
                                dept_id = dept_options.get(new_department) if new_department != "None" else None
                                if update_user_role(selected_username, new_role, dept_id):
                                    st.success(f"✅ Role and department updated for {selected_username}")
                                else:
                                    st.error("Failed to update role/department")
                                
                                if reset_password and new_password:
                                    if new_password == confirm_new and len(new_password) >= 4:
                                        if reset_user_password(selected_username, new_password):
                                            st.success(f"✅ Password reset for {selected_username}")
                                            st.info(f"New password: {new_password}")
                                        else:
                                            st.error("Failed to reset password")
                                    else:
                                        st.error("Passwords don't match or are too short")
                                st.rerun()
        
        with st.expander("🗑️ Delete User", expanded=False):
            st.warning("⚠️ Deleting a user is permanent and cannot be undone!")
            if users:
                delete_options = [f"{u['username']} - {u['full_name']}" for u in users if u['username'] != "admin"]
                if delete_options:
                    user_to_delete = st.selectbox("Select User to Delete", delete_options, key="admin_delete_user")
                    delete_username = user_to_delete.split(" - ")[0]
                    confirm = st.checkbox(f"I understand that this will permanently delete user '{delete_username}'")
                    
                    if st.button("🗑️ Delete User", use_container_width=True):
                        if confirm:
                            if delete_user(delete_username):
                                st.success(f"✅ User '{delete_username}' has been deleted!")
                                st.rerun()
                            else:
                                st.error(f"❌ Failed to delete user '{delete_username}'")
                        else:
                            st.error("Please confirm deletion")
        
        st.markdown("---")
        st.markdown("### Current Users")
        if users:
            user_display = []
            for user in users:
                dept_name = get_department_name(user['department_id']) if user['department_id'] else "N/A"
                user_display.append({
                    "Username": user['username'],
                    "Full Name": user['full_name'],
                    "Role": user['role'].replace("_", " ").title(),
                    "Department": dept_name
                })
            df_users = pd.DataFrame(user_display)
            st.dataframe(df_users, use_container_width=True, hide_index=True)
    
    # ========== TAB 2: POLICY MANAGEMENT ==========
    with admin_tabs[1]:
        st.markdown("### 📜 Policy Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            with st.expander("➕ Add New Policy", expanded=False):
                with st.form("admin_add_policy"):
                    st.markdown("#### Policy Details")
                    policy_name = st.text_input("Policy Name*")
                    category = st.selectbox("Policy Category*", POLICY_CATEGORIES)
                    version = st.text_input("Version*", value="v1.0")
                    policy_scope = st.selectbox("Policy Scope*", POLICY_SCOPE)
                    policy_owner = st.text_input("Policy Owner*")
                    
                    effective_date = st.date_input("Effective Date*", value=datetime.now().date())
                    expiry_date = st.date_input("Expiry Date*")
                    review_date = st.date_input("Next Review Date*")
                    policy_url = st.text_input("Policy Document URL", placeholder="https://...")
                    
                    st.markdown("#### Scope Details")
                    if policy_scope == "Institution-Wide":
                        st.info("This policy applies to the entire institution")
                        affected_entities = "All Departments"
                    elif policy_scope == "Committee":
                        committee_name = st.text_input("Committee Name")
                        affected_entities = f"Committee: {committee_name}" if committee_name else "Committee"
                    else:
                        departments_list = get_cached_departments()
                        dept_options_list = [d["name"] for d in departments_list]
                        affected_depts = st.multiselect("Affected Departments", dept_options_list)
                        affected_entities = ", ".join(affected_depts) if affected_depts else "Not specified"
                    
                    st.markdown("#### Compliance Tracking")
                    requires_acknowledgment = st.checkbox("Requires Staff Acknowledgment", value=True)
                    requires_sensitization = st.checkbox("Requires Sensitization", value=True)
                    change_log = st.text_area("Change Log / Summary", height=80)
                    
                    if st.form_submit_button("Save Policy", use_container_width=True):
                        if policy_name and category and policy_owner:
                            policy_data = {
                                "policy_name": policy_name,
                                "category": category,
                                "version": version,
                                "policy_scope": policy_scope,
                                "affected_entities": affected_entities,
                                "policy_owner": policy_owner,
                                "effective_date": effective_date.isoformat(),
                                "expiry_date": expiry_date.isoformat(),
                                "review_date": review_date.isoformat(),
                                "policy_url": policy_url if policy_url else None,
                                "requires_acknowledgment": requires_acknowledgment,
                                "requires_sensitization": requires_sensitization,
                                "change_log": change_log,
                                "department_id": None if policy_scope != "Department-Specific" else None,
                                "created_by": st.session_state.user_id
                            }
                            success, message = add_enhanced_policy(policy_data)
                            if success:
                                st.success(f"✅ {message}")
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")
                        else:
                            st.error("Please fill all required fields (*)")
        
        with col2:
            with st.expander("✏️ Edit / Delete Policy", expanded=False):
                st.markdown("#### Select Policy to Manage")
                policies = get_cached_policies("admin", None)
                if policies:
                    policy_options = {p["id"]: f"{p['policy_name']} (v{p.get('version', '1.0')})" for p in policies}
                    selected_policy_id = st.selectbox("Select Policy", list(policy_options.keys()), format_func=lambda x: policy_options[x], key="admin_edit_policy")
                    
                    if selected_policy_id:
                        selected_policy = next((p for p in policies if p["id"] == selected_policy_id), None)
                        if selected_policy:
                            action = st.radio("Action", ["Edit Policy", "Delete Policy"], horizontal=True)
                            
                            if action == "Edit Policy":
                                with st.form("admin_edit_policy_form"):
                                    edit_name = st.text_input("Policy Name", value=selected_policy.get("policy_name", ""))
                                    edit_category = st.selectbox("Category", POLICY_CATEGORIES, index=POLICY_CATEGORIES.index(selected_policy.get("category", "HR")) if selected_policy.get("category") in POLICY_CATEGORIES else 0)
                                    edit_version = st.text_input("Version", value=selected_policy.get("version", "v1.0"))
                                    edit_owner = st.text_input("Policy Owner", value=selected_policy.get("policy_owner", ""))
                                    edit_expiry = st.date_input("Expiry Date", value=datetime.strptime(selected_policy["expiry_date"], "%Y-%m-%d").date())
                                    edit_review = st.date_input("Review Date", value=datetime.strptime(selected_policy.get("review_date", selected_policy["expiry_date"]), "%Y-%m-%d").date())
                                    
                                    if st.form_submit_button("Update Policy", use_container_width=True):
                                        update_data = {
                                            "policy_name": edit_name,
                                            "category": edit_category,
                                            "version": edit_version,
                                            "policy_owner": edit_owner,
                                            "expiry_date": edit_expiry.isoformat(),
                                            "review_date": edit_review.isoformat(),
                                            "updated_at": datetime.now().isoformat()
                                        }
                                        if update_policy_admin(selected_policy_id, update_data):
                                            st.success("✅ Policy updated successfully!")
                                            st.rerun()
                                        else:
                                            st.error("Failed to update policy")
                            
                            elif action == "Delete Policy":
                                st.warning(f"⚠️ Are you sure you want to delete '{selected_policy['policy_name']}'?")
                                if st.button("Confirm Delete", use_container_width=True):
                                    if delete_policy(selected_policy_id):
                                        st.success("✅ Policy deleted successfully!")
                                        st.rerun()
                                    else:
                                        st.error("Failed to delete policy")
                else:
                    st.info("No policies found")
        
        st.markdown("---")
        st.markdown("### All Policies")
        all_policies = get_cached_policies("admin", None)
        if all_policies:
            df_policies_admin = pd.DataFrame(all_policies)
            display_cols = ['policy_name', 'category', 'version', 'policy_scope', 'policy_owner', 'status', 'expiry_date']
            st.dataframe(df_policies_admin[display_cols], use_container_width=True, hide_index=True)
    
    # ========== TAB 3: CONTRACT MANAGEMENT ==========
    with admin_tabs[2]:
        st.markdown("### 📄 Contract Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            with st.expander("➕ Add New Contract", expanded=False):
                with st.form("admin_add_contract"):
                    st.markdown("#### Contract Details")
                    title = st.text_input("Contract Title*")
                    vendor = st.text_input("Vendor Name*")
                    contract_duration = st.selectbox("Contract Duration", ["3 months", "6 months", "1 year", "2 years", "3 years", "4 years", "5 years"])
                    contract_value = st.number_input("Contract Value (KES)*", min_value=0.0, step=10000.0, format="%.2f")
                    amount_spent = st.number_input("Initial Amount Spent (KES)", min_value=0.0, step=10000.0, format="%.2f", value=0.0)
                    payment_terms = st.selectbox("Payment Terms", PAYMENT_TERMS)
                    end_date = st.date_input("Contract End Date*")
                    signed_date = st.date_input("Signed Date", value=datetime.now().date())
                    auto_renew = st.checkbox("Auto-renewal")
                    contract_url = st.text_input("Contract Document URL", placeholder="https://...")
                    compliance_status = st.selectbox("Compliance Status", ["Fully Compliant", "Partially Compliant", "Non-Compliant"])
                    vendor_performance = st.slider("Vendor Performance Rating", 0.0, 5.0, 3.0, 0.5)
                    breach_notes = st.text_area("Breach/Compliance Notes", height=60)
                    department_id = st.selectbox("Department", ["None"] + list(dept_options.keys()))
                    
                    if st.form_submit_button("Save Contract", use_container_width=True):
                        if title and vendor and contract_value > 0 and end_date:
                            dept_id = dept_options.get(department_id) if department_id != "None" else None
                            contract_data = {
                                "contract_title": title,
                                "vendor_name": vendor,
                                "contract_duration": contract_duration,
                                "contract_value": contract_value,
                                "total_contract_value": contract_value,
                                "amount_spent_to_date": amount_spent,
                                "payment_terms": payment_terms,
                                "start_date": datetime.now().date().isoformat(),
                                "end_date": end_date.isoformat(),
                                "signed_date": signed_date.isoformat(),
                                "auto_renewal": auto_renew,
                                "contract_url": contract_url if contract_url else None,
                                "compliance_status": compliance_status,
                                "vendor_performance": vendor_performance,
                                "breach_notes": breach_notes if breach_notes else None,
                                "is_multi_year": False,
                                "department_id": dept_id
                            }
                            success, message = add_enhanced_contract(contract_data)
                            if success:
                                st.success(f"✅ {message}")
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")
                        else:
                            st.error("Please fill all required fields (*)")
        
        with col2:
            with st.expander("✏️ Edit / Delete Contract", expanded=False):
                st.markdown("#### Select Contract to Manage")
                contracts = get_cached_contracts("admin", None)
                if contracts:
                    contract_options = {c["id"]: f"{c['contract_title']} - {c['vendor_name']}" for c in contracts}
                    selected_contract_id = st.selectbox("Select Contract", list(contract_options.keys()), format_func=lambda x: contract_options[x], key="admin_edit_contract")
                    
                    if selected_contract_id:
                        selected_contract = next((c for c in contracts if c["id"] == selected_contract_id), None)
                        if selected_contract:
                            action = st.radio("Action", ["Edit Contract", "Delete Contract"], horizontal=True)
                            
                            if action == "Edit Contract":
                                with st.form("admin_edit_contract_form"):
                                    edit_title = st.text_input("Contract Title", value=selected_contract.get("contract_title", ""))
                                    edit_vendor = st.text_input("Vendor", value=selected_contract.get("vendor_name", ""))
                                    edit_value = st.number_input("Contract Value", value=float(selected_contract.get("contract_value", 0)))
                                    edit_spent = st.number_input("Amount Spent", value=float(selected_contract.get("amount_spent_to_date", 0)))
                                    edit_end_date = st.date_input("End Date", value=datetime.strptime(selected_contract["end_date"], "%Y-%m-%d").date())
                                    edit_status = st.selectbox("Status", ["active", "expiring_soon", "expired"], index=["active", "expiring_soon", "expired"].index(selected_contract.get("status", "active")))
                                    edit_compliance = st.selectbox("Compliance Status", ["Fully Compliant", "Partially Compliant", "Non-Compliant"], 
                                                                  index=["Fully Compliant", "Partially Compliant", "Non-Compliant"].index(selected_contract.get("compliance_status", "Fully Compliant")))
                                    edit_performance = st.slider("Vendor Performance", 0.0, 5.0, float(selected_contract.get("vendor_performance", 3.0)), 0.5)
                                    
                                    if st.form_submit_button("Update Contract", use_container_width=True):
                                        update_data = {
                                            "contract_title": edit_title,
                                            "vendor_name": edit_vendor,
                                            "contract_value": edit_value,
                                            "amount_spent_to_date": edit_spent,
                                            "end_date": edit_end_date.isoformat(),
                                            "status": edit_status,
                                            "compliance_status": edit_compliance,
                                            "vendor_performance": edit_performance,
                                            "updated_at": datetime.now().isoformat()
                                        }
                                        if update_contract_admin(selected_contract_id, update_data):
                                            st.success("✅ Contract updated successfully!")
                                            st.rerun()
                                        else:
                                            st.error("Failed to update contract")
                            
                            elif action == "Delete Contract":
                                st.warning(f"⚠️ Are you sure you want to delete '{selected_contract['contract_title']}'?")
                                if st.button("Confirm Delete", use_container_width=True):
                                    if delete_contract(selected_contract_id):
                                        st.success("✅ Contract deleted successfully!")
                                        st.rerun()
                                    else:
                                        st.error("Failed to delete contract")
                else:
                    st.info("No contracts found")
        
        st.markdown("---")
        st.markdown("### All Contracts")
        all_contracts = get_cached_contracts("admin", None)
        if all_contracts:
            df_contracts_admin = pd.DataFrame(all_contracts)
            display_cols = ['contract_title', 'vendor_name', 'contract_value', 'amount_spent_to_date', 'status', 'end_date', 'compliance_status', 'vendor_performance', 'is_multi_year']
            st.dataframe(df_contracts_admin[display_cols], use_container_width=True, hide_index=True)
    
    # ========== TAB 4: WORK PLAN MANAGEMENT ==========
    with admin_tabs[3]:
        st.markdown("### 📋 Work Plan Management")
        
        work_plans = get_cached_work_plans("admin", None)
        
        col1, col2 = st.columns(2)
        
        with col1:
            with st.expander("➕ Add New Work Plan Activity", expanded=False):
                with st.form("admin_add_workplan"):
                    st.markdown("#### Work Plan Details")
                    strategic_pillar = st.selectbox("Strategic Pillar*", STRATEGIC_PILLARS)
                    key_result_area = st.text_input("Key Result Area*")
                    planned_activity = st.text_area("Planned Activity*")
                    performance_indicator = st.text_input("Performance Indicator*")
                    annual_target = st.text_input("Annual Target*")
                    due_date = st.date_input("Due Date*")
                    activity_category = st.selectbox("Activity Category*", ACTIVITY_CATEGORIES)
                    budget_allocation = st.number_input("Budget Allocation (KES)", min_value=0.0, step=10000.0, format="%.2f")
                    department = st.selectbox("Department", ["None"] + list(dept_options.keys()))
                    
                    if st.form_submit_button("Save Work Plan", use_container_width=True):
                        if key_result_area and planned_activity and performance_indicator and annual_target:
                            dept_id = dept_options.get(department) if department != "None" else None
                            dept_name = department if department != "None" else "Unknown"
                            work_plan_data = {
                                "strategic_pillar": strategic_pillar,
                                "key_result_area": key_result_area,
                                "planned_activity": planned_activity,
                                "performance_indicator": performance_indicator,
                                "annual_target": annual_target,
                                "due_date": due_date.isoformat(),
                                "activity_category": activity_category,
                                "budget_allocation": budget_allocation if budget_allocation > 0 else None,
                                "actual_achievement": 0,
                                "status": "Pending",
                                "progress_percent": 0,
                                "department_id": dept_id,
                                "department_name": dept_name,
                                "created_by": st.session_state.user_id,
                                "created_at": datetime.now().isoformat()
                            }
                            if add_work_plan(work_plan_data):
                                st.success("✅ Work plan activity added successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to add work plan")
                        else:
                            st.error("Please fill all required fields (*)")
        
        with col2:
            with st.expander("✏️ Edit / Delete Work Plan", expanded=False):
                st.markdown("#### Select Work Plan to Manage")
                if work_plans:
                    wp_options = {w["id"]: f"{w['planned_activity'][:50]}... - {w.get('department_name', 'Unknown')}" for w in work_plans}
                    selected_wp_id = st.selectbox("Select Work Plan", list(wp_options.keys()), format_func=lambda x: wp_options[x], key="admin_edit_workplan")
                    
                    if selected_wp_id:
                        selected_wp = next((w for w in work_plans if w["id"] == selected_wp_id), None)
                        if selected_wp:
                            action = st.radio("Action", ["Edit Work Plan", "Delete Work Plan"], horizontal=True)
                            
                            if action == "Edit Work Plan":
                                with st.form("admin_edit_workplan_form"):
                                    edit_activity = st.text_area("Planned Activity", value=selected_wp.get("planned_activity", ""))
                                    edit_target = st.text_input("Annual Target", value=selected_wp.get("annual_target", ""))
                                    edit_due_date = st.date_input("Due Date", value=datetime.strptime(selected_wp["due_date"], "%Y-%m-%d").date())
                                    edit_progress = st.number_input("Progress %", min_value=0, max_value=100, value=int(selected_wp.get("progress_percent", 0)))
                                    edit_status = st.selectbox("Status", ["Pending", "In Progress", "Done"], index=["Pending", "In Progress", "Done"].index(selected_wp.get("status", "Pending")))
                                    edit_actual = st.number_input("Actual Achievement", value=float(selected_wp.get("actual_achievement", 0)))
                                    
                                    if st.form_submit_button("Update Work Plan", use_container_width=True):
                                        update_data = {
                                            "planned_activity": edit_activity,
                                            "annual_target": edit_target,
                                            "due_date": edit_due_date.isoformat(),
                                            "progress_percent": edit_progress,
                                            "status": edit_status,
                                            "actual_achievement": edit_actual,
                                            "updated_at": datetime.now().isoformat()
                                        }
                                        if update_work_plan_admin(selected_wp_id, update_data):
                                            st.success("✅ Work plan updated successfully!")
                                            st.rerun()
                                        else:
                                            st.error("Failed to update work plan")
                            
                            elif action == "Delete Work Plan":
                                st.warning(f"⚠️ Are you sure you want to delete this activity?")
                                if st.button("Confirm Delete", use_container_width=True):
                                    if delete_work_plan(selected_wp_id):
                                        st.success("✅ Work plan deleted successfully!")
                                        st.rerun()
                                    else:
                                        st.error("Failed to delete work plan")
                else:
                    st.info("No work plans found")
        
        st.markdown("---")
        st.markdown("### All Work Plans")
        if work_plans:
            df_wp_admin = pd.DataFrame(work_plans)
            display_cols = ['planned_activity', 'department_name', 'annual_target', 'progress_percent', 'status', 'due_date']
            st.dataframe(df_wp_admin[display_cols], use_container_width=True, hide_index=True)
    
    # ========== TAB 5: DEPARTMENT MANAGEMENT ==========
    with admin_tabs[4]:
        st.markdown("### 🏢 Department Management")
        
        directorates = get_cached_directorates()
        directorate_options = {d["name"]: d["id"] for d in directorates}
        departments = get_cached_departments()
        
        col1, col2 = st.columns(2)
        
        with col1:
            with st.expander("➕ Add New Department", expanded=False):
                with st.form("admin_add_department"):
                    new_dept_name = st.text_input("Department Name*")
                    new_dept_directorate = st.selectbox("Directorate*", ["None"] + list(directorate_options.keys()))
                    new_dept_deputy = st.text_input("Deputy Director Name")
                    
                    if st.form_submit_button("Add Department", use_container_width=True):
                        if new_dept_name:
                            directorate_id = directorate_options.get(new_dept_directorate) if new_dept_directorate != "None" else None
                            success, message = add_department(new_dept_name, directorate_id, new_dept_deputy)
                            if success:
                                st.success(f"✅ {message}")
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")
                        else:
                            st.error("Please enter a department name")
        
        with col2:
            with st.expander("✏️ Edit Department", expanded=False):
                if departments:
                    dept_names = [d["name"] for d in departments]
                    selected_dept_name = st.selectbox("Select Department to Edit", dept_names, key="admin_edit_dept")
                    
                    if selected_dept_name:
                        selected_dept = next((d for d in departments if d["name"] == selected_dept_name), None)
                        if selected_dept:
                            with st.form("admin_edit_dept_form"):
                                edit_dept_name = st.text_input("Department Name", value=selected_dept["name"])
                                current_dir_name = ""
                                if selected_dept.get("directorate_id"):
                                    dir_info = get_directorate_by_id(selected_dept["directorate_id"])
                                    if dir_info:
                                        current_dir_name = dir_info["name"]
                                edit_dept_directorate = st.selectbox("Directorate", ["None"] + list(directorate_options.keys()), 
                                                                     index=0 if not current_dir_name else list(directorate_options.keys()).index(current_dir_name) + 1)
                                edit_dept_deputy = st.text_input("Deputy Director Name", value=selected_dept.get("deputy_director_name", ""))
                                
                                if st.form_submit_button("Update Department", use_container_width=True):
                                    directorate_id = directorate_options.get(edit_dept_directorate) if edit_dept_directorate != "None" else None
                                    success, message = update_department(selected_dept["id"], edit_dept_name, directorate_id, edit_dept_deputy)
                                    if success:
                                        st.success(f"✅ {message}")
                                        st.rerun()
                                    else:
                                        st.error(f"❌ {message}")
        
        st.markdown("---")
        st.markdown("### Existing Departments")
        if departments:
            for dept in departments:
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    directorate_info = ""
                    if dept.get("directorate_id"):
                        dir_info = get_directorate_by_id(dept["directorate_id"])
                        if dir_info:
                            directorate_info = f" ({dir_info['name']})"
                    deputy_info = f"\nDeputy: {dept.get('deputy_director_name', 'Not assigned')}" if dept.get('deputy_director_name') else ""
                    st.write(f"• {dept['name']}{directorate_info}{deputy_info}")
                with col3:
                    if dept['name'] not in ["Lending", "Strategy", "Finance", "ICT", "Human Resource"]:
                        if st.button(f"🗑️ Delete", key=f"admin_del_dept_{dept['id']}"):
                            success, message = delete_department(dept['id'])
                            if success:
                                st.success(f"✅ {message}")
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")
        else:
            st.info("No departments found")
    
    # ========== TAB 6: DIRECTORATE MANAGEMENT ==========
    with admin_tabs[5]:
        st.markdown("### 🏛️ Directorate Management")
        
        directorates = get_cached_directorates()
        
        col1, col2 = st.columns(2)
        
        with col1:
            with st.expander("➕ Add New Directorate", expanded=False):
                with st.form("admin_add_directorate"):
                    new_dir_name = st.text_input("Directorate Name*")
                    new_dir_director = st.text_input("Director Name*")
                    
                    if st.form_submit_button("Add Directorate", use_container_width=True):
                        if new_dir_name and new_dir_director:
                            success, message = add_directorate(new_dir_name, new_dir_director)
                            if success:
                                st.success(f"✅ {message}")
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")
                        else:
                            st.error("Please fill all required fields")
        
        with col2:
            with st.expander("✏️ Edit Directorate", expanded=False):
                if directorates:
                    dir_names = [d["name"] for d in directorates]
                    selected_dir_name = st.selectbox("Select Directorate to Edit", dir_names, key="admin_edit_dir")
                    
                    if selected_dir_name:
                        selected_dir = next((d for d in directorates if d["name"] == selected_dir_name), None)
                        if selected_dir:
                            with st.form("admin_edit_dir_form"):
                                edit_dir_name = st.text_input("Directorate Name", value=selected_dir["name"])
                                edit_dir_director = st.text_input("Director Name", value=selected_dir.get("director_name", ""))
                                
                                if st.form_submit_button("Update Directorate", use_container_width=True):
                                    success, message = update_directorate(selected_dir["id"], edit_dir_name, edit_dir_director)
                                    if success:
                                        st.success(f"✅ {message}")
                                        st.rerun()
                                    else:
                                        st.error(f"❌ {message}")
        
        st.markdown("---")
        st.markdown("### Existing Directorates")
        if directorates:
            departments = get_cached_departments()
            for dir_item in directorates:
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"• **{dir_item['name']}** - Director: {dir_item.get('director_name', 'Not assigned')}")
                with col2:
                    dept_count = len([d for d in departments if d.get('directorate_id') == dir_item['id']])
                    st.caption(f"{dept_count} departments")
                with col3:
                    if dir_item['name'] not in ["Operations", "Human Resource & Administration", "Fund Management", "ICT", "CEO's Office"]:
                        if st.button(f"🗑️ Delete", key=f"admin_del_dir_{dir_item['id']}"):
                            success, message = delete_directorate(dir_item['id'])
                            if success:
                                st.success(f"✅ {message}")
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")
        else:
            st.info("No directorates found")
    
    # ========== TAB 7: AUDIT LOG ==========
    with admin_tabs[6]:
        st.markdown("### 📋 Audit Log")
        st.markdown("Track all user activities and system changes")
        
        audit_logs = get_audit_logs(500)
        
        if audit_logs:
            df_audit = pd.DataFrame(audit_logs)
            
            col_date, col_user, col_action, col_entity = st.columns(4)
            with col_date:
                date_filter = st.date_input("Filter by Date", value=None)
            with col_user:
                users_list = ["All"] + df_audit['username'].unique().tolist()
                user_filter = st.selectbox("Filter by User", users_list)
            with col_action:
                actions_list = ["All"] + df_audit['action'].unique().tolist()
                action_filter = st.selectbox("Filter by Action", actions_list)
            with col_entity:
                entities_list = ["All"] + df_audit['entity_type'].unique().tolist()
                entity_filter = st.selectbox("Filter by Entity Type", entities_list)
            
            filtered_audit = df_audit.copy()
            if date_filter:
                filtered_audit = filtered_audit[pd.to_datetime(filtered_audit['created_at']).dt.date == date_filter]
            if user_filter != "All":
                filtered_audit = filtered_audit[filtered_audit['username'] == user_filter]
            if action_filter != "All":
                filtered_audit = filtered_audit[filtered_audit['action'] == action_filter]
            if entity_filter != "All":
                filtered_audit = filtered_audit[filtered_audit['entity_type'] == entity_filter]
            
            st.markdown(f"**Showing {len(filtered_audit)} audit records**")
            
            display_cols = ['created_at', 'username', 'action', 'entity_type', 'details']
            st.dataframe(filtered_audit[display_cols], use_container_width=True, hide_index=True)
            
            csv_audit = filtered_audit.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Audit Log", csv_audit, f"audit_log_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")
        else:
            st.info("No audit logs found. The audit_logs table exists but no records have been created yet. Perform some actions (login, create contract, etc.) to generate logs.")

# ============================================
# ENTERPRISE VIEW
# ============================================
elif choice == "🏢 Enterprise View" and st.session_state.user_role in ["admin", "management"]:
    st.subheader("Enterprise Management View")
    st.markdown("### Cross-Department Performance Overview")
    
    work_plans = get_work_plans()
    
    if work_plans:
        df = pd.DataFrame(work_plans)
        df['calculated_progress'] = df.apply(lambda x: calculate_progress_from_actual(x.get('annual_target', '0'), x.get('actual_achievement', 0)), axis=1)
        
        st.markdown("#### Department Performance Summary")
        performance_data = []
        for dept in df['department_name'].unique():
            dept_df = df[df['department_name'] == dept]
            total = len(dept_df)
            completed = len(dept_df[dept_df['calculated_progress'] >= 100])
            avg_progress = dept_df['calculated_progress'].mean()
            total_budget = dept_df['budget_allocation'].fillna(0).sum()
            
            performance_data.append({
                "Department": dept,
                "Total Activities": total,
                "Completed": completed,
                "Completion Rate": f"{(completed/total*100):.0f}%" if total > 0 else "0%",
                "Avg Progress": f"{avg_progress:.0f}%",
                "Budget (KES M)": f"{total_budget/1e6:.1f}"
            })
        
        if performance_data:
            df_perf = pd.DataFrame(performance_data)
            st.dataframe(df_perf, use_container_width=True, hide_index=True)
    
    tabs = st.tabs(["All Work Plans", "All Contracts", "All Policies"])
    
    with tabs[0]:
        work_plans = get_work_plans()
        if work_plans:
            df = pd.DataFrame(work_plans)
            display_cols = ['strategic_pillar', 'key_result_area', 'planned_activity', 
                           'department_name', 'status', 'progress_percent', 'due_date']
            st.dataframe(df[display_cols], use_container_width=True, hide_index=True)
        else:
            st.info("No work plans found")
    
    with tabs[1]:
        all_contracts = get_cached_contracts(st.session_state.user_role, st.session_state.user_dept)
        if all_contracts:
            df = pd.DataFrame(all_contracts)
            display_cols = ["contract_title", "vendor_name", "contract_value", "amount_spent_to_date", "end_date", "status", "compliance_status", "is_multi_year"]
            st.dataframe(df[display_cols], use_container_width=True, hide_index=True)
        else:
            st.info("No contracts found")
    
    with tabs[2]:
        all_policies = get_cached_policies(st.session_state.user_role, st.session_state.user_dept)
        if all_policies:
            df = pd.DataFrame(all_policies)
            st.dataframe(df[["policy_name", "expiry_date", "status"]], use_container_width=True, hide_index=True)
        else:
            st.info("No policies found")

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown("""
<div class='footer'>
    <p>© 2025 HELB - Higher Education Loans Board | Strategy Performance Management System</p>

</div>
""", unsafe_allow_html=True)
