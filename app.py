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
HELB_GRAY = "#F9FAFB"        # Light gray for cards

# Page config
st.set_page_config(
    page_title="HELB Strategy Performance System",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# LOAD HELB LOGO FROM URL
# ============================================
def get_logo_base64():
    """Load HELB logo from URL and convert to base64"""
    try:
        # Get logo URL from secrets or use default
        logo_url = st.secrets.get("HELB_LOGO_URL", "https://raw.githubusercontent.com/YOUR_USERNAME/strategy-system/main/HELB%20Logo.png")
        response = requests.get(logo_url, timeout=10)
        if response.status_code == 200:
            # Open image from bytes
            img = Image.open(BytesIO(response.content))
            # Resize for different uses while maintaining aspect ratio
            return {
                "large": resize_and_encode(img, 250, 100),
                "medium": resize_and_encode(img, 150, 60),
                "small": resize_and_encode(img, 80, 32),
                "original": base64.b64encode(response.content).decode()
            }
    except Exception as e:
        st.warning(f"Could not load logo from URL: {e}")
    
    # Fallback to local file
    try:
        img = Image.open("HELB Logo.png")
        return {
            "large": resize_and_encode(img, 250, 100),
            "medium": resize_and_encode(img, 150, 60),
            "small": resize_and_encode(img, 80, 32),
            "original": None
        }
    except:
        return None

def resize_and_encode(img, width, height):
    """Resize image maintaining aspect ratio and return base64"""
    # Calculate new size maintaining aspect ratio
    img_copy = img.copy()
    img_copy.thumbnail((width, height), Image.Resampling.LANCZOS)
    
    # Convert to RGB if necessary
    if img_copy.mode in ('RGBA', 'P'):
        img_copy = img_copy.convert('RGB')
    
    buffered = BytesIO()
    img_copy.save(buffered, format="PNG", optimize=True)
    return base64.b64encode(buffered.getvalue()).decode()

# Load logo once
LOGO_BASE64 = get_logo_base64()

# ============================================
# CUSTOM CSS - Professional HELB Design
# ============================================
st.markdown(f"""
<style>
    /* Hide Streamlit branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    .stAppDeployButton {{display: none;}}
    
    /* Main container - White background */
    .main {{
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
        color: {HELB_DARK} !important;
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
    
    /* Logout button */
    [data-testid="stSidebar"] .stButton > button {{
        background-color: rgba(255,255,255,0.2) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.3) !important;
    }}
    
    /* Headers */
    h1, h2, h3 {{
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
    
    .login-logo {{
        margin-bottom: 1rem;
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
    }}
    
    .login-container .stButton button {{
        background-color: {HELB_GOLD} !important;
        color: {HELB_DARK} !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px !important;
    }}
    
    /* KPI Cards */
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
    
    /* Metric Cards */
    .metric-card {{
        background: {HELB_WHITE};
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        border-left: 4px solid {HELB_GOLD};
        transition: all 0.3s ease;
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
        color: {HELB_DARK};
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
    
    /* Danger button */
    div[data-testid="column"]:has(button[key*="delete"]) button {{
        background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%) !important;
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
        transition: all 0.2s;
        background-color: {HELB_GRAY};
    }}
    
    .stTabs [aria-selected="true"] {{
        background-color: {HELB_GOLD} !important;
        color: {HELB_DARK} !important;
        font-weight: 600;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }}
    
    /* Expander */
    .streamlit-expanderHeader {{
        background-color: {HELB_GRAY} !important;
        border-radius: 8px !important;
        color: {HELB_GREEN} !important;
        font-weight: 600 !important;
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
        # Display logo
        if LOGO_BASE64 and LOGO_BASE64.get("large"):
            logo_html = f'<img src="data:image/png;base64,{LOGO_BASE64["large"]}" style="width: 200px; height: auto; margin-bottom: 1rem;">'
        else:
            logo_html = '<div style="font-size: 3rem; margin-bottom: 1rem;">🏦</div>'
        
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

# Dashboard Header with logo
col_header, col_refresh = st.columns([6, 1])
with col_header:
    if LOGO_BASE64 and LOGO_BASE64.get("small"):
        logo_html = f'<img src="data:image/png;base64,{LOGO_BASE64["small"]}" style="width: 40px; height: auto;">'
    else:
        logo_html = '<div style="font-size: 1.5rem;">🏦</div>'
    
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

# Sidebar with logo
with st.sidebar:
    if LOGO_BASE64 and LOGO_BASE64.get("medium"):
        st.markdown(f'<div style="text-align: center; padding: 0.5rem 0;"><img src="data:image/png;base64,{LOGO_BASE64["medium"]}" style="width: 120px; height: auto;"></div>', unsafe_allow_html=True)
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
# DASHBOARD
# ============================================
if choice == "📊 Dashboard":
    st.subheader("Dashboard Overview")
    
    plans = get_filtered_data("action_plans")
    contracts = get_filtered_data("contracts")
    policies = get_filtered_data("policies")
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if plans:
            completed = sum(1 for p in plans if p.get("status") == "completed")
            total = len(plans)
            avg_progress = sum(p.get("progress_percent", 0) for p in plans) / total if total > 0 else 0
            st.markdown(f"""
            <div class='kpi-card'>
                <div class='kpi-label'>📋 ACTION PLANS</div>
                <div class='kpi-value'>{completed}/{total}</div>
                <div class='progress-bar'><div class='progress-fill' style='width:{avg_progress}%;'></div></div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='kpi-card'>
                <div class='kpi-label'>📋 ACTION PLANS</div>
                <div class='kpi-value'>0/0</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        if contracts:
            expiring = sum(1 for c in contracts if c.get("status") == "expiring_soon")
            st.markdown(f"""
            <div class='kpi-card'>
                <div class='kpi-label'>📄 CONTRACTS</div>
                <div class='kpi-value'>{expiring}</div>
                <div class='kpi-label' style='font-size:0.6rem;'>expiring within 30 days</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='kpi-card'>
                <div class='kpi-label'>📄 CONTRACTS</div>
                <div class='kpi-value'>0</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        if policies:
            expiring_policies = 0
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
                <div class='kpi-label' style='font-size:0.6rem;'>expiring within 90 days</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='kpi-card'>
                <div class='kpi-label'>📜 POLICIES</div>
                <div class='kpi-value'>0</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col4:
        users_count = len(supabase.table("users").select("*").execute().data)
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-label'>👥 ACTIVE USERS</div>
            <div class='kpi-value'>{users_count}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Progress Chart
    if plans and len(plans) > 0:
        st.subheader("📈 Department Performance Overview")
        df = pd.DataFrame(plans)
        if st.session_state.user_role in ["admin", "management"]:
            depts = supabase.table("departments").select("id,name").execute().data
            dept_map = {d["id"]: d["name"] for d in depts}
            df["department"] = df["department_id"].map(dept_map)
            fig = px.bar(df, x="task_name", y="progress_percent", color="department", 
                        title="Action Plan Progress by Task",
                        color_discrete_sequence=[HELB_GREEN, HELB_GOLD, HELB_BLUE])
        else:
            fig = px.bar(df, x="task_name", y="progress_percent", color="status",
                        title="My Department's Action Plan Progress",
                        color_discrete_sequence=[HELB_GREEN, HELB_GOLD, HELB_BLUE])
        
        fig.update_layout(
            barmode='group', 
            bargap=0.3, 
            plot_bgcolor=HELB_WHITE,
            title_font_color=HELB_GREEN,
            title_font_size=16
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.success(f"👋 Welcome, {st.session_state.user_fullname}!")

# ============================================
# ACTION PLANS
# ============================================
elif choice == "✅ Action Plans":
    st.subheader("Action Plan Monitor")
    
    with st.expander("➕ Add New Action Item", expanded=False):
        with st.form("new_action"):
            col1, col2 = st.columns(2)
            with col1:
                task_name = st.text_input("Task Name*")
                due_date = st.date_input("Due Date*")
            with col2:
                status = st.selectbox("Status*", ["not started", "in progress", "completed", "delayed"])
                progress = st.slider("Progress %", 0, 100)
            
            if st.form_submit_button("Save Action Item", use_container_width=True):
                if task_name:
                    supabase.table("action_plans").insert({
                        "task_name": task_name,
                        "due_date": due_date.isoformat(),
                        "status": status,
                        "progress_percent": progress,
                        "department_id": st.session_state.user_dept,
                        "last_updated_by": st.session_state.user_id
                    }).execute()
                    st.success("✅ Action item added successfully!")
                    st.rerun()
                else:
                    st.error("Please enter a task name")
    
    plans = get_filtered_data("action_plans")
    if plans:
        for plan in plans:
            due_date = datetime.strptime(plan["due_date"], "%Y-%m-%d").date()
            days_left = (due_date - datetime.now().date()).days
            
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"**{plan['task_name']}**")
                    st.caption(f"📅 Due: {plan['due_date']} ({days_left} days left)")
                with col2:
                    st.progress(plan["progress_percent"] / 100)
                    st.caption(f"{plan['progress_percent']}%")
                with col3:
                    new_progress = st.number_input("Update %", 0, 100, plan["progress_percent"], key=f"p_{plan['id']}", label_visibility="collapsed")
                    if st.button(f"Update", key=f"u_{plan['id']}"):
                        new_status = "completed" if new_progress == 100 else "in progress" if new_progress > 0 else "not started"
                        supabase.table("action_plans").update({
                            "progress_percent": new_progress,
                            "status": new_status
                        }).eq("id", plan["id"]).execute()
                        st.success("Updated!")
                        st.rerun()
                st.markdown("---")
    else:
        st.info("No action plans found. Click 'Add New Action Item' to get started.")

# ============================================
# CONTRACTS
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
                color = "🟢"
                badge = '<span class="badge-active">Active</span>'
            elif days_left > 0:
                color = "🟡"
                badge = '<span class="badge-expiring">Expiring Soon</span>'
            else:
                color = "🔴"
                badge = '<span class="badge-expired">Expired</span>'
            
            st.markdown(f"""
            <div class='metric-card'>
                <div style='display:flex; justify-content:space-between; align-items:center;'>
                    <div>
                        <b style='font-size:16px;'>{color} {contract['contract_title']}</b><br>
                        <span style='color:#666;'>Vendor: {contract['vendor_name']}</span><br>
                        <span style='color:#666;'>End Date: {contract['end_date']} | {days_left} days remaining</span><br>
                        <span>Auto-renewal: {'Yes' if contract['auto_renewal'] else 'No'}</span>
                    </div>
                    <div>{badge}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No contracts found. Click 'Add New Contract' to get started.")

# ============================================
# POLICIES
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
                badge = '<span class="badge-active">Active</span>'
            elif days_left > 0:
                badge = '<span class="badge-expiring">Expiring Soon</span>'
            else:
                badge = '<span class="badge-expired">Expired</span>'
            
            st.markdown(f"""
            <div class='metric-card'>
                <div style='display:flex; justify-content:space-between; align-items:center;'>
                    <div>
                        <b style='font-size:16px;'>📜 {policy['policy_name']}</b><br>
                        <span style='color:#666;'>Expires: {policy['expiry_date']} ({days_left} days left)</span>
                    </div>
                    <div>{badge}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No policies found. Click 'Add New Policy' to get started.")

# ============================================
# ENHANCED USER MANAGEMENT (ADMIN ONLY)
# ============================================
elif choice == "👥 User Management" and st.session_state.user_role == "admin":
    st.subheader("User Management - Admin Panel")
    
    # Get all departments for dropdown
    depts = supabase.table("departments").select("id,name").execute().data
    dept_options = {d["name"]: d["id"] for d in depts}
    
    # Get all users
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
                
                # Get current user data
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
                    
                    # Password reset option
                    reset_password = st.checkbox("Reset Password")
                    new_password = None
                    if reset_password:
                        new_password = st.text_input("New Password", type="password")
                        confirm_new = st.text_input("Confirm New Password", type="password")
                    
                    if st.button("Save Changes", use_container_width=True):
                        # Update role and department
                        dept_id = dept_options.get(new_department) if new_department != "None" else None
                        if update_user_role(selected_username, new_role, dept_id):
                            st.success(f"✅ Role and department updated for {selected_username}")
                        else:
                            st.error("Failed to update role/department")
                        
                        # Reset password if requested
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
    
    # Display current users table
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
                "Completion Rate": f"{avg_progress:.0f}%"
            })
        else:
            performance_data.append({
                "Department": dept["name"],
                "Total Tasks": 0,
                "Completed": 0,
                "Completion Rate": "N/A"
            })
    
    if performance_data:
        df = pd.DataFrame(performance_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Tabs for detailed views
    tabs = st.tabs(["All Action Plans", "All Contracts", "All Policies"])
    
    with tabs[0]:
        all_plans = supabase.table("action_plans").select("*").execute().data
        if all_plans:
            df = pd.DataFrame(all_plans)
            df["department"] = df["department_id"].map(dept_names)
            st.dataframe(df[["task_name", "department", "status", "progress_percent", "due_date"]], use_container_width=True, hide_index=True)
        else:
            st.info("No action plans found")
    
    with tabs[1]:
        all_contracts = supabase.table("contracts").select("*").execute().data
        if all_contracts:
            df = pd.DataFrame(all_contracts)
            df["department"] = df["department_id"].map(dept_names)
            st.dataframe(df[["contract_title", "vendor_name", "department", "end_date", "status"]], use_container_width=True, hide_index=True)
        else:
            st.info("No contracts found")
    
    with tabs[2]:
        all_policies = supabase.table("policies").select("*").execute().data
        if all_policies:
            df = pd.DataFrame(all_policies)
            df["department"] = df["department_id"].map(dept_names).fillna("Global")
            st.dataframe(df[["policy_name", "department", "expiry_date"]], use_container_width=True, hide_index=True)
        else:
            st.info("No policies found")

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown(f"""
<div class='footer'>
    <p>© 2025 HELB - Higher Education Loans Board | Strategy Performance Management System</p>
    <p>Powered by Streamlit | Secure & Real-time</p>
</div>
""", unsafe_allow_html=True)
