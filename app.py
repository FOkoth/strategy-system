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

# Page config
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

# Quarter to Months Mapping
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
    """Get directorate name for a given department"""
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
        return True
    except:
        return False

def delete_work_plan(plan_id):
    try:
        supabase.table("work_plan").delete().eq("id", plan_id).execute()
        st.cache_data.clear()
        return True
    except:
        return False

def get_filtered_data(table_name):
    if table_name == "contracts":
        return get_cached_contracts(st.session_state.user_role, st.session_state.user_dept)
    elif table_name == "policies":
        return get_cached_policies(st.session_state.user_role, st.session_state.user_dept)
    else:
        return []

# ============================================
# ENHANCED CONTRACT FUNCTIONS
# ============================================
def add_enhanced_contract(data):
    """Add new contract with enhanced fields"""
    try:
        # Calculate days remaining
        end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").date()
        days_left = (end_date - datetime.now().date()).days
        
        # Determine status based on days remaining and utilization
        if days_left < 0:
            status = "expired"
        elif days_left <= 30:
            status = "expiring_soon"
        else:
            status = "active"
        
        # Calculate utilization rate
        contract_value = data.get("contract_value", 0)
        amount_spent = data.get("amount_spent_to_date", 0)
        utilization_rate = (amount_spent / contract_value * 100) if contract_value > 0 else 0
        
        # Add budget alert if needed
        if utilization_rate >= 80:
            data["budget_alert"] = True
        else:
            data["budget_alert"] = False
        
        data["days_remaining"] = days_left
        data["status"] = status
        data["utilization_rate"] = utilization_rate
        
        supabase.table("contracts").insert(data).execute()
        st.cache_data.clear()
        return True, "Contract added successfully"
    except Exception as e:
        return False, str(e)

def update_contract_spending(contract_id, amount_spent):
    """Update contract spending and recalculate utilization"""
    try:
        # Get current contract
        result = supabase.table("contracts").select("*").eq("id", contract_id).execute()
        if not result.data:
            return False
        
        contract = result.data[0]
        contract_value = contract.get("contract_value", 0)
        
        # Calculate new utilization
        utilization_rate = (amount_spent / contract_value * 100) if contract_value > 0 else 0
        
        # Set budget alert
        budget_alert = utilization_rate >= 80
        
        # Update
        supabase.table("contracts").update({
            "amount_spent_to_date": amount_spent,
            "utilization_rate": utilization_rate,
            "budget_alert": budget_alert,
            "updated_at": datetime.now().isoformat()
        }).eq("id", contract_id).execute()
        
        st.cache_data.clear()
        return True
    except Exception as e:
        return False

def update_vendor_performance(contract_id, performance_rating, compliance_status, breach_notes=None):
    """Update vendor performance metrics"""
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
        return True
    except Exception as e:
        return False

def get_contracts_analytics(contracts):
    """Generate analytics data for contracts"""
    if not contracts:
        return None
    
    df = pd.DataFrame(contracts)
    
    # Convert numeric columns
    df['contract_value'] = pd.to_numeric(df.get('contract_value', 0), errors='coerce').fillna(0)
    df['amount_spent_to_date'] = pd.to_numeric(df.get('amount_spent_to_date', 0), errors='coerce').fillna(0)
    df['vendor_performance'] = pd.to_numeric(df.get('vendor_performance', 0), errors='coerce').fillna(0)
    df['utilization_rate'] = pd.to_numeric(df.get('utilization_rate', 0), errors='coerce').fillna(0)
    
    # Add department info
    departments = get_cached_departments()
    dept_map = {d['id']: d['name'] for d in departments}
    df['department_name'] = df['department_id'].map(dept_map).fillna("Unknown")
    
    return df

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
        return True
    except:
        return False

