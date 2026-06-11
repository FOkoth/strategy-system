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

ACTIVITY_CATEGORIES = ["Strategic Plan", "Performance Contracting"]
STATUS_OPTIONS = ["Pending", "In Progress", "Done"]

# ============================================
# CUSTOM CSS - LIGHT THEME FIXES ONLY
# ============================================
if st.session_state.theme == "light":
    THEME_CSS = f"""
    <style>
        /* Hide Streamlit branding */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        .stAppDeployButton {{display: none;}}
        
        /* Main container - White background */
        .main, .stApp {{
            background-color: {HELB_WHITE} !important;
        }}
        
        /* MAKE ALL TEXT BLACK ON WHITE BACKGROUND */
        .stMarkdown, .stMarkdown p, .stMarkdown div, .stMarkdown span {{
            color: {HELB_BLACK} !important;
        }}
        
        /* Sidebar - HELB Green */
        [data-testid="stSidebar"] {{
            background-color: {HELB_GREEN} !important;
            padding-top: 1rem;
        }}
        
        [data-testid="stSidebar"] * {{
            color: white !important;
        }}
        
        /* Sidebar user info */
        .sidebar-user-info {{
            background: rgba(255,255,255,0.15);
            padding: 0.8rem;
            border-radius: 10px;
            margin: 0.5rem 0;
            text-align: center;
        }}
        
        .sidebar-user-info strong {{
            font-size: 0.85rem;
            display: block;
            margin-bottom: 5px;
        }}
        
        .sidebar-user-info .dept {{
            font-size: 0.7rem;
            display: block;
            margin-bottom: 3px;
        }}
        
        .sidebar-user-info .role {{
            font-size: 0.65rem;
            display: block;
        }}
        
        /* Navigation radio buttons */
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
        
        [data-testid="stSidebar"] div[role="radiogroup"] label:hover {{
            transform: translateX(5px);
            filter: brightness(1.05);
        }}
        
        /* Logout button */
        [data-testid="stSidebar"] .stButton > button {{
            background-color: rgba(255,255,255,0.2) !important;
            color: white !important;
            border: 1px solid rgba(255,255,255,0.3) !important;
            font-size: 0.75rem !important;
        }}
        
        /* Headers */
        h1, h2, h3, h4 {{
            color: {HELB_GREEN} !important;
            font-weight: 600 !important;
        }}
        
        h1 {{
            border-bottom: 3px solid {HELB_GOLD};
            padding-bottom: 15px;
            margin-bottom: 25px;
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
        
        .header-left {{
            display: flex;
            align-items: center;
            gap: 1rem;
        }}
        
        .dashboard-header h1 {{
            color: white !important;
            margin: 0;
            font-size: 1.2rem;
            font-weight: 600;
            border-bottom: none;
        }}
        
        .dashboard-header p {{
            color: rgba(255,255,255,0.85);
            margin: 0;
            font-size: 0.7rem;
        }}
        
        /* Login Container */
        .login-container {{
            background: linear-gradient(135deg, {HELB_GREEN} 0%, {HELB_BLUE} 100%);
            border-radius: 20px;
            padding: 2.5rem;
            text-align: center;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }}
        
        .login-title {{
            color: white;
            font-size: 1.5rem;
            font-weight: 700;
            margin: 0;
        }}
        
        .login-subtitle {{
            color: rgba(255,255,255,0.85);
            font-size: 0.85rem;
            margin-top: 0.5rem;
        }}
        
        /* KPI Cards */
        .kpi-card {{
            background: linear-gradient(135deg, {HELB_GREEN} 0%, {HELB_BLUE} 100%);
            border-radius: 12px;
            padding: 1rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            text-align: center;
        }}
        
        .kpi-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.15);
        }}
        
        .kpi-label {{
            font-size: 0.7rem;
            text-transform: uppercase;
            color: {HELB_GOLD} !important;
            font-weight: 600;
            letter-spacing: 0.5px;
        }}
        
        .kpi-value {{
            font-size: 1.8rem;
            font-weight: 700;
            margin: 0.3rem 0;
            color: white !important;
            line-height: 1.2;
        }}
        
        .kpi-sub {{
            font-size: 0.6rem;
            color: rgba(255,255,255,0.8) !important;
            margin-top: 0.2rem;
        }}
        
        .progress-bar {{
            height: 4px;
            background: rgba(255,255,255,0.3);
            border-radius: 2px;
            overflow: hidden;
            margin-top: 0.5rem;
        }}
        
        .progress-fill {{
            height: 100%;
            background: {HELB_GOLD};
            border-radius: 2px;
        }}
        
        /* Metric Cards */
        .metric-card {{
            background: {HELB_WHITE};
            border-radius: 12px;
            padding: 1rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            border-left: 4px solid {HELB_GOLD};
            transition: all 0.3s ease;
        }}
        
        /* Metric card text - BLACK for readability */
        .metric-card b, .metric-card span, .metric-card div {{
            color: {HELB_BLACK} !important;
        }}
        
        /* Status Badges */
        .badge-active {{
            background-color: {HELB_GREEN};
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }}
        
        .badge-pending {{
            background-color: #FFB81C;
            color: #1F2937;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }}
        
        .badge-inprogress {{
            background-color: #00529B;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }}
        
        .badge-expired {{
            background-color: #dc2626;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }}
        
        /* Buttons */
        .stButton > button {{
            background: linear-gradient(135deg, {HELB_GREEN} 0%, {HELB_BLUE} 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 10px 20px !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
        }}
        
        .stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }}
        
        /* Delete button */
        .stButton > button[key*="delete"] {{
            background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%) !important;
        }}
        
        /* Expander header */
        .streamlit-expanderHeader {{
            background-color: {HELB_WHITE} !important;
            border-radius: 8px !important;
            border: 1px solid #D1D5DB !important;
        }}
        
        .streamlit-expanderHeader p {{
            color: {HELB_BLACK} !important;
            font-size: 0.9rem !important;
            font-weight: 600 !important;
        }}
        
        .streamlit-expanderHeader:hover {{
            background-color: {HELB_GRAY} !important;
        }}
        
        .streamlit-expanderHeader:hover p {{
            color: {HELB_BLACK} !important;
        }}
        
        /* Expander content area */
        .streamlit-expanderContent {{
            background-color: {HELB_WHITE} !important;
            border: 1px solid #D1D5DB !important;
            border-top: none !important;
            border-radius: 0 0 8px 8px !important;
            padding: 1rem !important;
        }}
        
        /* Expander content text - BLACK */
        .streamlit-expanderContent p, 
        .streamlit-expanderContent span, 
        .streamlit-expanderContent div,
        .streamlit-expanderContent label,
        .streamlit-expanderContent strong {{
            color: {HELB_BLACK} !important;
        }}
        
        /* Input fields */
        .stTextInput input, .stSelectbox div, .stDateInput input, .stNumberInput input, .stTextArea textarea {{
            background-color: white !important;
            color: {HELB_BLACK} !important;
            border: 1px solid #D1D5DB !important;
            border-radius: 6px !important;
            font-size: 0.75rem !important;
        }}
        
        .stTextInput label, .stSelectbox label, .stDateInput label, .stNumberInput label {{
            font-size: 0.7rem !important;
            font-weight: 500 !important;
            color: {HELB_BLACK} !important;
        }}
        
        /* Text area specific */
        .stTextArea textarea {{
            color: {HELB_BLACK} !important;
        }}
        
        .stTextArea label {{
            color: {HELB_BLACK} !important;
        }}
        
        /* Slider */
        .stSlider label {{
            color: {HELB_BLACK} !important;
        }}
        
        /* Checkbox */
        .stCheckbox label {{
            color: {HELB_BLACK} !important;
        }}
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 0.5rem;
            background: {HELB_GRAY};
            padding: 0.5rem;
            border-radius: 12px;
            margin-bottom: 1rem;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            border-radius: 8px;
            padding: 0.5rem 1.2rem;
            font-weight: 500;
            font-size: 0.8rem;
            color: {HELB_DARK};
            white-space: nowrap;
            background-color: {HELB_GRAY};
        }}
        
        .stTabs [aria-selected="true"] {{
            background-color: {HELB_GOLD} !important;
            color: {HELB_DARK} !important;
            font-weight: 600;
        }}
        
        /* Footer */
        .footer {{
            text-align: center;
            padding: 1.5rem;
            color: #6B7280;
            font-size: 0.7rem;
            border-top: 1px solid #E5E7EB;
            margin-top: 2rem;
        }}
        
        /* Dataframe */
        .dataframe {{
            font-size: 0.8rem;
        }}
        
        .dataframe th {{
            background-color: {HELB_GREEN} !important;
            color: white !important;
            padding: 10px !important;
        }}
        
        .dataframe td {{
            color: {HELB_BLACK} !important;
        }}
        
        /* Placeholder text */
        .stTextInput input::placeholder, .stTextArea textarea::placeholder {{
            color: #9CA3AF !important;
        }}
        
        /* Caption text */
        .stCaption, caption {{
            color: #6B7280 !important;
        }}
        
        /* Info boxes */
        .stAlert {{
            background-color: {HELB_GRAY} !important;
            border-left: 4px solid {HELB_GOLD} !important;
        }}
        
        .stAlert p {{
            color: {HELB_BLACK} !important;
        }}
    </style>
    """
