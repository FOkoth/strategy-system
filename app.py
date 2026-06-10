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
HELB_GREEN = "#00843D"      # HELB Green - Primary
HELB_GOLD = "#FFB81C"        # HELB Gold - Accent
HELB_BLUE = "#00529B"        # HELB Blue - Secondary
HELB_DARK = "#1F2937"        # Dark text
HELB_WHITE = "#FFFFFF"       # White background
HELB_GRAY = "#F8FAFC"        # Light gray for cards
HELB_BORDER = "#E5E7EB"      # Border color

# Page config
st.set_page_config(
    page_title="HELB Strategy Performance System",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# LOAD HELB LOGO - Clean with transparent background
# ============================================
def get_logo_base64():
    """Load HELB logo and return clean base64 without background artifacts"""
    try:
        # Try to get logo URL from secrets
        logo_url = st.secrets.get("HELB_LOGO_URL", "")
        
        if logo_url:
            response = requests.get(logo_url, timeout=10)
            if response.status_code == 200:
                img = Image.open(BytesIO(response.content))
                
                # Convert to RGBA to handle transparency
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                # Create a white background and composite
                white_bg = Image.new('RGBA', img.size, (255, 255, 255, 255))
                img = Image.alpha_composite(white_bg, img)
                
                # Convert to RGB for PNG
                img = img.convert('RGB')
                
                # Resize maintaining aspect ratio
                img.thumbnail((250, 100), Image.Resampling.LANCZOS)
                
                buffered = BytesIO()
                img.save(buffered, format="PNG", optimize=True)
                return base64.b64encode(buffered.getvalue()).decode()
    except Exception as e:
        st.warning(f"Could not load logo from URL: {e}")
    
    try:
        # Fallback to local file
        img = Image.open("HELB Logo.png")
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        white_bg = Image.new('RGBA', img.size, (255, 255, 255, 255))
        img = Image.alpha_composite(white_bg, img)
        img = img.convert('RGB')
        img.thumbnail((250, 100), Image.Resampling.LANCZOS)
        buffered = BytesIO()
        img.save(buffered, format="PNG", optimize=True)
        return base64.b64encode(buffered.getvalue()).decode()
    except:
        return None

def get_logo_small():
    """Get smaller version of logo for sidebar and header"""
    try:
        logo_url = st.secrets.get("HELB_LOGO_URL", "")
        if logo_url:
            response = requests.get(logo_url, timeout=10)
            if response.status_code == 200:
                img = Image.open(BytesIO(response.content))
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                white_bg = Image.new('RGBA', img.size, (255, 255, 255, 255))
                img = Image.alpha_composite(white_bg, img)
                img = img.convert('RGB')
                img.thumbnail((120, 48), Image.Resampling.LANCZOS)
                buffered = BytesIO()
                img.save(buffered, format="PNG", optimize=True)
                return base64.b64encode(buffered.getvalue()).decode()
    except:
        pass
    return None

# Load logos
LOGO_LARGE = get_logo_base64()
LOGO_SMALL = get_logo_small()

# ============================================
# CUSTOM CSS - Light Theme Only
# ============================================
st.markdown(f"""
<style>
    /* Hide Streamlit branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    .stAppDeployButton {{display: none;}}
    
    /* Main container - White background */
    .stApp, .main {{
        background-color: {HELB_WHITE} !important;
    }}
    
    /* Sidebar - HELB Green */
    [data-testid="stSidebar"] {{
        background-color: {HELB_GREEN} !important;
        padding-top: 1rem;
    }}
    
    [data-testid="stSidebar"] * {{
        color: white !important;
    }}
    
    [data-testid="stSidebar"] .stMarkdown {{
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
    
    /* Navigation radio buttons - Gold background */
    [data-testid="stSidebar"] div[role="radiogroup"] label {{
        background-color: {HELB_GOLD} !important;
        color: {HELB_GREEN} !important;
        border-radius: 8px !important;
        padding: 10px 15px !important;
        margin: 5px 0 !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }}
    
    [data-testid="stSidebar"] div[role="radiogroup"] label:hover {{
        transform: translateX(5px);
        filter: brightness(1.05);
    }}
    
    /* Sidebar button */
    [data-testid="stSidebar"] .stButton > button {{
        background-color: rgba(255,255,255,0.2) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.3) !important;
    }}
    
    /* Headers - Green */
    h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{
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
    
    /* Login Container - Solid Green */
    .login-container {{
        background-color: {HELB_GREEN};
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
    
    /* Login form inputs */
    .login-container .stTextInput input {{
        border-radius: 8px;
        border: none;
        padding: 10px;
        background-color: white;
        color: {HELB_DARK};
    }}
    
    .login-container .stButton button {{
        background-color: {HELB_GOLD} !important;
        color: {HELB_GREEN} !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px !important;
    }}
    
    /* KPI Cards - Solid Green */
    .kpi-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 1rem;
        margin-bottom: 1.5rem;
    }}
    
    .kpi-card {{
        background: {HELB_GREEN};
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }}
    
    .kpi-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 5px 20px rgba(0,0,0,0.15);
    }}
    
    .kpi-label {{
        font-size: 0.7rem;
        text-transform: uppercase;
        color: {HELB_GOLD};
        font-weight: 600;
        letter-spacing: 0.5px;
    }}
    
    .kpi-value {{
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0.3rem 0;
        color: white;
        line-height: 1.2;
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
    
    /* Metric Cards - White with left gold border */
    .metric-card {{
        background: {HELB_WHITE};
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        border-left: 4px solid {HELB_GOLD};
        transition: all 0.3s ease;
        margin-bottom: 0.5rem;
    }}
    
    .metric-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 5px 20px rgba(0,0,0,0.12);
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
    
    .badge-expiring {{
        background-color: {HELB_GOLD};
        color: {HELB_GREEN};
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
    
    /* Tabs - Light gray background, gold when selected */
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
        transition: all 0.2s;
        background-color: {HELB_GRAY};
    }}
    
    .stTabs [aria-selected="true"] {{
        background-color: {HELB_GOLD} !important;
        color: {HELB_GREEN} !important;
        font-weight: 600;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }}
    
    .stTabs [data-baseweb="tab"]:hover {{
        background-color: rgba(255,184,28,0.2);
    }}
    
    /* Expander */
    .streamlit-expanderHeader {{
        background-color: {HELB_GRAY} !important;
        border-radius: 8px !important;
        color: {HELB_GREEN} !important;
        font-weight: 600 !important;
        border: 1px solid {HELB_BORDER} !important;
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
    
    /* Info/Warning boxes */
    .stAlert {{
        border-radius: 10px;
    }}
    
    /* Footer */
    .footer {{
        text-align: center;
        padding: 1.5rem;
        color: #6B7280;
        font-size: 0.7rem;
        border-top: 1px solid {HELB_BORDER};
        margin-top: 2rem;
    }}
    
    /* Text colors for light theme */
    p, li, .stMarkdown, .stText {{
        color: {HELB_DARK} !important;
    }}
    
    /* Input fields */
    .stTextInput input, .stSelectbox select, .stTextArea textarea {{
        background-color: {HELB_WHITE} !important;
        border: 1px solid {HELB_BORDER} !important;
        border-radius: 8px !important;
        color: {HELB_DARK} !important;
    }}
    
    /* Success message */
    .stSuccess {{
        background-color: #E8F5E9 !important;
        border-left: 4px solid {HELB_GREEN} !important;
    }}
</style>
""", unsafe_allow_html=True)

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
# SESSION STATE
# ============================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
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

def get_all_users():
    """Get all users for admin management"""
    try:
        result = supabase.table("users").select("*").execute()
        return result.data
    except:
        return []

def delete_user(username):
    """Delete a user"""
    try:
        supabase.table("users").delete().eq("username", username).execute()
        return True
    except:
        return False

def update_user_role(username, new_role, department_id):
    """Update user role and department"""
    try:
        supabase.table("users").update({
            "role": new_role,
            "department_id": department_id if department_id != "None" else None
        }).eq("username", username).execute()
        return True
    except:
        return False

def reset_user_password(username, new_password):
    """Reset user password"""
    try:
        supabase.table("users").update({
            "password_hash": new_password
        }).eq("username", username).execute()
        return True
    except:
        return False

def create_new_user(username, full_name, password, role, department_id):
    """Create a new user"""
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
        # Display crisp logo
        if LOGO_LARGE:
            logo_html = f'<img src="data:image/png;base64,{LOGO_LARGE}" style="width: 220px; height: auto; margin-bottom: 1rem; display: block; margin-left: auto; margin-right: auto;">'
        else:
            logo_html = '<div style="font-size: 3rem; margin-bottom: 1rem; text-align: center;">🏦</div>'
        
        st.markdown(f"""
        <div class='login-container'>
            <div style="padding: 0.5rem;">{logo_html}</div>
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
                            st.session_state.authenticated = True
                            st.session_state.user = user
                            st.session_state.user_role = user["role"]
                            st.session_state.user_dept = user["department_id"]
                            st.session_state.user_name = user["username"]
                            st.session_state.user_fullname = user["full_name"]
                            st.session_state.user_id = user["id"]
                            st.rerun()
                        else:
                            st.error("❌ Invalid password")
                    else:
                        st.error("❌ User not found")
                else:
                    st.warning("Please enter both username and password")
    st.stop()

# ============================================
# MAIN APPLICATION (LOGGED IN)
# ============================================

# Dashboard Header with small logo
col_header, col_refresh = st.columns([6, 1])
with col_header:
    if LOGO_SMALL:
        logo_html = f'<img src="data:image/png;base64,{LOGO_SMALL}" style="width: 35px; height: auto;">'
    else:
        logo_html = '<div style="font-size: 1.3rem;">🏦</div>'
    
    st.markdown(f"""
    <div class='dashboard-header'>
        <div class='header-left'>
            {logo_html}
            <div>
                <h1>HELB Strategy Performance Management System</h1>
                <p>Real-time monitoring | Action plans | Contracts | Policies</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
with col_refresh:
    if st.button("🔄 Refresh", key="global_refresh"):
        st.rerun()

# Sidebar with small logo
with st.sidebar:
    if LOGO_SMALL:
        st.markdown(f'<div style="text-align: center; padding: 0.5rem 0;"><img src="data:image/png;base64,{LOGO_SMALL}" style="width: 100px; height: auto;"></div>', unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='text-align: center; padding: 0.5rem 0;'>
            <div style='font-size: 2rem;'>🏦</div>
            <p style='color: white; font-weight: 700; margin: 0; font-size: 0.9rem;'>HELB</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class='sidebar-user-info'>
        <strong>{st.session_state.user_fullname}</strong><br>
        <span style='font-size: 0.7rem;'>{st.session_state.user_role.replace('_', ' ').title()}</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Navigation menu
    menu_options = ["📊 Dashboard", "✅ Action Plans", "📄 Contracts", "📋 Policies"]
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
# REST OF THE APP (Dashboard, Action Plans, Contracts, Policies, User Management, Enterprise View)
# ============================================

# [The remaining code for Dashboard, Action Plans, Contracts, Policies, 
#  User Management, and Enterprise View remains the same as the previous version]
# ... (continue with the same functions from the previous working code)