def reset_user_password(username, new_password):
    try:
        supabase.table("users").update({
            "password_hash": new_password
        }).eq("username", username).execute()
        st.cache_data.clear()
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
# CUSTOM CSS
# ============================================
if st.session_state.theme == "light":
    THEME_CSS = f"""
    <style>
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        .stAppDeployButton {{display: none;}}
        
        .main, .stApp {{ background-color: {HELB_WHITE} !important; }}
        
        /* Login page text - BLACK for visibility */
        .stTextInput label {{
            color: {HELB_BLACK} !important;
        }}
        
        [data-testid="stSidebar"] {{ background-color: {HELB_GREEN} !important; padding-top: 1rem; }}
        [data-testid="stSidebar"] * {{ color: white !important; }}
        
        .sidebar-user-info {{
            background: rgba(255,255,255,0.15);
            padding: 0.8rem;
            border-radius: 10px;
            margin: 0.5rem 0;
            text-align: center;
        }}
        .sidebar-user-info strong {{ font-size: 0.85rem; display: block; margin-bottom: 5px; }}
        .sidebar-user-info .dept {{ font-size: 0.7rem; display: block; margin-bottom: 3px; }}
        .sidebar-user-info .role {{ font-size: 0.65rem; display: block; }}
        
        [data-testid="stSidebar"] div[role="radiogroup"] label {{
            background-color: {HELB_GOLD} !important;
            color: {HELB_DARK} !important;
            border-radius: 8px !important;
            padding: 8px 12px !important;
            margin: 4px 0 !important;
            font-weight: 600 !important;
            font-size: 0.8rem !important;
            transition: all 0.3s ease !important;
        }}
        
        [data-testid="stSidebar"] div[role="radiogroup"] label[data-baseweb="radio"]:has(input:checked) {{
            background-color: {HELB_BLUE} !important;
            color: white !important;
        }}
        
        [data-testid="stSidebar"] .stButton > button {{
            background-color: rgba(255,255,255,0.2) !important;
            color: white !important;
            font-size: 0.75rem !important;
        }}
        
        h1, h2, h3, h4 {{ color: {HELB_GREEN} !important; font-weight: 600 !important; }}
        h1 {{ border-bottom: 3px solid {HELB_GOLD}; padding-bottom: 15px; margin-bottom: 25px; }}
        
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
        
        .login-container {{
            background: linear-gradient(135deg, {HELB_GREEN} 0%, {HELB_BLUE} 100%);
            border-radius: 20px;
            padding: 2.5rem;
            text-align: center;
        }}
        .login-title {{ color: white; font-size: 1.5rem; font-weight: 700; }}
        .login-subtitle {{ color: rgba(255,255,255,0.85); font-size: 0.85rem; }}
        
        .kpi-card {{
            background: linear-gradient(135deg, {HELB_GREEN} 0%, {HELB_BLUE} 100%);
            border-radius: 12px;
            padding: 1rem;
            text-align: center;
        }}
        .kpi-label {{ font-size: 0.7rem; text-transform: uppercase; color: {HELB_GOLD} !important; font-weight: 600; }}
        .kpi-value {{ font-size: 1.5rem; font-weight: 700; margin: 0.2rem 0; color: white !important; }}
        .kpi-sub {{ font-size: 0.55rem; color: white !important; margin-top: 0.2rem; opacity: 0.9; }}
        .progress-bar {{ height: 4px; background: rgba(255,255,255,0.3); border-radius: 2px; margin-top: 0.5rem; }}
        .progress-fill {{ height: 100%; background: {HELB_GOLD}; border-radius: 2px; }}
        
        .metric-card {{
            background: {HELB_WHITE};
            border-radius: 12px;
            padding: 1rem;
            border-left: 4px solid {HELB_GOLD};
        }}
        .metric-card * {{ color: {HELB_BLACK} !important; }}
        
        .badge-active {{ background-color: {HELB_GREEN}; color: white; padding: 3px 10px; border-radius: 20px; font-size: 11px; }}
        .badge-pending {{ background-color: #dc2626; color: white; padding: 3px 10px; border-radius: 20px; font-size: 11px; }}
        .badge-inprogress {{ background-color: #FFB81C; color: #1F2937; padding: 3px 10px; border-radius: 20px; font-size: 11px; }}
        .badge-exceeded {{ background-color: #8B5CF6; color: white; padding: 3px 10px; border-radius: 20px; font-size: 11px; }}
        .badge-expired {{ background-color: #dc2626; color: white; padding: 3px 10px; border-radius: 20px; font-size: 11px; }}
        
        .stButton > button {{
            background: linear-gradient(135deg, {HELB_GREEN} 0%, {HELB_BLUE} 100%) !important;
            color: white !important;
            border-radius: 8px !important;
            padding: 8px 16px !important;
            font-weight: 600 !important;
        }}
        .stButton > button[key*="delete"] {{ background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%) !important; }}
        
        .streamlit-expanderHeader {{ background-color: {HELB_WHITE} !important; border: 1px solid #D1D5DB !important; }}
        .streamlit-expanderHeader p {{ color: {HELB_BLACK} !important; font-size: 0.85rem !important; font-weight: 600 !important; }}
        .streamlit-expanderContent {{ background-color: {HELB_WHITE} !important; border: 1px solid #D1D5DB !important; border-top: none !important; padding: 1rem !important; }}
        .streamlit-expanderContent * {{ color: {HELB_BLACK} !important; }}
        
        .stTextInput input, .stSelectbox div, .stDateInput input, .stNumberInput input, .stTextArea textarea {{
            background-color: white !important;
            color: {HELB_BLACK} !important;
            border: 1px solid #D1D5DB !important;
            font-size: 0.75rem !important;
        }}
        
        .stTabs [data-baseweb="tab-list"] {{ background: {HELB_GRAY}; padding: 0.3rem; border-radius: 10px; gap: 0.3rem; }}
        .stTabs [data-baseweb="tab"] {{ font-size: 0.75rem; padding: 0.3rem 1rem; color: {HELB_BLACK}; }}
        .stTabs [aria-selected="true"] {{ background-color: {HELB_GOLD} !important; color: {HELB_BLACK} !important; font-weight: 600; }}
        
        .footer {{ text-align: center; padding: 1rem; color: #6B7280; font-size: 0.6rem; border-top: 1px solid #E5E7EB; margin-top: 1.5rem; }}
        
        .dataframe th {{ background-color: {HELB_GREEN} !important; color: white !important; font-size: 0.7rem; }}
        .dataframe td {{ color: {HELB_BLACK} !important; font-size: 0.7rem; }}
        .stMarkdown, .stMarkdown p, .stMarkdown div {{ color: {HELB_BLACK} !important; }}
        hr {{ margin: 0.5rem 0; }}
    </style>
    """
else:
    THEME_CSS = f"""
    <style>
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        .stAppDeployButton {{display: none;}}
        
        .main, .stApp {{ background-color: #1a1a2e !important; }}
        
        /* Login page text - WHITE for visibility in dark mode */
        .stTextInput label {{
            color: white !important;
        }}
        
        [data-testid="stSidebar"] {{ background-color: #0f3460 !important; padding-top: 1rem; }}
        [data-testid="stSidebar"] * {{ color: white !important; }}
        
        .sidebar-user-info {{
            background: rgba(255,255,255,0.15);
            padding: 0.8rem;
            border-radius: 10px;
            margin: 0.5rem 0;
            text-align: center;
        }}
        .sidebar-user-info strong {{ font-size: 0.85rem; display: block; margin-bottom: 5px; }}
        .sidebar-user-info .dept {{ font-size: 0.7rem; display: block; margin-bottom: 3px; }}
        .sidebar-user-info .role {{ font-size: 0.65rem; display: block; }}
        
        [data-testid="stSidebar"] div[role="radiogroup"] label {{
            background-color: {HELB_GOLD} !important;
            color: {HELB_DARK} !important;
            border-radius: 8px !important;
            padding: 8px 12px !important;
            margin: 4px 0 !important;
            font-weight: 600 !important;
            font-size: 0.8rem !important;
        }}
        
        [data-testid="stSidebar"] div[role="radiogroup"] label[data-baseweb="radio"]:has(input:checked) {{
            background-color: {HELB_GREEN} !important;
            color: white !important;
        }}
        
        h1, h2, h3, h4 {{ color: {HELB_GOLD} !important; font-weight: 600 !important; }}
        
        .dashboard-header {{
            background: linear-gradient(135deg, #0f3460 0%, #16213e 100%);
            padding: 0.8rem 1.5rem;
            border-radius: 12px;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .dashboard-header h1 {{ color: white !important; font-size: 1.2rem; }}
        .dashboard-header p {{ color: {HELB_GOLD} !important; }}
        
        .login-container {{ background: linear-gradient(135deg, #0f3460 0%, #16213e 100%); border-radius: 20px; padding: 2.5rem; text-align: center; }}
        
        .kpi-card {{ background: linear-gradient(135deg, #0f3460 0%, #16213e 100%); border-radius: 10px; padding: 0.8rem; text-align: center; }}
        .kpi-label {{ color: {HELB_GOLD}; font-size: 0.65rem; }}
        .kpi-value {{ color: white; font-size: 1.3rem; font-weight: 700; }}
        .kpi-sub {{ color: rgba(255,255,255,0.7); font-size: 0.55rem; }}
        
        .metric-card {{ background: #16213e; border-radius: 10px; padding: 0.8rem; border-left: 4px solid {HELB_GOLD}; }}
        
        .stButton > button {{ background: linear-gradient(135deg, #0f3460 0%, #16213e 100%) !important; color: white !important; }}
        
        .stTextInput input, .stSelectbox div, .stDateInput input, .stNumberInput input, .stTextArea textarea {{
            background-color: #2d2d44 !important;
            color: white !important;
            border: 1px solid #4a4a6a !important;
        }}
        
        .streamlit-expanderHeader {{ background-color: #2d2d44 !important; }}
        .streamlit-expanderHeader p {{ color: {HELB_GOLD} !important; }}
        
        .stTabs [data-baseweb="tab-list"] {{ background: #2d2d44; }}
        .stTabs [aria-selected="true"] {{ background-color: {HELB_GOLD} !important; color: {HELB_DARK} !important; }}
        
        .footer {{ text-align: center; padding: 1rem; color: #6B7280; border-top: 1px solid #2d2d44; margin-top: 1.5rem; }}
    </style>
    """