else:
    # Dark theme - leave as is (working perfectly)
    THEME_CSS = f"""
    <style>
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        .stAppDeployButton {{display: none;}}
        
        .main, .stApp {{
            background-color: #1a1a2e !important;
        }}
        
        [data-testid="stSidebar"] {{
            background-color: #0f3460 !important;
            padding-top: 1rem;
        }}
        
        [data-testid="stSidebar"] * {{
            color: white !important;
        }}
        
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
        
        [data-testid="stSidebar"] .stButton > button {{
            background-color: rgba(255,255,255,0.2) !important;
            color: white !important;
            font-size: 0.75rem !important;
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
        
        .login-container {{
            background: linear-gradient(135deg, #0f3460 0%, #16213e 100%);
            border-radius: 20px;
            padding: 2.5rem;
            text-align: center;
        }}
        
        .kpi-card {{
            background: linear-gradient(135deg, #0f3460 0%, #16213e 100%);
            border-radius: 12px;
            padding: 1rem;
            text-align: center;
        }}
        
        .kpi-label {{ color: {HELB_GOLD}; font-size: 0.7rem; }}
        .kpi-value {{ color: white; font-size: 1.8rem; }}
        .kpi-sub {{ color: rgba(255,255,255,0.8); font-size: 0.6rem; }}
        
        .metric-card {{
            background: #16213e;
            border-radius: 12px;
            padding: 1rem;
            border-left: 4px solid {HELB_GOLD};
        }}
        
        .stButton > button {{
            background: linear-gradient(135deg, #0f3460 0%, #16213e 100%) !important;
            color: white !important;
        }}
        
        .stTextInput input, .stSelectbox div, .stDateInput input, .stNumberInput input, .stTextArea textarea {{
            background-color: #2d2d44 !important;
            color: white !important;
            border: 1px solid #4a4a6a !important;
            font-size: 0.75rem !important;
        }}
        
        .stTextInput label, .stSelectbox label, .stDateInput label, .stNumberInput label {{ color: #e0e0e0 !important; }}
        
        .streamlit-expanderHeader {{ background-color: #2d2d44 !important; }}
        .streamlit-expanderHeader p {{ color: {HELB_GOLD} !important; font-size: 0.9rem !important; }}
        
        .stTabs [data-baseweb="tab-list"] {{ background: #2d2d44; }}
        .stTabs [aria-selected="true"] {{ background-color: {HELB_GOLD} !important; color: {HELB_DARK} !important; }}
        
        .footer {{
            text-align: center;
            padding: 1.5rem;
            color: #6B7280;
            border-top: 1px solid #2d2d44;
            margin-top: 2rem;
        }}
        
        .stMarkdown, p, span, div, label {{ color: #e0e0e0 !important; }}
    </style>
    """

st.markdown(THEME_CSS, unsafe_allow_html=True)

# ============================================
# SUPABASE CONNECTION
# ============================================
@st.cache_resource
def init_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

# ============================================
# WORK PLAN FUNCTIONS
# ============================================
def get_work_plans():
    """Get work plans based on user role"""
    try:
        if st.session_state.user_role in ["admin", "management"]:
            result = supabase.table("work_plan").select("*").order("created_at", desc=True).execute()
        else:
            result = supabase.table("work_plan").select("*").eq("department_id", st.session_state.user_dept).order("created_at", desc=True).execute()
        return result.data
    except Exception as e:
        return []

def add_work_plan(data):
    try:
        result = supabase.table("work_plan").insert(data).execute()
        return True
    except Exception as e:
        st.error(f"Error adding work plan: {e}")
        return False

def update_work_plan_status(plan_id, new_status, progress_percent=None):
    try:
        update_data = {"status": new_status, "updated_at": datetime.now().isoformat()}
        if progress_percent is not None:
            update_data["progress_percent"] = progress_percent
        supabase.table("work_plan").update(update_data).eq("id", plan_id).execute()
        return True
    except:
        return False

def delete_work_plan(plan_id):
    """Delete work plan - Admin only"""
    try:
        supabase.table("work_plan").delete().eq("id", plan_id).execute()
        return True
    except:
        return False

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
# HELPER FUNCTIONS
# ============================================
def get_department_name(dept_id):
    if dept_id is None:
        return "No Department"
    try:
        result = supabase.table("departments").select("name").eq("id", dept_id).execute()
        return result.data[0]["name"] if result.data else "Unknown Department"
    except:
        return "Unknown Department"