st.markdown(THEME_CSS, unsafe_allow_html=True)

# ============================================
# LOGIN PAGE
# ============================================
if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if LOGO_BASE64:
            logo_html = f'<img src="data:image/png;base64,{LOGO_BASE64}" style="width: 200px; height: auto; margin-bottom: 1rem; background: transparent;">'
        else:
            logo_html = '<div style="font-size: 3rem;">🏦</div>'
        
        st.markdown(f"""
        <div class='login-container'>
            <div class='login-logo'>{logo_html}</div>
            <h1 class='login-title'>HIGHER EDUCATION LOANS BOARD</h1>
            <p class='login-subtitle'>Strategy Performance Management System</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submitted = st.form_submit_button("Login", use_container_width=True)
            
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
                            st.rerun()
                        else:
                            st.error("❌ Invalid password")
                    else:
                        st.error("❌ User not found")
                else:
                    st.warning("Please enter both username and password")
    st.stop()

# ============================================
# MAIN APPLICATION
# ============================================

# Header with theme toggle
col_header, col_theme, col_refresh = st.columns([5, 1, 1])
with col_header:
    if LOGO_BASE64:
        logo_html = f'<img src="data:image/png;base64,{LOGO_BASE64}" style="width: 40px; height: auto; background: transparent;">'
    else:
        logo_html = '<div style="font-size: 1.5rem;">🏦</div>'
    
    st.markdown(f"""
    <div class='dashboard-header'>
        <div class='header-left'>
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

# Sidebar
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
        <span class='dept'>{dept_display}</span>
        <span class='role'>{role_display}</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    menu_options = ["📊 Dashboard", "📋 Work Plans", "📄 Contracts", "📋 Policies"]
    if st.session_state.user_role == "admin":
        menu_options.append("👥 User Management")
    if st.session_state.user_role in ["admin", "management"]:
        menu_options.append("🏢 Enterprise View")
    
    choice = st.radio("📋 Navigation", menu_options, label_visibility="collapsed")
    
    st.markdown("---")
    
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.clear()
        st.cache_data.clear()
        st.rerun()

# ============================================
# WORK PLANS MODULE
# ============================================
if choice == "📋 Work Plans":
    if st.session_state.user_role in ["admin", "management"]:
        st.markdown("<h2>📋 Institution-Wide Work Plan</h2>", unsafe_allow_html=True)
    else:
        st.markdown(f"<h2>📋 {st.session_state.user_dept_name} Department Work Plan</h2>", unsafe_allow_html=True)
    
    # Filter Bar
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
    
    # TAB 1: ADD NEW WORK PLAN ACTIVITY
    with tab_add:
        st.markdown("### Add New Work Plan Activity")
        
        # Get directorate for the user's department (auto-populate)
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
                # Auto-populate Directorate field
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
    
    # TAB 2: VIEW ALL ACTIVITIES
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
    
    # TAB 3: WORK PLAN DASHBOARD
    with tab_dashboard:
        if filtered_plans:
            df = pd.DataFrame(filtered_plans)
            df['calculated_progress'] = df.apply(lambda x: calculate_progress_from_actual(x.get('annual_target', '0'), x.get('actual_achievement', 0)), axis=1)
            df['exceeded'] = df.apply(lambda x: is_target_exceeded(x.get('actual_achievement', 0), x.get('annual_target', '0')), axis=1)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"<div class='kpi-card'><div class='kpi-label'>📋 TOTAL ACTIVITIES</div><div class='kpi-value'>{len(df)}</div></div>", unsafe_allow_html=True)
            with col2:
                completed = len(df[df['calculated_progress'] >= 100])
                rate = (completed/len(df)*100) if len(df)>0 else 0
                st.markdown(f"<div class='kpi-card'><div class='kpi-label'>✅ COMPLETION RATE</div><div class='kpi-value'>{rate:.0f}%</div><div class='progress-bar'><div class='progress-fill' style='width:{rate}%;'></div></div></div>", unsafe_allow_html=True)
            with col3:
                total_budget = df['budget_allocation'].fillna(0).sum()
                st.markdown(f"<div class='kpi-card'><div class='kpi-label'>💰 TOTAL BUDGET</div><div class='kpi-value'>KES {total_budget/1e6:.1f}M</div></div>", unsafe_allow_html=True)
            with col4:
                exceeded_count = len(df[df['exceeded'] == True])
                st.markdown(f"<div class='kpi-card'><div class='kpi-label'>🏆 TARGETS EXCEEDED</div><div class='kpi-value'>{exceeded_count}</div></div>", unsafe_allow_html=True)
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
        st.session_state.filter_financial_year = st.selectbox("Financial Year", financial_years, 
                                                               index=financial_years.index(st.session_state.filter_financial_year) if st.session_state.filter_financial_year in financial_years else 0,
                                                               key="fy_filter_dash")
    with col_q_dash:
        quarters = ["All", "Q1 (Jul-Sep)", "Q2 (Oct-Dec)", "Q3 (Jan-Mar)", "Q4 (Apr-Jun)"]
        st.session_state.filter_quarter = st.selectbox("Quarter", quarters,
                                                        index=quarters.index(st.session_state.filter_quarter) if st.session_state.filter_quarter in quarters else 0,
                                                        key="q_filter_dash")
    with col_m_dash:
        available_months = get_months_for_quarter(st.session_state.filter_quarter)
        st.session_state.filter_month = st.selectbox("Month", ["All"] + available_months,
                                                      index=0 if st.session_state.filter_month == "All" or st.session_state.filter_month not in available_months else available_months.index(st.session_state.filter_month) + 1,
                                                      key="m_filter_dash")
    
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
        
        filtered_df = filter_work_plans_by_date(df_plans, st.session_state.filter_financial_year, 
                                                 st.session_state.filter_quarter, st.session_state.filter_month)
        
        if st.session_state.user_role in ["admin", "management"]:
            departments_list = filtered_df['department_name'].unique().tolist() if not filtered_df.empty else []
            if departments_list:
                selected_dept_filter = st.multiselect("Filter by Department", departments_list, default=[])
                if selected_dept_filter:
                    filtered_df = filtered_df[filtered_df['department_name'].isin(selected_dept_filter)]
    else:
        filtered_df = pd.DataFrame()
    
    tab_work, tab_contracts, tab_policies = st.tabs(["📋 Work Plans Analytics", "📄 Contracts Analytics", "📜 Policies Analytics"])
    
    with tab_work:
        if not filtered_df.empty:
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.markdown(f"<div class='kpi-card'><div class='kpi-label'>📋 TOTAL</div><div class='kpi-value'>{len(filtered_df)}</div><div class='kpi-sub'>Activities</div></div>", unsafe_allow_html=True)
            with col2:
                completed = len(filtered_df[filtered_df['calculated_progress'] >= 100])
                rate = (completed/len(filtered_df)*100) if len(filtered_df)>0 else 0
                st.markdown(f"<div class='kpi-card'><div class='kpi-label'>✅ COMPLETED</div><div class='kpi-value'>{rate:.0f}%</div><div class='progress-bar'><div class='progress-fill' style='width:{rate}%;'></div></div></div>", unsafe_allow_html=True)
            with col3:
                avg_progress = filtered_df['calculated_progress'].mean()
                st.markdown(f"<div class='kpi-card'><div class='kpi-label'>📈 AVG PROGRESS</div><div class='kpi-value'>{avg_progress:.0f}%</div></div>", unsafe_allow_html=True)
            with col4:
                total_budget = filtered_df['budget_allocation'].fillna(0).sum()
                st.markdown(f"<div class='kpi-card'><div class='kpi-label'>💰 BUDGET</div><div class='kpi-value'>KES {total_budget/1e6:.1f}M</div></div>", unsafe_allow_html=True)
            with col5:
                exceeded = len(filtered_df[filtered_df['exceeded'] == True])
                st.markdown(f"<div class='kpi-card'><div class='kpi-label'>🏆 EXCEEDED</div><div class='kpi-value'>{exceeded}</div></div>", unsafe_allow_html=True)
            
            st.markdown("---")
            
            col_chart1, col_chart2 = st.columns(2)
            with col_chart1:
                st.markdown("#### Status Distribution")
                status_counts = filtered_df['status_group'].value_counts().reset_index()
                status_counts.columns = ['Status', 'Count']
                # FIXED COLORS: Done = Green, In Progress = Amber/Gold, Not Started = Red
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
                pillar_progress = filtered_df.groupby('strategic_pillar')['calculated_progress'].mean().reset_index()
                pillar_progress.columns = ['Pillar', 'Progress %']
                pillar_progress = pillar_progress.sort_values('Progress %', ascending=True)
                fig = px.bar(pillar_progress, y='Pillar', x='Progress %', orientation='h',
                            color='Progress %', color_continuous_scale='Greens',
                            text='Progress %')
                fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                fig.update_layout(height=350, xaxis_title="Progress %", yaxis_title="", margin=dict(l=20, r=20, t=30, b=20))
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("#### Department Performance")
            dept_progress = filtered_df.groupby('department_name')['calculated_progress'].mean().reset_index()
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
                category_stats = filtered_df['activity_category'].value_counts().reset_index()
                category_stats.columns = ['Category', 'Count']
                fig = px.bar(category_stats, x='Category', y='Count',
                            color='Count', color_discrete_sequence=[HELB_GREEN],
                            text='Count')
                fig.update_traces(textposition='outside')
                fig.update_layout(height=350, margin=dict(l=20, r=20, t=30, b=20))
                st.plotly_chart(fig, use_container_width=True)
            
            with col_chart4:
                st.markdown("#### Quarterly Performance Trend")
                quarterly_data = filtered_df.groupby('quarter').agg({
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
            
            overdue_df = filtered_df[(filtered_df['days_left'] < 0) & (filtered_df['calculated_progress'] < 100)]
            urgent_df = filtered_df[(filtered_df['days_left'] >= 0) & (filtered_df['days_left'] <= 14) & (filtered_df['calculated_progress'] < 80)]
            
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
                csv = filtered_df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download Work Plan Data", csv, f"work_plan_data_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")
        else:
            st.info("No work plan data available for the selected filters.")
    
    with tab_contracts:
        if contracts:
            # Enhanced Contracts Analytics Dashboard with professional KPI cards
            df_contracts = pd.DataFrame(contracts)
            
            # Calculate enhanced metrics
            df_contracts['contract_value'] = pd.to_numeric(df_contracts.get('contract_value', 0), errors='coerce').fillna(0)
            df_contracts['amount_spent_to_date'] = pd.to_numeric(df_contracts.get('amount_spent_to_date', 0), errors='coerce').fillna(0)
            df_contracts['vendor_performance'] = pd.to_numeric(df_contracts.get('vendor_performance', 0), errors='coerce').fillna(0)
            df_contracts['utilization_rate'] = pd.to_numeric(df_contracts.get('utilization_rate', 0), errors='coerce').fillna(0)
            
            # Add department names
            departments = get_cached_departments()
            dept_map = {d['id']: d['name'] for d in departments}
            df_contracts['department_name'] = df_contracts['department_id'].map(dept_map).fillna("Unknown")
            
            # Professional KPI Row with consistent styling
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                total_value = df_contracts['contract_value'].sum()
                st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-label'>💰 TOTAL CONTRACT VALUE</div>
                    <div class='kpi-value'>KES {total_value/1e6:.1f}M</div>
                    <div class='kpi-sub'>Total Value</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                total_spent = df_contracts['amount_spent_to_date'].sum()
                utilization = (total_spent/total_value*100) if total_value > 0 else 0
                st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-label'>💸 TOTAL SPENT</div>
                    <div class='kpi-value'>KES {total_spent/1e6:.1f}M</div>
                    <div class='progress-bar'><div class='progress-fill' style='width:{utilization}%;'></div></div>
                    <div class='kpi-sub'>{utilization:.0f}% utilized</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                active = len(df_contracts[df_contracts['status'] == 'active'])
                st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-label'>✅ ACTIVE CONTRACTS</div>
                    <div class='kpi-value'>{active}</div>
                    <div class='kpi-sub'>Active Contracts</div>
                </div>
                """, unsafe_allow_html=True)
            with col4:
                expiring = len(df_contracts[df_contracts['status'] == 'expiring_soon'])
                st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-label'>⚠️ EXPIRING SOON</div>
                    <div class='kpi-value'>{expiring}</div>
                    <div class='kpi-sub'>Within 30 days</div>
                </div>
                """, unsafe_allow_html=True)
            with col5:
                avg_performance = df_contracts[df_contracts['vendor_performance'] > 0]['vendor_performance'].mean()
                st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-label'>⭐ AVG VENDOR RATING</div>
                    <div class='kpi-value'>{avg_performance:.1f}/5</div>
                    <div class='kpi-sub'>Vendor Rating</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Analytics Charts
            col_chart1, col_chart2 = st.columns(2)
            with col_chart1:
                st.markdown("#### Contract Value by Department")
                dept_value = df_contracts.groupby('department_name')['contract_value'].sum().reset_index()
                dept_value = dept_value.sort_values('contract_value', ascending=True)
                fig = px.bar(dept_value, y='department_name', x='contract_value', orientation='h',
                            color='contract_value', color_continuous_scale='Greens',
                            text=dept_value['contract_value'].apply(lambda x: f'KES {x/1e6:.1f}M'))
                fig.update_traces(textposition='outside')
                fig.update_layout(height=400, xaxis_title="Contract Value (KES)", yaxis_title="", margin=dict(l=20, r=20, t=30, b=20))
                st.plotly_chart(fig, use_container_width=True)
            
            with col_chart2:
                st.markdown("#### Spend Utilization Status")
                high_util = len(df_contracts[df_contracts['utilization_rate'] >= 80])
                medium_util = len(df_contracts[(df_contracts['utilization_rate'] >= 50) & (df_contracts['utilization_rate'] < 80)])
                low_util = len(df_contracts[df_contracts['utilization_rate'] < 50])
                
                util_data = pd.DataFrame({
                    'Utilization': ['High (80%+)', 'Medium (50-80%)', 'Low (<50%)'],
                    'Count': [high_util, medium_util, low_util]
                })
                fig = px.pie(util_data, values='Count', names='Utilization', hole=0.4,
                            color_discrete_sequence=[HELB_GREEN, HELB_GOLD, HELB_BLUE])
                fig.update_layout(height=350, margin=dict(l=20, r=20, t=30, b=20))
                st.plotly_chart(fig, use_container_width=True)
            
            col_chart3, col_chart4 = st.columns(2)
            with col_chart3:
                st.markdown("#### Vendor Performance Distribution")
                perf_bins = pd.cut(df_contracts[df_contracts['vendor_performance'] > 0]['vendor_performance'], 
                                  bins=[0, 2, 3, 4, 5], labels=['Poor (0-2)', 'Fair (2-3)', 'Good (3-4)', 'Excellent (4-5)'])
                perf_counts = perf_bins.value_counts()
                fig = px.bar(x=perf_counts.values, y=perf_counts.index, orientation='h',
                            color=perf_counts.values, color_continuous_scale='Greens',
                            text=perf_counts.values)
                fig.update_traces(textposition='outside')
                fig.update_layout(height=300, xaxis_title="Number of Contracts", yaxis_title="", margin=dict(l=20, r=20, t=30, b=20))
                st.plotly_chart(fig, use_container_width=True)
            
            with col_chart4:
                st.markdown("#### Budget Alert Summary")
                alert_count = len(df_contracts[df_contracts.get('budget_alert', False) == True])
                no_alert = len(df_contracts) - alert_count
                alert_data = pd.DataFrame({
                    'Status': ['⚠️ Budget Alert', '✅ Healthy'],
                    'Count': [alert_count, no_alert]
                })
                fig = px.pie(alert_data, values='Count', names='Status', hole=0.4,
                            color_discrete_sequence=['#dc2626', HELB_GREEN])
                fig.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20))
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            st.markdown("### 📋 Contract List")
            
            for _, contract in df_contracts.iterrows():
                end_date = datetime.strptime(contract["end_date"], "%Y-%m-%d").date()
                days_left = (end_date - datetime.now().date()).days
                
                if days_left > 30:
                    badge = '<span class="badge-active">🟢 Active</span>'
                elif days_left > 0:
                    badge = '<span class="badge-inprogress">🟡 Expiring Soon</span>'
                else:
                    badge = '<span class="badge-expired">🔴 Expired</span>'
                
                # Show budget alert if applicable
                budget_alert_badge = ''
                if contract.get('budget_alert', False):
                    budget_alert_badge = '<span style="background-color: #dc2626; color: white; padding: 2px 8px; border-radius: 12px; font-size: 10px; margin-left: 10px;">⚠️ Budget Alert</span>'
                
                utilization = contract.get('utilization_rate', 0)
                performance = contract.get('vendor_performance', 0)
                
                st.markdown(f"""
                <div class='metric-card'>
                    <div style='display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;'>
                        <div style='flex:1;'>
                            <b>📄 {contract['contract_title']}</b>{budget_alert_badge}<br>
                            <span style='font-size:0.85rem;'>Vendor: {contract['vendor_name']}</span><br>
                            <span style='font-size:0.8rem; color:#6B7280;'>End Date: {contract['end_date']} | {days_left} days remaining</span><br>
                            <span style='font-size:0.8rem;'>💰 Value: KES {contract.get('contract_value', 0):,.0f} | Spent: KES {contract.get('amount_spent_to_date', 0):,.0f} ({utilization:.0f}% used)</span><br>
                            <span style='font-size:0.8rem;'>⭐ Performance: {performance}/5 | Payment: {contract.get('payment_terms', 'Not specified')}</span>
                        </div>
                        <div style='text-align:right;'>
                            {badge}<br>
                            <span style='font-size:0.7rem;'>Auto-renewal: {'Yes' if contract.get('auto_renewal', False) else 'No'}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No contracts found. Click 'Add New Contract' in the Contracts section to get started.")
    
    with tab_policies:
        if policies:
            df_policies = pd.DataFrame(policies)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"<div class='kpi-card'><div class='kpi-label'>📜 TOTAL POLICIES</div><div class='kpi-value'>{len(df_policies)}</div></div>", unsafe_allow_html=True)
            with col2:
                expiring_soon = 0
                for p in policies:
                    try:
                        expiry = datetime.strptime(p["expiry_date"], "%Y-%m-%d").date()
                        if 0 < (expiry - datetime.now().date()).days <= 90:
                            expiring_soon += 1
                    except:
                        pass
                st.markdown(f"<div class='kpi-card'><div class='kpi-label'>⚠️ EXPIRING SOON</div><div class='kpi-value'>{expiring_soon}</div></div>", unsafe_allow_html=True)
            with col3:
                expired = 0
                for p in policies:
                    try:
                        expiry = datetime.strptime(p["expiry_date"], "%Y-%m-%d").date()
                        if (expiry - datetime.now().date()).days < 0:
                            expired += 1
                    except:
                        pass
                st.markdown(f"<div class='kpi-card'><div class='kpi-label'>🔴 EXPIRED</div><div class='kpi-value'>{expired}</div></div>", unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("#### Policy Status Overview")
            for policy in policies:
                expiry = datetime.strptime(policy["expiry_date"], "%Y-%m-%d").date()
                days_left = (expiry - datetime.now().date()).days
                
                if days_left > 90:
                    badge = '<span class="badge-active">🟢 Active</span>'
                elif days_left > 0:
                    badge = '<span class="badge-inprogress">🟡 Expiring Soon</span>'
                else:
                    badge = '<span class="badge-expired">🔴 Expired</span>'
                
                st.markdown(f"""
                <div class='metric-card'>
                    <div style='display:flex; justify-content:space-between; align-items:center;'>
                        <div>
                            <b>📜 {policy['policy_name']}</b><br>
                            Expires: {policy['expiry_date']} ({days_left} days left)
                        </div>
                        <div>{badge}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No policies found. Click 'Add New Policy' in the Policies section to get started.")
    
    st.success(f"👋 Welcome, {st.session_state.user_fullname}!")

# ============================================
# ENHANCED CONTRACTS SECTION
# ============================================
elif choice == "📄 Contracts":
    st.subheader("Contract Management")
    
    # Create tabs for better organization
    tab_overview, tab_active, tab_expiring, tab_add = st.tabs(["📊 Overview & Analytics", "✅ Active Contracts", "⚠️ Expiring & Expired", "➕ New Contract"])
    
    with tab_overview:
        contracts = get_cached_contracts(st.session_state.user_role, st.session_state.user_dept)
        if contracts:
            df_contracts = pd.DataFrame(contracts)
            
            # Enhanced metrics
            df_contracts['contract_value'] = pd.to_numeric(df_contracts.get('contract_value', 0), errors='coerce').fillna(0)
            df_contracts['amount_spent_to_date'] = pd.to_numeric(df_contracts.get('amount_spent_to_date', 0), errors='coerce').fillna(0)
            df_contracts['vendor_performance'] = pd.to_numeric(df_contracts.get('vendor_performance', 0), errors='coerce').fillna(0)
            
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
                avg_performance = df_contracts[df_contracts['vendor_performance'] > 0]['vendor_performance'].mean()
                st.metric("⭐ Avg Vendor Rating", f"{avg_performance:.1f}/5" if avg_performance > 0 else "N/A")
            
            st.markdown("---")
            
            # Show budget alerts
            budget_alerts = df_contracts[df_contracts.get('budget_alert', False) == True]
            if not budget_alerts.empty:
                st.warning(f"⚠️ **Budget Alerts:** {len(budget_alerts)} contract(s) have exceeded 80% utilization")
                for _, contract in budget_alerts.iterrows():
                    st.caption(f"• {contract['contract_title']}: {contract.get('utilization_rate', 0):.0f}% utilized")
        else:
            st.info("No contracts found. Add your first contract in the 'New Contract' tab.")
    
    with tab_active:
        contracts = get_cached_contracts(st.session_state.user_role, st.session_state.user_dept)
        if contracts:
            active_contracts = [c for c in contracts if c.get('status') == 'active']
            if active_contracts:
                for contract in active_contracts:
                    end_date = datetime.strptime(contract["end_date"], "%Y-%m-%d").date()
                    days_left = (end_date - datetime.now().date()).days
                    
                    utilization = contract.get('utilization_rate', 0)
                    performance = contract.get('vendor_performance', 0)
                    compliance = contract.get('compliance_status', 'Not assessed')
                    
                    st.markdown(f"""
                    <div class='metric-card'>
                        <div style='display:flex; justify-content:space-between; align-items:start;'>
                            <div style='flex:2;'>
                                <b>📄 {contract['contract_title']}</b><br>
                                <span style='font-size:0.85rem;'>Vendor: {contract['vendor_name']}</span><br>
                                <span style='font-size:0.8rem; color:#6B7280;'>End Date: {contract['end_date']} | {days_left} days remaining</span><br>
                                <span style='font-size:0.8rem;'>💰 Value: KES {contract.get('contract_value', 0):,.0f} | Spent: KES {contract.get('amount_spent_to_date', 0):,.0f} ({utilization:.0f}% used)</span><br>
                                <span style='font-size:0.8rem;'>⭐ Performance: {performance}/5 | Compliance: {compliance}</span><br>
                                <span style='font-size:0.8rem;'>💳 Payment Terms: {contract.get('payment_terms', 'Not specified')}</span>
                            </div>
                            <div style='text-align:right;'>
                                <span class='badge-active'>🟢 Active</span><br>
                                <span style='font-size:0.7rem;'>Auto-renewal: {'Yes' if contract.get('auto_renewal', False) else 'No'}</span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Add update controls in expander
                    with st.expander("✏️ Update Contract Performance", expanded=False):
                        col1, col2 = st.columns(2)
                        with col1:
                            new_spent = st.number_input("Update Amount Spent", 
                                                       min_value=0.0, 
                                                       value=float(contract.get('amount_spent_to_date', 0)),
                                                       step=10000.0,
                                                       key=f"spent_{contract['id']}")
                            if st.button(f"Update Spending", key=f"update_spent_{contract['id']}"):
                                if update_contract_spending(contract['id'], new_spent):
                                    st.success("✅ Spending updated!")
                                    st.rerun()
                        with col2:
                            new_performance = st.slider("Vendor Performance Rating", 0.0, 5.0, 
                                                       value=float(performance), step=0.5,
                                                       key=f"perf_{contract['id']}")
                            new_compliance = st.selectbox("Compliance Status", 
                                                         ["Fully Compliant", "Partially Compliant", "Non-Compliant"],
                                                         index=["Fully Compliant", "Partially Compliant", "Non-Compliant"].index(compliance) if compliance in ["Fully Compliant", "Partially Compliant", "Non-Compliant"] else 0,
                                                         key=f"comp_{contract['id']}")
                            if st.button(f"Update Performance", key=f"update_perf_{contract['id']}"):
                                if update_vendor_performance(contract['id'], new_performance, new_compliance):
                                    st.success("✅ Performance updated!")
                                    st.rerun()
            else:
                st.info("No active contracts found.")
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
                    
                    status_badge = '<span class="badge-inprogress">🟡 Expiring Soon</span>' if days_left > 0 else '<span class="badge-expired">🔴 Expired</span>'
                    
                    st.markdown(f"""
                    <div class='metric-card'>
                        <div style='display:flex; justify-content:space-between; align-items:center;'>
                            <div>
                                <b>📄 {contract['contract_title']}</b><br>
                                Vendor: {contract['vendor_name']}<br>
                                End Date: {contract['end_date']} | {abs(days_left)} days {'overdue' if days_left < 0 else 'left'}<br>
                                Auto-renewal: {'Yes' if contract.get('auto_renewal', False) else 'No'}
                            </div>
                            <div>{status_badge}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("✅ No expiring or expired contracts!")
        else:
            st.info("No contracts found.")
    
    with tab_add:
        st.markdown("### Add New Contract with Enhanced Tracking")
        
        with st.form("new_contract_enhanced"):
            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input("Contract Title*")
                vendor = st.text_input("Vendor Name*")
                contract_value = st.number_input("Contract Value (KES)*", min_value=0.0, step=10000.0, format="%.2f")
                amount_spent = st.number_input("Initial Amount Spent (KES)", min_value=0.0, step=10000.0, format="%.2f", value=0.0)
                payment_terms = st.selectbox("Payment Terms", ["Monthly", "Quarterly", "Bi-annually", "Annually", "Milestone-based", "One-time"])
            with col2:
                end_date = st.date_input("Contract End Date*")
                signed_date = st.date_input("Signed Date", value=datetime.now().date())
                auto_renew = st.checkbox("Auto-renewal")
                contract_url = st.text_input("Contract Document URL", placeholder="https://...")
                compliance_status = st.selectbox("Initial Compliance Status", ["Fully Compliant", "Partially Compliant", "Non-Compliant"])
            
            if st.form_submit_button("Save Contract", use_container_width=True):
                if title and vendor and contract_value > 0 and end_date:
                    contract_data = {
                        "contract_title": title,
                        "vendor_name": vendor,
                        "contract_value": contract_value,
                        "amount_spent_to_date": amount_spent,
                        "payment_terms": payment_terms,
                        "start_date": datetime.now().date().isoformat(),
                        "end_date": end_date.isoformat(),
                        "signed_date": signed_date.isoformat(),
                        "auto_renewal": auto_renew,
                        "contract_url": contract_url if contract_url else None,
                        "compliance_status": compliance_status,
                        "vendor_performance": 0,  # Initial rating
                        "department_id": st.session_state.user_dept
                    }
                    
                    success, message = add_enhanced_contract(contract_data)
                    if success:
                        st.success(f"✅ {message}")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to add contract: {message}")
                else:
                    st.error("Please fill all required fields (*)")

# ============================================
# POLICIES SECTION
# ============================================
elif choice == "📋 Policies":
    st.subheader("Policy Monitor")
    
    with st.expander("➕ Add New Policy", expanded=False):
        with st.form("new_policy"):
            policy_name = st.text_input("Policy Name*")
            expiry_date = st.date_input("Expiry Date*")
            is_global = st.checkbox("Global Policy (applies to all departments)")
            
            if st.form_submit_button("Save Policy", use_container_width=True):
                if policy_name:
                    supabase.table("policies").insert({
                        "policy_name": policy_name,
                        "expiry_date": expiry_date.isoformat(),
                        "department_id": None if is_global else st.session_state.user_dept,
                        "status": "active"
                    }).execute()
                    st.success("Policy added successfully!")
                    st.rerun()
                else:
                    st.error("Please enter a policy name")
    
    policies = get_cached_policies(st.session_state.user_role, st.session_state.user_dept)
    if policies:
        for policy in policies:
            expiry = datetime.strptime(policy["expiry_date"], "%Y-%m-%d").date()
            days_left = (expiry - datetime.now().date()).days
            
            if days_left > 90:
                badge = '<span class="badge-active">Active</span>'
            elif days_left > 0:
                badge = '<span class="badge-inprogress">Expiring Soon</span>'
            else:
                badge = '<span class="badge-expired">Expired</span>'
            
            st.markdown(f"""
            <div class='metric-card'>
                <div style='display:flex; justify-content:space-between; align-items:center;'>
                    <div>
                        <b>📜 {policy['policy_name']}</b><br>
                        Expires: {policy['expiry_date']} ({days_left} days left)
                    </div>
                    <div>{badge}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No policies found. Click 'Add New Policy' to get started.")

# ============================================
# USER MANAGEMENT (ADMIN ONLY)
# ============================================
elif choice == "👥 User Management" and st.session_state.user_role == "admin":
    st.subheader("User Management - Admin Panel")
    
    directorates = get_cached_directorates()
    directorate_options = {d["name"]: d["id"] for d in directorates}
    departments = get_cached_departments()
    dept_options = {d["name"]: d["id"] for d in departments}
    users = get_all_users()
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["➕ Create New User", "✏️ Edit User Role", "🗑️ Delete User", "🏢 Manage Departments", "🏛️ Manage Directorates"])
    
    with tab1:
        with st.form("create_user_form"):
            st.markdown("### Create New User Account")
            col1, col2 = st.columns(2)
            with col1:
                new_username = st.text_input("Username*")
                new_full_name = st.text_input("Full Name*")
            with col2:
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
    
    with tab2:
        st.markdown("### Edit User Role and Department")
        if users:
            user_options = [f"{u['username']} - {u['full_name']}" for u in users if u['username'] != "admin"]
            if user_options:
                selected_user_str = st.selectbox("Select User to Edit", user_options)
                selected_username = selected_user_str.split(" - ")[0]
                
                current_user = next((u for u in users if u['username'] == selected_username), None)
                if current_user:
                    col1, col2 = st.columns(2)
                    with col1:
                        new_role = st.selectbox("New Role", ["department_champion", "management", "admin"], 
                                               index=["department_champion", "management", "admin"].index(current_user['role']))
                    with col2:
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
            else:
                st.info("No other users to edit")
        else:
            st.info("No users found")
    
    with tab3:
        st.markdown("### Delete User")
        st.warning("⚠️ Deleting a user is permanent and cannot be undone!")
        
        if users:
            delete_options = [f"{u['username']} - {u['full_name']}" for u in users if u['username'] != "admin"]
            if delete_options:
                user_to_delete = st.selectbox("Select User to Delete", delete_options)
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
                        st.error("Please confirm deletion by checking the box")
            else:
                st.info("No other users to delete")
        else:
            st.info("No users found")
    
    with tab4:
        st.markdown("### Manage Departments")
        
        with st.expander("➕ Add New Department", expanded=False):
            with st.form("add_department_form"):
                col1, col2 = st.columns(2)
                with col1:
                    new_dept_name = st.text_input("Department Name*")
                    new_dept_directorate = st.selectbox("Directorate*", ["None"] + list(directorate_options.keys()))
                with col2:
                    new_dept_deputy = st.text_input("Deputy Director Name", placeholder="e.g., Deputy Director - Department Name")
                
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
        
        st.markdown("### Edit Existing Departments")
        if departments:
            dept_names = [d["name"] for d in departments]
            selected_dept_name = st.selectbox("Select Department to Edit", dept_names, key="edit_dept_select")
            
            if selected_dept_name:
                selected_dept = next((d for d in departments if d["name"] == selected_dept_name), None)
                if selected_dept:
                    with st.form("edit_department_form"):
                        col1, col2 = st.columns(2)
                        with col1:
                            edit_dept_name = st.text_input("Department Name", value=selected_dept["name"])
                            current_dir_name = ""
                            if selected_dept.get("directorate_id"):
                                dir_info = get_directorate_by_id(selected_dept["directorate_id"])
                                if dir_info:
                                    current_dir_name = dir_info["name"]
                            edit_dept_directorate = st.selectbox("Directorate", ["None"] + list(directorate_options.keys()), 
                                                                 index=0 if not current_dir_name else list(directorate_options.keys()).index(current_dir_name) + 1)
                        with col2:
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
                with col2:
                    pass
                with col3:
                    if dept['name'] not in ["Lending", "Strategy", "Finance", "ICT", "Human Resource"]:
                        if st.button(f"🗑️ Delete", key=f"del_dept_{dept['id']}"):
                            success, message = delete_department(dept['id'])
                            if success:
                                st.success(f"✅ {message}")
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")
        else:
            st.info("No departments found")
    
    with tab5:
        st.markdown("### Manage Directorates")
        
        with st.expander("➕ Add New Directorate", expanded=False):
            with st.form("add_directorate_form"):
                col1, col2 = st.columns(2)
                with col1:
                    new_dir_name = st.text_input("Directorate Name*")
                with col2:
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
        
        st.markdown("### Edit Existing Directorates")
        if directorates:
            dir_names = [d["name"] for d in directorates]
            selected_dir_name = st.selectbox("Select Directorate to Edit", dir_names, key="edit_dir_select")
            
            if selected_dir_name:
                selected_dir = next((d for d in directorates if d["name"] == selected_dir_name), None)
                if selected_dir:
                    with st.form("edit_directorate_form"):
                        col1, col2 = st.columns(2)
                        with col1:
                            edit_dir_name = st.text_input("Directorate Name", value=selected_dir["name"])
                        with col2:
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
            for dir_item in directorates:
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"• **{dir_item['name']}** - Director: {dir_item.get('director_name', 'Not assigned')}")
                with col2:
                    dept_count = len([d for d in departments if d.get('directorate_id') == dir_item['id']])
                    st.caption(f"{dept_count} departments")
                with col3:
                    if dir_item['name'] not in ["Operations", "Human Resource & Administration", "Fund Management", "ICT", "CEO's Office"]:
                        if st.button(f"🗑️ Delete", key=f"del_dir_{dir_item['id']}"):
                            success, message = delete_directorate(dir_item['id'])
                            if success:
                                st.success(f"✅ {message}")
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")
        else:
            st.info("No directorates found")
    
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
            display_cols = ["contract_title", "vendor_name", "contract_value", "amount_spent_to_date", "end_date", "status"]
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
    <p>Powered by Streamlit | Target-Based Progress Tracking | Comprehensive Analytics</p>
</div>
""", unsafe_allow_html=True)