def get_filtered_data(table_name):
    if st.session_state.user_role in ["admin", "management"]:
        return supabase.table(table_name).select("*").execute().data
    else:
        return supabase.table(table_name).select("*").eq("department_id", st.session_state.user_dept).execute().data

def get_all_users():
    try:
        result = supabase.table("users").select("*").execute()
        return result.data
    except:
        return []

def delete_user(username):
    try:
        supabase.table("users").delete().eq("username", username).execute()
        return True
    except:
        return False

def update_user_role(username, new_role, department_id):
    try:
        supabase.table("users").update({
            "role": new_role,
            "department_id": department_id if department_id != "None" else None
        }).eq("username", username).execute()
        return True
    except:
        return False

def reset_user_password(username, new_password):
    try:
        supabase.table("users").update({
            "password_hash": new_password
        }).eq("username", username).execute()
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
        return True, "User created successfully"
    except Exception as e:
        return False, str(e)

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
    if st.button(f"{theme_icon} {theme_label}", key="theme_toggle", help="Toggle between light and dark mode"):
        toggle_theme()

with col_refresh:
    if st.button("🔄 Refresh", key="global_refresh"):
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
        st.rerun()

# ============================================
# WORK PLANS MODULE
# ============================================
if choice == "📋 Work Plans":
    if st.session_state.user_role in ["admin", "management"]:
        st.markdown("<h2>📋 Institution-Wide Work Plan</h2>", unsafe_allow_html=True)
        st.markdown("<p style='margin-bottom: 1rem;'>Enterprise-wide strategic planning and performance management</p>", unsafe_allow_html=True)
    else:
        st.markdown(f"<h2>📋 {st.session_state.user_dept_name} Department Work Plan</h2>", unsafe_allow_html=True)
        st.markdown("<p style='margin-bottom: 1rem;'>Departmental strategic planning and performance management</p>", unsafe_allow_html=True)
    
    work_plans = get_work_plans()
    
    tab_add, tab_view, tab_dashboard = st.tabs(["➕ Add Work Plan Activity", "📊 View All Activities", "📈 Performance Dashboard"])
    
    # ============================================
    # TAB 1: ADD NEW WORK PLAN ACTIVITY
    # ============================================
    with tab_add:
        st.markdown("### Add New Work Plan Activity")
        
        with st.form("add_work_plan_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                strategic_pillar = st.selectbox("Strategic Issue (Pillar)*", STRATEGIC_PILLARS)
                strategy = st.text_area("Strategy", placeholder="e.g., Enhance customer service through digital platforms", height=80, help="Optional but recommended")
                key_result_area = st.text_input("Key Result Area*", placeholder="e.g., Improve customer satisfaction score")
                planned_activity = st.text_area("Planned Activity*", placeholder="Describe the activity in detail")
                performance_indicator = st.text_input("Performance Indicator*", placeholder="e.g., Customer satisfaction score")
            
            with col2:
                budget_allocation = st.number_input("Budget Allocation (KShs.)", min_value=0.0, step=10000.0, format="%.2f", help="Optional - leave as 0 if not applicable")
                annual_target = st.text_input("Annual Target*", placeholder="e.g., 90% satisfaction rate")
                due_date = st.date_input("Due Date*")
                activity_category = st.selectbox("Activity Category*", ACTIVITY_CATEGORIES)
                dept_name = st.session_state.user_dept_name if st.session_state.user_dept_name else "Current Department"
                st.text_input("Department", value=dept_name, disabled=True)
            
            submitted = st.form_submit_button("Save Work Plan Activity", use_container_width=True)
            
            if submitted:
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
                    else:
                        st.error("Failed to add work plan activity.")
    
    # ============================================
    # TAB 2: VIEW ALL ACTIVITIES
    # ============================================
    with tab_view:
        if st.session_state.user_role in ["admin", "management"]:
            st.markdown("### All Department Work Plans (Institution-Wide)")
        else:
            st.markdown(f"### {st.session_state.user_dept_name} Department Work Plan Activities")
        
        if work_plans:
            col_filter1, col_filter2, col_filter3 = st.columns(3)
            with col_filter1:
                pillar_filter = st.multiselect("Filter by Pillar", STRATEGIC_PILLARS, default=[])
            with col_filter2:
                status_filter = st.multiselect("Filter by Status", STATUS_OPTIONS, default=[])
            with col_filter3:
                category_filter = st.multiselect("Filter by Category", ACTIVITY_CATEGORIES, default=[])
            
            if st.session_state.user_role in ["admin", "management"]:
                with col_filter1:
                    departments_list = list(set([p.get("department_name", "Unknown") for p in work_plans if p.get("department_name")]))
                    dept_filter = st.multiselect("Filter by Department", departments_list, default=[])
            else:
                dept_filter = []
            
            filtered_plans = work_plans
            if pillar_filter:
                filtered_plans = [p for p in filtered_plans if p.get("strategic_pillar") in pillar_filter]
            if status_filter:
                filtered_plans = [p for p in filtered_plans if p.get("status") in status_filter]
            if category_filter:
                filtered_plans = [p for p in filtered_plans if p.get("activity_category") in category_filter]
            if dept_filter:
                filtered_plans = [p for p in filtered_plans if p.get("department_name") in dept_filter]
            
            st.markdown(f"**Showing {len(filtered_plans)} activities**")
            
            for plan in filtered_plans:
                if plan.get("status") == "Done":
                    badge = '<span class="badge-active">✅ Done</span>'
                elif plan.get("status") == "In Progress":
                    badge = '<span class="badge-inprogress">🔄 In Progress</span>'
                else:
                    badge = '<span class="badge-pending">⏳ Pending</span>'
                
                due_date = datetime.strptime(plan["due_date"], "%Y-%m-%d").date()
                days_left = (due_date - datetime.now().date()).days
                
                expander_title = f"📌 {plan['planned_activity'][:80]}... - {plan.get('strategic_pillar', 'N/A')}"
                if st.session_state.user_role in ["admin", "management"] and plan.get('department_name'):
                    expander_title += f" - {plan.get('department_name', 'N/A')}"
                
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
                        else:
                            st.markdown("**Budget:** Not applicable")
                        
                        st.markdown("---")
                        st.markdown("**Update Progress**")
                        
                        new_status = st.selectbox(
                            "Update Status", 
                            STATUS_OPTIONS, 
                            index=STATUS_OPTIONS.index(plan.get("status", "Pending")),
                            key=f"status_{plan['id']}"
                        )
                        
                        new_progress = st.slider(
                            "Progress %", 
                            0, 100, 
                            value=plan.get("progress_percent", 0),
                            key=f"progress_{plan['id']}"
                        )
                        
                        col_update, col_delete = st.columns(2)
                        with col_update:
                            if st.button(f"Update", key=f"update_{plan['id']}"):
                                if update_work_plan_status(plan['id'], new_status, new_progress):
                                    st.success("✅ Updated successfully!")
                                    st.rerun()
                        
                        with col_delete:
                            if st.session_state.user_role == "admin":
                                if st.button(f"🗑️ Delete", key=f"delete_{plan['id']}"):
                                    if delete_work_plan(plan['id']):
                                        st.success("✅ Deleted successfully!")
                                        st.rerun()
                    
                    st.markdown("---")
                    st.caption(f"Created: {plan.get('created_at', 'N/A')[:10] if plan.get('created_at') else 'N/A'}")
        else:
            st.info("No work plan activities found. Click 'Add Work Plan Activity' to get started.")
    
    # ============================================
    # TAB 3: PERFORMANCE DASHBOARD
    # ============================================
    with tab_dashboard:
        if st.session_state.user_role in ["admin", "management"]:
            st.markdown("### 📊 Institution-Wide Work Plan Performance Dashboard")
        else:
            st.markdown(f"### 📊 {st.session_state.user_dept_name} Department Performance Dashboard")
        
        if work_plans:
            df = pd.DataFrame(work_plans)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_activities = len(df)
                st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-label'>📋 TOTAL ACTIVITIES</div>
                    <div class='kpi-value'>{total_activities}</div>
                    <div class='kpi-sub'>Total work plan items</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                completed = len(df[df['status'] == 'Done'])
                completion_rate = (completed / total_activities * 100) if total_activities > 0 else 0
                st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-label'>✅ COMPLETION RATE</div>
                    <div class='kpi-value'>{completion_rate:.1f}%</div>
                    <div class='progress-bar'><div class='progress-fill' style='width:{completion_rate}%;'></div></div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                total_budget = df['budget_allocation'].fillna(0).sum()
                st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-label'>💰 TOTAL BUDGET</div>
                    <div class='kpi-value'>KES {total_budget/1e6:.1f}M</div>
                    <div class='kpi-sub'>Allocated funds</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                in_progress = len(df[df['status'] == 'In Progress'])
                st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-label'>🔄 IN PROGRESS</div>
                    <div class='kpi-value'>{in_progress}</div>
                    <div class='kpi-sub'>Active activities</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                st.markdown("#### Status Distribution by Pillar")
                status_by_pillar = df.groupby(['strategic_pillar', 'status']).size().reset_index(name='count')
                fig = px.bar(status_by_pillar, x='strategic_pillar', y='count', color='status',
                            color_discrete_map={'Done': HELB_GREEN, 'In Progress': HELB_BLUE, 'Pending': HELB_GOLD},
                            title="Activity Status by Strategic Pillar")
                fig.update_layout(height=400, xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
            
            with col_chart2:
                st.markdown("#### Budget Allocation by Pillar")
                budget_data = df[df['budget_allocation'].notna() & (df['budget_allocation'] > 0)]
                if not budget_data.empty:
                    budget_by_pillar = budget_data.groupby('strategic_pillar')['budget_allocation'].sum().reset_index()
                    fig = px.pie(budget_by_pillar, values='budget_allocation', names='strategic_pillar',
                                title="Budget Distribution by Pillar",
                                color_discrete_sequence=[HELB_GREEN, HELB_GOLD, HELB_BLUE, "#FF6B6B", "#4ECDC4"])
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No budget data available for chart")
            
            if st.session_state.user_role in ["admin", "management"]:
                st.markdown("#### Department Performance Overview")
                dept_performance = df.groupby('department_name').agg({
                    'id': 'count',
                    'status': lambda x: (x == 'Done').sum(),
                    'progress_percent': 'mean'
                }).reset_index()
                dept_performance.columns = ['Department', 'Total Activities', 'Completed', 'Avg Progress %']
                dept_performance['Completion Rate %'] = (dept_performance['Completed'] / dept_performance['Total Activities'] * 100).round(1)
                
                fig = px.bar(dept_performance, x='Department', y='Completion Rate %',
                            title="Completion Rate by Department",
                            color='Completion Rate %', color_continuous_scale='Greens',
                            text='Completion Rate %')
                fig.update_traces(textposition='outside')
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            with st.expander("📋 Detailed Work Plan Data", expanded=False):
                display_cols = ['strategic_pillar', 'key_result_area', 'planned_activity', 
                               'performance_indicator', 'budget_allocation', 'status', 
                               'progress_percent', 'due_date', 'department_name']
                display_df = df[display_cols] if all(col in df.columns for col in display_cols) else df
                st.dataframe(display_df, use_container_width=True, hide_index=True)
                
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Export Work Plan Data", csv, f"work_plan_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")
        else:
            st.info("No data available. Add work plan activities to see the dashboard.")

# ============================================
# DASHBOARD
# ============================================
elif choice == "📊 Dashboard":
    st.subheader("Dashboard Overview")
    
    work_plans = get_work_plans()
    contracts = get_filtered_data("contracts")
    policies = get_filtered_data("policies")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if work_plans:
            completed = sum(1 for w in work_plans if w.get("status") == "Done")
            total = len(work_plans)
            avg_progress = sum(w.get("progress_percent", 0) for w in work_plans) / total if total > 0 else 0
            st.markdown(f"""
            <div class='kpi-card'>
                <div class='kpi-label'>📋 WORK PLANS</div>
                <div class='kpi-value'>{completed}/{total}</div>
                <div class='progress-bar'><div class='progress-fill' style='width:{avg_progress}%;'></div></div>
                <div class='kpi-sub'>Completion Progress</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='kpi-card'>
                <div class='kpi-label'>📋 WORK PLANS</div>
                <div class='kpi-value'>0/0</div>
                <div class='kpi-sub'>No plans yet</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        if contracts:
            expiring = sum(1 for c in contracts if c.get("status") == "expiring_soon")
            total_contracts = len(contracts)
            st.markdown(f"""
            <div class='kpi-card'>
                <div class='kpi-label'>📄 CONTRACTS</div>
                <div class='kpi-value'>{expiring}</div>
                <div class='kpi-sub'>expiring within 30 days out of {total_contracts}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='kpi-card'>
                <div class='kpi-label'>📄 CONTRACTS</div>
                <div class='kpi-value'>0</div>
                <div class='kpi-sub'>No contracts yet</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        if policies:
            expiring_policies = 0
            total_policies = len(policies)
            for p in policies:
                try:
                    expiry = datetime.strptime(p["expiry_date"], "%Y-%m-%d").date()
                    if (expiry - datetime.now().date()).days <= 90:
                        expiring_policies += 1
                except:
                    pass
            st.markdown(f"""
            <div class='kpi-card'>
                <div class='kpi-label'>📜 POLICIES</div>
                <div class='kpi-value'>{expiring_policies}</div>
                <div class='kpi-sub'>expiring within 90 days out of {total_policies}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='kpi-card'>
                <div class='kpi-label'>📜 POLICIES</div>
                <div class='kpi-value'>0</div>
                <div class='kpi-sub'>No policies yet</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col4:
        users_count = len(supabase.table("users").select("*").execute().data)
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-label'>👥 ACTIVE USERS</div>
            <div class='kpi-value'>{users_count}</div>
            <div class='kpi-sub'>System users</div>
        </div>
        """, unsafe_allow_html=True)
    
    if work_plans and len(work_plans) > 0:
        st.subheader("📈 Work Plan Performance Overview")
        df = pd.DataFrame(work_plans)
        
        if st.session_state.user_role in ["admin", "management"]:
            dept_progress = df.groupby('department_name').agg({
                'progress_percent': 'mean',
                'status': lambda x: (x == 'Done').sum()
            }).reset_index()
            dept_progress.columns = ['Department', 'Avg Progress %', 'Completed']
            fig = px.bar(dept_progress, x='Department', y='Avg Progress %',
                        title="Average Progress by Department",
                        color='Avg Progress %', color_continuous_scale='Greens')
        else:
            status_counts = df['status'].value_counts().reset_index()
            status_counts.columns = ['Status', 'Count']
            fig = px.pie(status_counts, values='Count', names='Status',
                        title="Work Plan Status Distribution",
                        color_discrete_sequence=[HELB_GREEN, HELB_BLUE, HELB_GOLD])
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    st.success(f"👋 Welcome, {st.session_state.user_fullname}!")

# ============================================
# CONTRACTS (simplified - working)
# ============================================
elif choice == "📄 Contracts":
    st.subheader("Contract Tracker")
    
    with st.expander("➕ Add New Contract", expanded=False):
        with st.form("new_contract"):
            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input("Contract Title*")
                vendor = st.text_input("Vendor*")
            with col2:
                end_date = st.date_input("End Date*")
                auto_renew = st.checkbox("Auto-renewal")
            
            if st.form_submit_button("Save Contract", use_container_width=True):
                if title and vendor:
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
                    st.success("Contract added successfully!")
                    st.rerun()
                else:
                    st.error("Please fill all required fields")
    
    contracts = get_filtered_data("contracts")
    if contracts:
        for contract in contracts:
            end_date = datetime.strptime(contract["end_date"], "%Y-%m-%d").date()
            days_left = (end_date - datetime.now().date()).days
            
            if days_left > 30:
                badge = "🟢 Active"
            elif days_left > 0:
                badge = "🟡 Expiring Soon"
            else:
                badge = "🔴 Expired"
            
            st.markdown(f"""
            <div class='metric-card'>
                <b>{badge} - {contract['contract_title']}</b><br>
                Vendor: {contract['vendor_name']}<br>
                End Date: {contract['end_date']} | {days_left} days remaining<br>
                Auto-renewal: {'Yes' if contract['auto_renewal'] else 'No'}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No contracts found. Click 'Add New Contract' to get started.")

# ============================================
# POLICIES (simplified - working)
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
    
    policies = get_filtered_data("policies")
    if policies:
        for policy in policies:
            expiry = datetime.strptime(policy["expiry_date"], "%Y-%m-%d").date()
            days_left = (expiry - datetime.now().date()).days
            
            if days_left > 90:
                badge = "🟢 Active"
            elif days_left > 0:
                badge = "🟡 Expiring Soon"
            else:
                badge = "🔴 Expired"
            
            st.markdown(f"""
            <div class='metric-card'>
                <b>{badge} - 📜 {policy['policy_name']}</b><br>
                Expires: {policy['expiry_date']} ({days_left} days left)
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No policies found. Click 'Add New Policy' to get started.")

# ============================================
# USER MANAGEMENT (ADMIN ONLY)
# ============================================
elif choice == "👥 User Management" and st.session_state.user_role == "admin":
    st.subheader("User Management - Admin Panel")
    
    depts = supabase.table("departments").select("id,name").execute().data
    dept_options = {d["name"]: d["id"] for d in depts}
    users = get_all_users()
    
    tab1, tab2, tab3 = st.tabs(["➕ Create New User", "✏️ Edit User Role", "🗑️ Delete User"])
    
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
        
        st.markdown("#### Department Performance Summary")
        
        performance_data = []
        for dept in df['department_name'].unique():
            dept_df = df[df['department_name'] == dept]
            total = len(dept_df)
            completed = len(dept_df[dept_df['status'] == 'Done'])
            avg_progress = dept_df['progress_percent'].mean()
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
        
        st.markdown("#### Strategic Pillar Analysis")
        pillar_summary = df.groupby('strategic_pillar').agg({
            'id': 'count',
            'progress_percent': 'mean',
            'budget_allocation': 'sum'
        }).reset_index()
        pillar_summary.columns = ['Strategic Pillar', 'Total Activities', 'Avg Progress %', 'Total Budget']
        
        fig = px.bar(pillar_summary, x='Strategic Pillar', y='Avg Progress %',
                    title="Progress by Strategic Pillar",
                    color='Avg Progress %', color_continuous_scale='Greens')
        fig.update_layout(height=400, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
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
        all_contracts = supabase.table("contracts").select("*").execute().data
        if all_contracts:
            df = pd.DataFrame(all_contracts)
            depts = supabase.table("departments").select("id,name").execute().data
            dept_names = {d["id"]: d["name"] for d in depts}
            df["department"] = df["department_id"].map(dept_names)
            st.dataframe(df[["contract_title", "vendor_name", "department", "end_date", "status"]], use_container_width=True, hide_index=True)
        else:
            st.info("No contracts found")
    
    with tabs[2]:
        all_policies = supabase.table("policies").select("*").execute().data
        if all_policies:
            df = pd.DataFrame(all_policies)
            depts = supabase.table("departments").select("id,name").execute().data
            dept_names = {d["id"]: d["name"] for d in depts}
            df["department"] = df["department_id"].map(dept_names).fillna("Global")
            st.dataframe(df[["policy_name", "department", "expiry_date"]], use_container_width=True, hide_index=True)
        else:
            st.info("No policies found")

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown("""
<div class='footer'>
    <p>© 2025 HELB - Higher Education Loans Board | Strategy Performance Management System</p>
    <p>Powered by Streamlit | Work Plan Management | Secure & Real-time</p>
</div>
""", unsafe_allow_html=True)
