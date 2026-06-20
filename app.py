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
from dateutil.relativedelta import relativedelta
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer 
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from sklearn.linear_model import LinearRegression
import numpy as np
import hashlib
import calendar

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
# COUNTDOWN TIMER CSS - PROFESSIONAL STYLING
# ============================================
COUNTDOWN_CSS = """
    /* Main Countdown Container */
    .countdown-wrapper {
        background: linear-gradient(135deg, #00843D 0%, #00529B 100%);
        border-radius: 16px;
        padding: 1.2rem 2rem;
        margin: 0.5rem 0 1.5rem 0;
        box-shadow: 0 8px 32px rgba(0, 132, 61, 0.25);
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Animated Background Glow */
    .countdown-wrapper::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle at 30% 50%, rgba(255, 184, 28, 0.08) 0%, transparent 60%),
                    radial-gradient(circle at 70% 50%, rgba(255, 255, 255, 0.05) 0%, transparent 40%);
        animation: countdownPulse 4s ease-in-out infinite;
    }
    
    @keyframes countdownPulse {
        0%, 100% { transform: scale(1) rotate(0deg); opacity: 0.5; }
        50% { transform: scale(1.05) rotate(2deg); opacity: 1; }
    }
    
    /* Top Section - Title and Status */
    .countdown-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        position: relative;
        z-index: 1;
        margin-bottom: 0.8rem;
        flex-wrap: wrap;
        gap: 0.5rem;
    }
    
    .countdown-title {
        color: #FFFFFF;
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: 0.3px;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .countdown-title span {
        color: #FFB81C;
        font-weight: 700;
    }
    
    .countdown-status {
        font-size: 0.7rem;
        font-weight: 600;
        padding: 0.2rem 0.8rem;
        border-radius: 20px;
        background: rgba(255, 255, 255, 0.15);
        color: #FFFFFF;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(4px);
    }
    
    .countdown-status.urgent {
        background: rgba(239, 68, 68, 0.3);
        border-color: rgba(239, 68, 68, 0.4);
        color: #FCA5A5;
    }
    
    .countdown-status.warning {
        background: rgba(245, 158, 11, 0.3);
        border-color: rgba(245, 158, 11, 0.4);
        color: #FCD34D;
    }
    
    .countdown-status.success {
        background: rgba(16, 185, 129, 0.3);
        border-color: rgba(16, 185, 129, 0.4);
        color: #6EE7B7;
    }
    
    /* Timer Grid */
    .countdown-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        position: relative;
        z-index: 1;
        max-width: 500px;
        margin: 0 auto 0.8rem auto;
    }
    
    .countdown-item {
        background: rgba(255, 255, 255, 0.12);
        border-radius: 12px;
        padding: 0.6rem 0.3rem;
        text-align: center;
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        transition: all 0.3s ease;
    }
    
    .countdown-item:hover {
        transform: translateY(-2px);
        background: rgba(255, 255, 255, 0.18);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    }
    
    .countdown-number {
        font-size: 2rem;
        font-weight: 700;
        color: #FFFFFF;
        line-height: 1.1;
        font-variant-numeric: tabular-nums;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .countdown-label {
        font-size: 0.5rem;
        text-transform: uppercase;
        color: #FFB81C;
        font-weight: 600;
        letter-spacing: 0.8px;
        margin-top: 0.1rem;
    }
    
    /* Progress Bar */
    .countdown-progress {
        position: relative;
        z-index: 1;
        max-width: 500px;
        margin: 0 auto;
    }
    
    .countdown-progress-bar {
        width: 100%;
        height: 6px;
        background: rgba(255, 255, 255, 0.15);
        border-radius: 4px;
        overflow: hidden;
        position: relative;
    }
    
    .countdown-progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #FFB81C, #FFB81C);
        border-radius: 4px;
        transition: width 1.5s ease;
        position: relative;
        box-shadow: 0 0 10px rgba(255, 184, 28, 0.3);
    }
    
    .countdown-progress-fill::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
        animation: shimmer 2s infinite;
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    .countdown-progress-text {
        display: flex;
        justify-content: space-between;
        font-size: 0.55rem;
        color: rgba(255, 255, 255, 0.7);
        margin-top: 0.3rem;
    }
    
    .countdown-progress-text span:last-child {
        color: #FFB81C;
        font-weight: 600;
    }
    
    /* Footer Details */
    .countdown-footer {
        display: flex;
        justify-content: center;
        gap: 1.5rem;
        margin-top: 0.6rem;
        position: relative;
        z-index: 1;
        flex-wrap: wrap;
        padding-top: 0.6rem;
        border-top: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    .countdown-detail-item {
        font-size: 0.6rem;
        color: rgba(255, 255, 255, 0.75);
        display: flex;
        align-items: center;
        gap: 0.3rem;
    }
    
    .countdown-detail-item strong {
        color: #FFB81C;
        font-weight: 700;
        font-size: 0.7rem;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .countdown-wrapper {
            padding: 0.8rem 1rem;
        }
        .countdown-grid {
            grid-template-columns: repeat(4, 1fr);
            gap: 0.4rem;
        }
        .countdown-number {
            font-size: 1.3rem;
        }
        .countdown-label {
            font-size: 0.4rem;
            letter-spacing: 0.5px;
        }
        .countdown-title {
            font-size: 0.7rem;
        }
        .countdown-status {
            font-size: 0.55rem;
            padding: 0.15rem 0.6rem;
        }
        .countdown-footer {
            gap: 0.8rem;
        }
        .countdown-detail-item {
            font-size: 0.5rem;
        }
        .countdown-detail-item strong {
            font-size: 0.6rem;
        }
        .countdown-header {
            flex-direction: column;
            align-items: flex-start;
        }
    }
    
    @media (max-width: 480px) {
        .countdown-grid {
            gap: 0.25rem;
        }
        .countdown-number {
            font-size: 1rem;
        }
        .countdown-item {
            padding: 0.4rem 0.2rem;
        }
        .countdown-label {
            font-size: 0.35rem;
        }
    }
"""
# ============================================
# FINANCIAL YEAR COUNTDOWN FUNCTIONS
# ============================================
def get_financial_year_countdown():
    """Calculate time remaining until June 30, 2027"""
    target_date = datetime(2027, 6, 30, 23, 59, 59)
    now = datetime.now()
    diff = target_date - now
    
    if diff.total_seconds() <= 0:
        return {
            'days': 0, 'hours': 0, 'minutes': 0, 'seconds': 0,
            'weeks': 0, 'months': 0, 'total_seconds': 0,
            'expired': True, 'percentage_elapsed': 100
        }
    
    total_seconds = diff.total_seconds()
    days = diff.days
    hours = diff.seconds // 3600
    minutes = (diff.seconds % 3600) // 60
    seconds = diff.seconds % 60
    weeks = days // 7
    months = days // 30
    
    fy_start = datetime(2026, 7, 1, 0, 0, 0)
    fy_total_days = (target_date - fy_start).days
    fy_elapsed_days = (now - fy_start).days
    percentage_elapsed = (fy_elapsed_days / fy_total_days) * 100 if fy_total_days > 0 else 0
    
    return {
        'days': days, 'hours': hours, 'minutes': minutes, 'seconds': seconds,
        'weeks': weeks, 'months': months, 'total_seconds': total_seconds,
        'expired': False, 'percentage_elapsed': min(percentage_elapsed, 100)
    }

def display_countdown_timer():
    """Display the financial year countdown timer with professional styling"""
    countdown = get_financial_year_countdown()
    
    if countdown['expired']:
        st.markdown("""
        <div class='countdown-wrapper'>
            <div class='countdown-header'>
                <div class='countdown-title'>📅 FINANCIAL YEAR 2026/2027</div>
                <span class='countdown-status expired'>⏰ COMPLETED</span>
            </div>
            <div style='text-align: center; padding: 0.5rem; position: relative; z-index: 1;'>
                <div style='color: #FFB81C; font-size: 1.1rem; font-weight: 700;'>
                    🎯 Time to review and plan for the next financial year
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Determine urgency
    if countdown['days'] <= 30:
        status_class = "urgent"
        status_icon = "🔴"
        status_text = "URGENT - Less than 30 days!"
    elif countdown['days'] <= 90:
        status_class = "warning"
        status_icon = "🟡"
        status_text = "WARNING - Less than 3 months!"
    else:
        status_class = "success"
        status_icon = "🟢"
        status_text = "On Track"
    
    # Format numbers
    days = str(countdown['days']).zfill(2)
    hours = str(countdown['hours']).zfill(2)
    minutes = str(countdown['minutes']).zfill(2)
    seconds = str(countdown['seconds']).zfill(2)
    percentage_elapsed = countdown['percentage_elapsed']
    
    st.markdown(f"""
    <div class='countdown-wrapper'>
        <!-- Header -->
        <div class='countdown-header'>
            <div class='countdown-title'>
                ⏰ TIME REMAINING: <span>JUNE 30, 2027</span>
            </div>
            <span class='countdown-status {status_class}'>{status_icon} {status_text}</span>
        </div>
        
        <!-- Timer Grid -->
        <div class='countdown-grid'>
            <div class='countdown-item'>
                <div class='countdown-number'>{days}</div>
                <div class='countdown-label'>Days</div>
            </div>
            <div class='countdown-item'>
                <div class='countdown-number'>{hours}</div>
                <div class='countdown-label'>Hours</div>
            </div>
            <div class='countdown-item'>
                <div class='countdown-number'>{minutes}</div>
                <div class='countdown-label'>Minutes</div>
            </div>
            <div class='countdown-item'>
                <div class='countdown-number'>{seconds}</div>
                <div class='countdown-label'>Seconds</div>
            </div>
        </div>
        
        <!-- Progress Bar -->
        <div class='countdown-progress'>
            <div class='countdown-progress-bar'>
                <div class='countdown-progress-fill' style='width: {percentage_elapsed:.1f}%;'></div>
            </div>
            <div class='countdown-progress-text'>
                <span>FY 2026/2027 Started</span>
                <span>{percentage_elapsed:.1f}% Elapsed</span>
                <span>Ending June 30, 2027</span>
            </div>
        </div>
        
        <!-- Footer Details -->
        <div class='countdown-footer'>
            <span class='countdown-detail-item'>📅 <strong>{countdown['weeks']}</strong> Weeks Remaining</span>
            <span class='countdown-detail-item'>📆 <strong>{countdown['months']}</strong> Months Remaining</span>
            <span class='countdown-detail-item'>⏱️ <strong>{int(countdown['total_seconds']):,}</strong> Seconds Remaining</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
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

# ============================================
# PASSWORD HASHING FUNCTION
# ============================================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ============================================
# LOAD HELB LOGO FOR FAVICON AND DISPLAY
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
# PAGE CONFIG
# ============================================
if LOGO_BASE64:
    favicon_html = f'<link rel="icon" href="data:image/png;base64,{LOGO_BASE64}" type="image/png">'
else:
    favicon_html = ''

st.set_page_config(
    page_title="HELB Strategy Performance System",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Mobile responsive CSS
mobile_css = """
<style>
    @media (max-width: 768px) {
        .stApp {
            padding: 0.5rem;
        }
        .stColumns {
            flex-direction: column;
        }
        .kpi-card {
            min-height: 80px !important;
            padding: 0.5rem !important;
        }
        .kpi-card .kpi-value {
            font-size: 1rem !important;
        }
        .kpi-card .kpi-label {
            font-size: 0.55rem !important;
        }
        .stTabs [data-baseweb="tab-list"] {
            flex-wrap: wrap;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 0.5rem 1rem !important;
            font-size: 0.8rem !important;
        }
        .dashboard-header h1 {
            font-size: 1rem !important;
        }
        .dashboard-header p {
            font-size: 0.6rem !important;
        }
        .sidebar-user-info strong {
            font-size: 0.75rem !important;
        }
        .stExpander {
            margin-bottom: 0.5rem;
        }
    }
    @media (max-width: 768px) {
        button, .stButton > button {
            padding: 0.5rem 1rem !important;
            min-height: 44px;
        }
        input, select, textarea {
            font-size: 16px !important;
        }
    }
    @media (max-width: 768px) {
        [data-testid="stSidebar"] {
            width: 80% !important;
        }
    }
    .calendar-day {
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 0.5rem;
        min-height: 100px;
        background-color: white;
    }
    .calendar-day-header {
        font-weight: bold;
        text-align: center;
        padding: 0.5rem;
        background-color: #f3f4f6;
        border-radius: 6px;
    }
    .calendar-event {
        background-color: #00843D;
        color: white;
        padding: 0.2rem 0.4rem;
        border-radius: 4px;
        font-size: 0.7rem;
        margin-bottom: 0.2rem;
        cursor: pointer;
    }
    .calendar-event:hover {
        background-color: #00529B;
    }
</style>
"""

st.markdown(f'<head>{favicon_html}</head>', unsafe_allow_html=True)
st.markdown(mobile_css, unsafe_allow_html=True)

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

POLICY_DURATIONS = ["2 years", "3 years", "4 years", "5 years"]

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

def get_months_for_quarter_num(quarter):
    """Get month numbers for a given quarter"""
    if quarter == "Q1 (Jul-Sep)":
        return [7, 8, 9]
    elif quarter == "Q2 (Oct-Dec)":
        return [10, 11, 12]
    elif quarter == "Q3 (Jan-Mar)":
        return [1, 2, 3]
    elif quarter == "Q4 (Apr-Jun)":
        return [4, 5, 6]
    return []

# ============================================
# SESSION STATE FOR FILTERS & NAVIGATION
# ============================================
if "filter_financial_year" not in st.session_state:
    st.session_state.filter_financial_year = "All"
if "filter_quarter" not in st.session_state:
    st.session_state.filter_quarter = "All"
if "filter_month" not in st.session_state:
    st.session_state.filter_month = "All"
if "active_menu" not in st.session_state:
    st.session_state.active_menu = "📊 Dashboard"
if "active_work_plan_tab" not in st.session_state:
    st.session_state.active_work_plan_tab = 0
if "active_contracts_tab" not in st.session_state:
    st.session_state.active_contracts_tab = 0
if "active_policies_tab" not in st.session_state:
    st.session_state.active_policies_tab = 0
if "calendar_selected_quarter" not in st.session_state:
    st.session_state.calendar_selected_quarter = "All"
if "calendar_selected_year" not in st.session_state:
    st.session_state.calendar_selected_year = datetime.now().year

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
# PREDICTIVE ANALYTICS FUNCTIONS
# ============================================
def predict_completion_trend(df):
    """Predict future completion rates using linear regression"""
    if len(df) < 3:
        return None, None, None
    
    df['date'] = pd.to_datetime(df['created_at'])
    df = df.sort_values('date')
    df['days_since_start'] = (df['date'] - df['date'].min()).dt.days
    
    X = df['days_since_start'].values.reshape(-1, 1)
    y = df['progress_percent'].values
    
    model = LinearRegression()
    model.fit(X, y)
    
    max_days = df['days_since_start'].max()
    future_days = [max_days + 30, max_days + 60, max_days + 90]
    future_predictions = model.predict(np.array(future_days).reshape(-1, 1))
    
    r2 = model.score(X, y)
    
    return future_predictions, future_days, r2

def calculate_risk_score(progress, days_left, total_days):
    """Calculate risk score for an activity"""
    if days_left <= 0:
        return 100 if progress < 100 else 0
    
    expected_progress = max(0, min(100, (1 - (days_left / total_days)) * 100)) if total_days > 0 else 0
    progress_gap = expected_progress - progress
    
    if progress_gap > 30:
        return 90
    elif progress_gap > 15:
        return 60
    elif progress_gap > 0:
        return 30
    else:
        return 10

# ============================================
# PILLAR PERFORMANCE SUMMARY FUNCTION
# ============================================
def generate_pillar_performance_summary(activities):
    """Generate a high-level summary of pillar-wise performance"""
    
    pillar_data = {}
    
    for activity in activities:
        pillar = activity.get('strategic_pillar', 'Uncategorized')
        status = activity.get('status', 'Pending')
        progress = activity.get('progress_percent', 0)
        
        if pillar not in pillar_data:
            pillar_data[pillar] = {
                'total': 0,
                'completed': 0,
                'in_progress': 0,
                'pending': 0,
                'total_progress': 0,
                'activities': []
            }
        
        pillar_data[pillar]['total'] += 1
        pillar_data[pillar]['total_progress'] += progress
        pillar_data[pillar]['activities'].append(activity)
        
        if status == 'Done':
            pillar_data[pillar]['completed'] += 1
        elif status == 'In Progress':
            pillar_data[pillar]['in_progress'] += 1
        else:
            pillar_data[pillar]['pending'] += 1
    
    # Calculate averages and create summary
    summary = []
    for pillar, data in pillar_data.items():
        avg_progress = data['total_progress'] / data['total'] if data['total'] > 0 else 0
        completion_rate = (data['completed'] / data['total'] * 100) if data['total'] > 0 else 0
        
        summary.append({
            'Pillar': pillar,
            'Total': data['total'],
            'Completed': data['completed'],
            'In Progress': data['in_progress'],
            'Pending': data['pending'],
            'Avg Progress': round(avg_progress, 1),
            'Completion Rate': round(completion_rate, 1)
        })
    
    return pd.DataFrame(summary)

# ============================================
# ENHANCED CALENDAR VIEW WITH CLICK FUNCTIONALITY
# ============================================
def generate_calendar_html(activities, year, month, quarter_filter="All"):
    """Generate HTML for month calendar view with quarter filtering, start/end markers, and clickable activities"""
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    
    # Filter activities by quarter if specified
    filtered_activities = activities
    if quarter_filter != "All":
        quarter_months = get_months_for_quarter_num(quarter_filter)
        filtered_activities = []
        for activity in activities:
            if activity.get('due_date'):
                due_date = pd.to_datetime(activity['due_date']).date()
                if due_date.year == year and due_date.month in quarter_months:
                    filtered_activities.append(activity)
    
    # Group activities by date with start/end markers
    activities_by_date = {}
    start_dates = {}
    end_dates = {}
    
    # Create serializable activity data for JSON
    serializable_activities_by_date = {}
    
    for activity in filtered_activities:
        if activity.get('due_date'):
            due_date = pd.to_datetime(activity['due_date']).date()
            if due_date.year == year and due_date.month == month:
                date_key = str(due_date.day)
                if date_key not in activities_by_date:
                    activities_by_date[date_key] = []
                    serializable_activities_by_date[date_key] = []
                
                # Create serializable version of activity with ALL fields
                serializable_act = {
                    'planned_activity': str(activity.get('planned_activity', '')),
                    'status': str(activity.get('status', 'Pending')),
                    'department_name': str(activity.get('department_name', 'Unknown')),
                    'progress_percent': int(activity.get('progress_percent', 0)),
                    'due_date': str(activity.get('due_date', '')),
                    'start_date': str(activity.get('start_date', '')),
                    'end_date': str(activity.get('end_date', '')),
                    'strategic_pillar': str(activity.get('strategic_pillar', '')),
                    'comment': str(activity.get('comment', '')) if activity.get('comment') else '',
                    'id': int(activity.get('id', 0)) if activity.get('id') else 0,
                    'key_result_area': str(activity.get('key_result_area', '')),
                    'performance_indicator': str(activity.get('performance_indicator', '')),
                    'annual_target': str(activity.get('annual_target', '')),
                    'actual_achievement': float(activity.get('actual_achievement', 0)),
                    'budget_allocation': float(activity.get('budget_allocation', 0)) if activity.get('budget_allocation') else 0,
                    'activity_category': str(activity.get('activity_category', ''))
                }
                
                activities_by_date[date_key].append(activity)
                serializable_activities_by_date[date_key].append(serializable_act)
        
        # Track start and end dates
        if activity.get('start_date'):
            start_date = pd.to_datetime(activity['start_date']).date()
            if start_date.year == year and start_date.month == month:
                start_dates[start_date.day] = True
        if activity.get('end_date'):
            end_date = pd.to_datetime(activity['end_date']).date()
            if end_date.year == year and end_date.month == month:
                end_dates[end_date.day] = True
    
    # Determine theme for styling
    is_dark = st.session_state.theme == "dark"
    
    # Build HTML with JavaScript for click functionality
    html = f"""
    <style>
        .calendar-clickable {{
            cursor: pointer !important;
            transition: all 0.2s ease !important;
        }}
        .calendar-clickable:hover {{
            opacity: 0.85 !important;
            transform: scale(0.97) !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15) !important;
        }}
        .calendar-event-item {{
            cursor: pointer !important;
            transition: all 0.2s ease !important;
        }}
        .calendar-event-item:hover {{
            opacity: 0.8 !important;
            transform: scale(0.95) !important;
        }}
        /* Modal styles */
        .calendar-modal {{
            display: none;
            position: fixed;
            z-index: 99999;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            overflow: auto;
            background-color: rgba(0,0,0,0.6);
            backdrop-filter: blur(4px);
            animation: fadeIn 0.3s ease;
        }}
        .calendar-modal-content {{
            background-color: {'#ffffff' if not is_dark else '#1e293b'};
            margin: 5% auto;
            padding: 25px;
            border-radius: 16px;
            width: 90%;
            max-width: 750px;
            max-height: 80vh;
            overflow-y: auto;
            box-shadow: 0 20px 60px rgba(0,0,0,0.4);
            animation: slideDown 0.3s ease;
            border: 1px solid {'#e5e7eb' if not is_dark else '#334155'};
        }}
        .calendar-modal-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #00843D;
        }}
        .calendar-modal-close {{
            color: {'#6b7280' if not is_dark else '#94a3b8'};
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
            transition: 0.3s;
            line-height: 1;
            padding: 0 8px;
        }}
        .calendar-modal-close:hover {{
            color: {'#000000' if not is_dark else '#ffffff'};
            transform: rotate(90deg);
        }}
        .calendar-modal-title {{
            color: {'#000000' if not is_dark else '#ffffff'};
            font-size: 1.3rem;
            font-weight: 700;
            margin: 0;
        }}
        .calendar-modal-title span {{
            color: #00843D;
        }}
        .calendar-modal-subtitle {{
            color: {'#6b7280' if not is_dark else '#94a3b8'};
            font-size: 0.85rem;
            margin-top: 0.25rem;
        }}
        .calendar-modal-activity {{
            padding: 0.75rem 1rem;
            margin-bottom: 0.5rem;
            border-radius: 8px;
            border-left: 4px solid #00843D;
            background-color: {'#f9fafb' if not is_dark else '#0f172a'};
            transition: all 0.2s ease;
        }}
        .calendar-modal-activity:hover {{
            background-color: {'#f3f4f6' if not is_dark else '#1e293b'};
            transform: translateX(4px);
        }}
        .calendar-modal-activity-title {{
            font-weight: 600;
            color: {'#000000' if not is_dark else '#ffffff'};
            font-size: 0.95rem;
        }}
        .calendar-modal-activity-detail {{
            font-size: 0.8rem;
            color: {'#6b7280' if not is_dark else '#94a3b8'};
            margin-top: 0.25rem;
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }}
        .calendar-modal-activity-detail span {{
            background: {'#e5e7eb' if not is_dark else '#334155'};
            padding: 0.1rem 0.5rem;
            border-radius: 12px;
            font-size: 0.7rem;
        }}
        .calendar-modal-activity-status {{
            display: inline-block;
            padding: 0.1rem 0.5rem;
            border-radius: 12px;
            font-size: 0.7rem;
            font-weight: 600;
        }}
        .status-done {{ background: #10b981; color: white; }}
        .status-progress {{ background: #f59e0b; color: white; }}
        .status-pending {{ background: #ef4444; color: white; }}
        .no-activities {{
            color: {'#6b7280' if not is_dark else '#94a3b8'};
            text-align: center;
            padding: 2rem;
            font-size: 1rem;
        }}
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        @keyframes slideDown {{
            from {{ transform: translateY(-50px); opacity: 0; }}
            to {{ transform: translateY(0); opacity: 1; }}
        }}
        .calendar-legend {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 0.5rem;
            padding: 0.5rem;
            border-top: 1px solid {'#e5e7eb' if not is_dark else '#475569'};
        }}
        .calendar-legend-item {{
            font-size: 0.65rem;
            color: {'#000000' if not is_dark else '#FFFFFF'};
            display: flex;
            align-items: center;
            gap: 0.3rem;
        }}
        .calendar-legend-color {{
            display: inline-block;
            width: 14px;
            height: 14px;
            border-radius: 3px;
            border: 1px solid #00843D;
            vertical-align: middle;
        }}
        /* Progress bar in modal */
        .modal-progress-bar {{
            width: 100%;
            height: 4px;
            background: #E5E7EB;
            border-radius: 2px;
            margin-top: 6px;
            overflow: hidden;
        }}
        .modal-progress-fill {{
            height: 100%;
            border-radius: 2px;
            transition: width 0.5s;
        }}
    </style>
    
    <div style="background: {'#ffffff' if not is_dark else '#1e293b'}; padding: 1rem; border-radius: 12px; border: 1px solid {'#e5e7eb' if not is_dark else '#334155'};">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; padding: 0 0.5rem;">
            <h4 style="margin: 0; color: {'#000000' if not is_dark else '#FFFFFF'};">📅 {month_name} {year}</h4>
            <span style="font-size: 0.8rem; color: {'#6b7280' if not is_dark else '#94a3b8'};">
                📋 {len(filtered_activities)} activities
            </span>
        </div>
        
        <!-- Modal -->
        <div id="calendarModal" class="calendar-modal" onclick="if(event.target===this) closeModal()">
            <div class="calendar-modal-content">
                <div class="calendar-modal-header">
                    <div>
                        <div class="calendar-modal-title">📅 Activities for <span id="modalDate"></span></div>
                        <div class="calendar-modal-subtitle" id="modalSubtitle"></div>
                    </div>
                    <span class="calendar-modal-close" onclick="closeModal()">&times;</span>
                </div>
                <div id="modalActivities"></div>
            </div>
        </div>
        
        <table style="width:100%; border-collapse: collapse; background: {'#ffffff' if not is_dark else '#1e293b'};">
            <tr>
    """
    
    for day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']:
        html += f'<th style="padding: 8px; text-align: center; background-color: {"#f3f4f6" if not is_dark else "#334155"}; border: 1px solid {"#e5e7eb" if not is_dark else "#475569"}; color: {"#000000" if not is_dark else "#FFFFFF"}; font-size: 0.8rem;">{day}</th>'
    html += '</tr>'
    
    for week in cal:
        html += '<tr>'
        for day in week:
            if day == 0:
                html += f'<td style="padding: 8px; border: 1px solid {"#e5e7eb" if not is_dark else "#475569"}; vertical-align: top; height: 85px; background-color: {"#f9fafb" if not is_dark else "#0f172a"};"></td>'
            else:
                date_key = str(day)
                day_activities = activities_by_date.get(date_key, [])
                is_start = day in start_dates
                is_end = day in end_dates
                has_activities = len(day_activities) > 0
                
                # Determine background color
                if is_start and is_end:
                    bg_color = '#d1fae5' if not is_dark else '#064e3b'
                    border_style = "border: 2px solid #00843D; border-radius: 8px;"
                elif is_start:
                    bg_color = '#d1fae5' if not is_dark else '#064e3b'
                    border_style = "border-left: 3px solid #00843D; border-top: 2px solid #00843D; border-bottom: 2px solid #00843D; border-radius: 8px 0 0 8px;"
                elif is_end:
                    bg_color = '#d1fae5' if not is_dark else '#064e3b'
                    border_style = "border-right: 3px solid #00843D; border-top: 2px solid #00843D; border-bottom: 2px solid #00843D; border-radius: 0 8px 8px 0;"
                elif has_activities:
                    bg_color = '#fef3c7' if not is_dark else '#1e293b'
                    border_style = ""
                else:
                    bg_color = 'white' if not is_dark else '#0f172a'
                    border_style = ""
                
                # Add clickable class if there are activities
                clickable_class = 'calendar-clickable' if has_activities else ''
                onclick_attr = f'onclick="openModal({day}, {year}, {month})"' if has_activities else ''
                
                html += f'<td class="{clickable_class}" {onclick_attr} style="padding: 8px; border: 1px solid {"#e5e7eb" if not is_dark else "#475569"}; vertical-align: top; height: 85px; background-color: {bg_color}; {border_style}">'
                html += f'<div style="display: flex; justify-content: space-between; align-items: center;">'
                html += f'<strong style="color: {"#000000" if not is_dark else "#FFFFFF"};">{day}</strong>'
                
                if is_start:
                    html += f'<span style="font-size: 0.45rem; background: #00843D; color: white; padding: 1px 4px; border-radius: 4px;">▶ Start</span>'
                elif is_end:
                    html += f'<span style="font-size: 0.45rem; background: #00843D; color: white; padding: 1px 4px; border-radius: 4px;">◼ End</span>'
                elif has_activities:
                    html += f'<span style="font-size: 0.45rem; color: {"#6b7280" if not is_dark else "#94a3b8"};">{len(day_activities)}</span>'
                
                html += '</div>'
                
                # Show activities (max 3 in calendar view)
                for act in day_activities[:3]:
                    status_icon = "✅" if act.get('status') == 'Done' else "🟡" if act.get('status') == 'In Progress' else "🔴"
                    html += f'<div style="font-size: 0.6rem; margin-top: 3px; padding: 2px 6px; background-color: #00843D; color: white; border-radius: 4px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; cursor: pointer;" onclick="event.stopPropagation(); openModal({day}, {year}, {month})">'
                    html += f'{status_icon} {str(act["planned_activity"])[:20]}...'
                    html += '</div>'
                
                if len(day_activities) > 3:
                    html += f'<div style="font-size: 0.5rem; margin-top: 2px; color: {"#6b7280" if not is_dark else "#94a3b8"}; text-align: center; cursor: pointer;" onclick="event.stopPropagation(); openModal({day}, {year}, {month})">+{len(day_activities)-3} more</div>'
                
                html += '</td>'
        html += '</tr>'
    html += '</table>'
    
    # Legend
    html += f'''
    <div class="calendar-legend">
        <span class="calendar-legend-item">
            <span class="calendar-legend-color" style="background: #d1fae5; border-color: #00843D;"></span>
            Activity Range
        </span>
        <span class="calendar-legend-item">
            <span class="calendar-legend-color" style="background: #fef3c7; border-color: #f59e0b;"></span>
            Has Activity
        </span>
        <span class="calendar-legend-item">
            <span style="color: #00843D; font-weight: bold;">▶</span> Start Date
        </span>
        <span class="calendar-legend-item">
            <span style="color: #00843D; font-weight: bold;">◼</span> End Date
        </span>
        <span class="calendar-legend-item">
            🔴 Pending
        </span>
        <span class="calendar-legend-item">
            🟡 In Progress
        </span>
        <span class="calendar-legend-item">
            ✅ Done
        </span>
        <span class="calendar-legend-item">
            👆 Click date for details
        </span>
    </div>
    </div>
    
    <script>
        // Store ALL activities data for the modal - using serializable data
        var activitiesData = {json.dumps(serializable_activities_by_date)};
        var currentMonth = {month};
        var currentYear = {year};
        
        function openModal(day, year, month) {{
            var modal = document.getElementById("calendarModal");
            var modalActivities = document.getElementById("modalActivities");
            var modalSubtitle = document.getElementById("modalSubtitle");
            
            var dateObj = new Date(year, month - 1, day);
            var dateStr = dateObj.toLocaleDateString('en-US', {{ weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }});
            
            document.getElementById("modalDate").textContent = dateStr;
            
            // Get ALL activities for this date
            var dayKey = day.toString();
            var activities = activitiesData[dayKey] || [];
            
            if (activities.length === 0) {{
                modalActivities.innerHTML = '<div class="no-activities">No activities for this date</div>';
                modalSubtitle.textContent = 'No activities scheduled';
            }} else {{
                modalSubtitle.textContent = activities.length + ' activity(ies) scheduled';
                var html = '';
                // Show ALL activities
                activities.forEach(function(act, index) {{
                    var statusClass = act.status === 'Done' ? 'status-done' : (act.status === 'In Progress' ? 'status-progress' : 'status-pending');
                    var statusIcon = act.status === 'Done' ? '✅' : (act.status === 'In Progress' ? '🟡' : '🔴');
                    var progressColor = act.progress_percent >= 100 ? '#10B981' : (act.progress_percent > 0 ? '#F59E0B' : '#EF4444');
                    
                    html += '<div class="calendar-modal-activity" style="border-left-color: ' + (act.status === 'Done' ? '#10B981' : act.status === 'In Progress' ? '#F59E0B' : '#EF4444') + ';">';
                    html += '<div class="calendar-modal-activity-title">' + statusIcon + ' ' + act.planned_activity + '</div>';
                    html += '<div class="calendar-modal-activity-detail">';
                    html += '<span>🏛️ ' + (act.department_name || 'Unknown') + '</span>';
                    html += '<span>📊 ' + (act.progress_percent || 0) + '%</span>';
                    html += '<span>📅 Due: ' + act.due_date + '</span>';
                    html += '<span class="calendar-modal-activity-status ' + statusClass + '">' + act.status + '</span>';
                    if (act.strategic_pillar) {{
                        html += '<span>📌 ' + act.strategic_pillar.substring(0, 30) + '...</span>';
                    }}
                    if (act.key_result_area) {{
                        html += '<span>🎯 ' + act.key_result_area.substring(0, 25) + '...</span>';
                    }}
                    if (act.annual_target) {{
                        html += '<span>🎯 Target: ' + act.annual_target + '</span>';
                    }}
                    if (act.actual_achievement) {{
                        html += '<span>📈 Actual: ' + act.actual_achievement + '</span>';
                    }}
                    if (act.budget_allocation && act.budget_allocation > 0) {{
                        html += '<span>💰 KES ' + act.budget_allocation.toLocaleString() + '</span>';
                    }}
                    if (act.comment) {{
                        html += '<span>💬 ' + act.comment.substring(0, 50) + '...</span>';
                    }}
                    html += '</div>';
                    // Progress bar
                    html += '<div class="modal-progress-bar">';
                    html += '<div class="modal-progress-fill" style="width: ' + Math.min(act.progress_percent, 100) + '%; background: ' + progressColor + ';"></div>';
                    html += '</div>';
                    html += '</div>';
                }});
                modalActivities.innerHTML = html;
            }}
            
            modal.style.display = "block";
            document.body.style.overflow = "hidden";
        }}
        
        function closeModal() {{
            document.getElementById("calendarModal").style.display = "none";
            document.body.style.overflow = "auto";
        }}
        
        // Close modal on Escape key
        document.addEventListener('keydown', function(event) {{
            if (event.key === "Escape") {{
                closeModal();
            }}
        }});
    </script>
    '''
    
    return html

# ============================================
# PASSWORD MANAGEMENT FUNCTIONS
# ============================================
def change_user_password(username, old_password, new_password):
    try:
        result = supabase.table("users").select("*").eq("username", username).execute()
        if not result.data:
            return False, "User not found"
        
        user = result.data[0]
        if old_password != user["password_hash"] and hash_password(old_password) != user["password_hash"]:
            return False, "Current password is incorrect"
        
        supabase.table("users").update({
            "password_hash": hash_password(new_password),
            "updated_at": datetime.now().isoformat()
        }).eq("username", username).execute()
        
        add_audit_log("PASSWORD_CHANGE", "user", None, f"User {username} changed password")
        return True, "Password changed successfully!"
    except Exception as e:
        return False, str(e)

def admin_reset_password(username, new_password="password123"):
    try:
        supabase.table("users").update({
            "password_hash": hash_password(new_password),
            "updated_at": datetime.now().isoformat()
        }).eq("username", username).execute()
        
        add_audit_log("PASSWORD_RESET", "user", None, f"Admin reset password for {username}")
        return True, f"Password reset to '{new_password}' for {username}"
    except Exception as e:
        return False, str(e)

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
            "user_id": st.session_state.user_id if hasattr(st.session_state, 'user_id') else None,
            "username": st.session_state.user_name if hasattr(st.session_state, 'user_name') else "system",
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
        
        dir_result = supabase.table("directorates").select("id, name, director_name").execute()
        directorates = {d["id"]: d for d in dir_result.data}
        
        for dept in depts:
            if dept.get("directorate_id") and dept["directorate_id"] in directorates:
                dept["directorate_name"] = directorates[dept["directorate_id"]]["name"]
                dept["director_name"] = directorates[dept["directorate_id"]]["director_name"]
            else:
                dept["directorate_name"] = None
                dept["director_name"] = None
        return depts
    except Exception as e:
        print(f"Error in get_cached_departments: {e}")
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
@st.cache_data(ttl=120)
def get_cached_work_plans(user_role, user_dept):
    try:
        if user_role in ["admin", "management"]:
            result = supabase.table("work_plan").select("*").order("created_at", desc=True).execute()
        else:
            result = supabase.table("work_plan").select("*").eq("department_id", user_dept).order("created_at", desc=True).execute()
        return result.data
    except:
        return []

@st.cache_data(ttl=120)
def get_cached_contracts(user_role, user_dept):
    try:
        if user_role in ["admin", "management"]:
            result = supabase.table("contracts").select("*").order("created_at", desc=True).execute()
        else:
            result = supabase.table("contracts").select("*").eq("department_id", user_dept).order("created_at", desc=True).execute()
        
        # Handle missing department_name - don't try to update the table, just handle in code
        for contract in result.data:
            if 'department_name' not in contract or not contract['department_name']:
                if contract.get('department_id'):
                    dept_name = get_department_name(contract['department_id'])
                    contract['department_name'] = dept_name if dept_name else 'Unassigned'
                else:
                    contract['department_name'] = 'Unassigned'
        
        return result.data
    except:
        return []

@st.cache_data(ttl=120)
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

def update_work_plan_progress(plan_id, actual_achievement, progress_percent, status, comment=None):
    try:
        progress_int = int(progress_percent) if progress_percent else 0
        
        update_data = {
            "actual_achievement": float(actual_achievement) if actual_achievement else 0,
            "progress_percent": progress_int,
            "status": status,
            "updated_at": datetime.now().isoformat()
        }
        
        if comment:
            update_data["comment"] = comment
            
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
# CONTRACT FUNCTIONS - UPDATED FOR DEPARTMENT ACCESS
# ============================================
def get_contract_years(contract_id):
    try:
        result = supabase.table("contract_years").select("*").eq("contract_id", contract_id).order("year_number").execute()
        return result.data
    except:
        return []

def add_multi_year_contract(contract_data, years_data):
    try:
        total_value = sum(y.get('annual_value', 0) for y in years_data)
        contract_data['contract_value'] = total_value
        contract_data['total_contract_value'] = total_value
        
        result = supabase.table("contracts").insert(contract_data).execute()
        if not result.data:
            return False, "Failed to create contract"
        
        contract_id = result.data[0]['id']
        
        for year_data in years_data:
            year_data['contract_id'] = contract_id
            if year_data.get('annual_value', 0) > 0:
                year_data['utilization_rate'] = (year_data.get('amount_spent_to_date', 0) / year_data['annual_value'] * 100)
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
        
        supabase.table("contract_years").update({
            "amount_spent_to_date": amount_spent,
            "updated_at": datetime.now().isoformat()
        }).eq("id", year_id).execute()
        
        all_years = get_contract_years(year['contract_id'])
        total_spent = sum(y.get('amount_spent_to_date', 0) for y in all_years)
        total_value = sum(y.get('annual_value', 0) for y in all_years)
        utilization = (total_spent / total_value * 100) if total_value > 0 else 0
        
        supabase.table("contracts").update({
            "amount_spent_to_date": total_spent,
            "utilization_rate": utilization,
            "budget_alert": utilization >= 80,
            "updated_at": datetime.now().isoformat()
        }).eq("id", year['contract_id']).execute()
        
        st.cache_data.clear()
        return True
    except Exception as e:
        return False

def update_contract_year_status(year_id, status, notes=None):
    try:
        update_data = {
            "status": status,
            "updated_at": datetime.now().isoformat()
        }
        if notes:
            update_data["notes"] = notes
        
        supabase.table("contract_years").update(update_data).eq("id", year_id).execute()
        st.cache_data.clear()
        return True
    except Exception as e:
        return False

def add_enhanced_contract(data):
    try:
        # Ensure department_name is set
        if 'department_name' not in data or not data['department_name']:
            if data.get('department_id'):
                dept_name = get_department_name(data['department_id'])
                data['department_name'] = dept_name if dept_name else 'Unassigned'
            else:
                data['department_name'] = 'Unassigned'
        
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

def update_contract_admin_full(contract_id, data):
    """Full contract update for admin - all fields editable"""
    try:
        # Add updated_at timestamp
        data['updated_at'] = datetime.now().isoformat()
        
        # Ensure department_name is set - don't try to update the table, just handle in code
        if 'department_name' not in data or not data['department_name']:
            if data.get('department_id'):
                dept_name = get_department_name(data['department_id'])
                data['department_name'] = dept_name if dept_name else 'Unassigned'
            else:
                data['department_name'] = 'Unassigned'
        
        # Calculate derived fields
        end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").date()
        days_left = (end_date - datetime.now().date()).days
        
        if days_left < 0:
            data["status"] = "expired"
        elif days_left <= 30:
            data["status"] = "expiring_soon"
        else:
            data["status"] = "active"
        
        data["days_remaining"] = days_left
        
        # Calculate utilization
        contract_value = float(data.get("contract_value", 0))
        amount_spent = float(data.get("amount_spent_to_date", 0))
        utilization_rate = (amount_spent / contract_value * 100) if contract_value > 0 else 0
        data["utilization_rate"] = utilization_rate
        data["budget_alert"] = utilization_rate >= 80
        
        # Update the contract
        result = supabase.table("contracts").update(data).eq("id", contract_id).execute()
        
        # Check if update was successful
        if result.data:
            st.cache_data.clear()
            add_audit_log("FULL_UPDATE", "contract", contract_id, f"Admin full updated contract: {data.get('contract_title', '')}")
            return True
        else:
            return False
    except Exception as e:
        print(f"Error in update_contract_admin_full: {e}")
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
# POLICY FUNCTIONS
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
        result = supabase.table("policy_acknowledgments").select("*").eq("policy_id", policy_id).execute()
        return result.data
    except:
        return []

def acknowledge_policy(policy_id, department_id):
    try:
        result = supabase.table("policy_acknowledgments").select("*").eq("policy_id", policy_id).eq("department_id", department_id).execute()
        
        if result.data:
            supabase.table("policy_acknowledgments").update({
                "acknowledged": True,
                "acknowledged_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }).eq("id", result.data[0]["id"]).execute()
        else:
            supabase.table("policy_acknowledgments").insert({
                "policy_id": policy_id,
                "department_id": department_id,
                "acknowledged": True,
                "acknowledged_at": datetime.now().isoformat()
            }).execute()
        
        add_audit_log("ACKNOWLEDGE", "policy", policy_id, f"Policy acknowledged by department {department_id}")
        return True
    except Exception as e:
        return False

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
            "password_hash": hash_password(new_password)
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
            "password_hash": hash_password(password),
            "role": role,
            "department_id": department_id if department_id != "None" else None
        }).execute()
        st.cache_data.clear()
        add_audit_log("CREATE", "user", None, f"Created user: {username}")
        return True, "User created successfully"
    except Exception as e:
        return False, str(e)

# ============================================
# PDF REPORT GENERATION FUNCTIONS
# ============================================
def generate_work_plan_pdf_report(df, title="HELB Work Plan Report"):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
    styles = getSampleStyleSheet()
    elements = []
    
    try:
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor(HELB_GREEN))
    except:
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=16, textColor=colors.black)
    
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    
    total = len(df)
    completed = len(df[df['calculated_progress'] >= 100]) if 'calculated_progress' in df.columns else 0
    in_progress = len(df[(df['calculated_progress'] > 0) & (df['calculated_progress'] < 100)]) if 'calculated_progress' in df.columns else 0
    not_started = len(df[df['calculated_progress'] == 0]) if 'calculated_progress' in df.columns else 0
    
    summary_data = [
        ["Metric", "Value"],
        ["Total Activities", str(total)],
        ["Completed", str(completed)],
        ["In Progress", str(in_progress)],
        ["Not Started", str(not_started)]
    ]
    summary_table = Table(summary_data, colWidths=[2*inch, 2*inch])
    
    try:
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.HexColor(HELB_GREEN)),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (1, 0), 12),
            ('BACKGROUND', (0, 1), (1, -1), colors.beige),
            ('GRID', (0, 0), (1, -1), 1, colors.black)
        ]))
    except:
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (1, 0), 12),
            ('BACKGROUND', (0, 1), (1, -1), colors.beige),
            ('GRID', (0, 0), (1, -1), 1, colors.black)
        ]))
    
    elements.append(summary_table)
    elements.append(Spacer(1, 0.3*inch))
    
    display_cols = ['planned_activity', 'department_name', 'status', 'progress_percent', 'due_date']
    available_cols = [col for col in display_cols if col in df.columns]
    display_df = df[available_cols].head(50)
    table_data = [display_df.columns.tolist()] + display_df.fillna('').values.tolist()
    
    work_table = Table(table_data, repeatRows=1)
    try:
        work_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(HELB_GREEN)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]))
    except:
        work_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]))
    
    elements.append(work_table)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

def generate_contracts_pdf_report(df, title="HELB Contracts Report"):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
    styles = getSampleStyleSheet()
    elements = []
    
    try:
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor(HELB_GREEN))
    except:
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=16, textColor=colors.black)
    
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    
    total_value = df['contract_value'].sum() if 'contract_value' in df.columns else 0
    total_spent = df['amount_spent_to_date'].sum() if 'amount_spent_to_date' in df.columns else 0
    active = len(df[df['status'] == 'active']) if 'status' in df.columns else 0
    
    summary_data = [
        ["Metric", "Value"],
        ["Total Contract Value", f"KES {total_value:,.0f}"],
        ["Total Spent", f"KES {total_spent:,.0f}"],
        ["Active Contracts", str(active)],
        ["Total Contracts", str(len(df))]
    ]
    summary_table = Table(summary_data, colWidths=[2*inch, 2*inch])
    
    try:
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.HexColor(HELB_GREEN)),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (1, -1), 1, colors.black)
        ]))
    except:
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (1, -1), 1, colors.black)
        ]))
    
    elements.append(summary_table)
    elements.append(Spacer(1, 0.3*inch))
    
    display_cols = ['contract_title', 'vendor_name', 'contract_value', 'amount_spent_to_date', 'status', 'end_date', 'department_name']
    available_cols = [col for col in display_cols if col in df.columns]
    display_df = df[available_cols].head(30)
    table_data = [display_df.columns.tolist()] + display_df.fillna('').values.tolist()
    
    contract_table = Table(table_data, repeatRows=1)
    try:
        contract_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(HELB_GREEN)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
        ]))
    except:
        contract_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
        ]))
    
    elements.append(contract_table)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

def generate_policies_pdf_report(df, title="HELB Policies Report"):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
    styles = getSampleStyleSheet()
    elements = []
    
    try:
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor(HELB_GREEN))
    except:
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=16, textColor=colors.black)
    
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    
    active = len(df[df['status'] == 'active']) if 'status' in df.columns else 0
    expiring = len(df[df['status'] == 'expiring_soon']) if 'status' in df.columns else 0
    expired = len(df[df['status'] == 'expired']) if 'status' in df.columns else 0
    
    summary_data = [
        ["Metric", "Value"],
        ["Total Policies", str(len(df))],
        ["Active Policies", str(active)],
        ["Expiring Soon", str(expiring)],
        ["Expired", str(expired)]
    ]
    summary_table = Table(summary_data, colWidths=[2*inch, 2*inch])
    
    try:
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.HexColor(HELB_GREEN)),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (1, -1), 1, colors.black)
        ]))
    except:
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (1, -1), 1, colors.black)
        ]))
    
    elements.append(summary_table)
    elements.append(Spacer(1, 0.3*inch))
    
    display_cols = ['policy_name', 'category', 'policy_owner', 'expiry_date', 'status']
    available_cols = [col for col in display_cols if col in df.columns]
    display_df = df[available_cols].head(30)
    table_data = [display_df.columns.tolist()] + display_df.fillna('').values.tolist()
    
    policy_table = Table(table_data, repeatRows=1)
    try:
        policy_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(HELB_GREEN)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
        ]))
    except:
        policy_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
        ]))
    
    elements.append(policy_table)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

# ============================================
# BULK UPLOAD FUNCTIONS
# ============================================
def generate_work_plan_template():
    template_df = pd.DataFrame({
        "strategic_pillar": [
            "1. Customer Excellence",
            "2. Financial Sustainability and Stewardship"
        ],
        "strategy": [
            "Enhance customer service through digital platforms",
            "Optimize budget allocation and reduce costs"
        ],
        "key_result_area": [
            "Customer Satisfaction Score",
            "Budget Utilization"
        ],
        "planned_activity": [
            "Implement new customer feedback system",
            "Quarterly budget review process"
        ],
        "performance_indicator": [
            "Customer satisfaction rating",
            "Utilization rate"
        ],
        "annual_target": [
            "85%",
            "95%"
        ],
        "start_date": [
            "2025-01-01",
            "2025-01-01"
        ],
        "end_date": [
            "2025-12-31",
            "2025-12-31"
        ],
        "budget_allocation": [
            "100000",
            "50000"
        ],
        "activity_category": [
            "SP Deliverable",
            "PC Deliverable"
        ]
    })
    return template_df

def bulk_upload_work_plans(df, department_id, department_name, user_id):
    success_count = 0
    error_count = 0
    errors = []
    
    for idx, row in df.iterrows():
        try:
            if pd.isna(row.get("planned_activity")) or str(row.get("planned_activity")).strip() == "":
                continue
                
            work_plan_data = {
                "strategic_pillar": str(row.get("strategic_pillar", "")),
                "strategy": str(row.get("strategy", "")) if pd.notna(row.get("strategy")) else None,
                "key_result_area": str(row.get("key_result_area", "")),
                "planned_activity": str(row.get("planned_activity", "")),
                "performance_indicator": str(row.get("performance_indicator", "")),
                "budget_allocation": float(row.get("budget_allocation", 0)) if pd.notna(row.get("budget_allocation")) else None,
                "annual_target": str(row.get("annual_target", "")),
                "actual_achievement": 0,
                "start_date": pd.to_datetime(row.get("start_date")).date().isoformat() if pd.notna(row.get("start_date")) else None,
                "end_date": pd.to_datetime(row.get("end_date")).date().isoformat() if pd.notna(row.get("end_date")) else None,
                "due_date": pd.to_datetime(row.get("end_date")).date().isoformat() if pd.notna(row.get("end_date")) else None,
                "activity_category": str(row.get("activity_category", "SP Deliverable")),
                "status": "Pending",
                "progress_percent": 0,
                "department_id": department_id,
                "department_name": department_name,
                "created_by": user_id,
                "created_at": datetime.now().isoformat()
            }
            
            if add_work_plan(work_plan_data):
                success_count += 1
            else:
                error_count += 1
                errors.append(f"Row {idx+2}: Failed to insert")
        except Exception as e:
            error_count += 1
            errors.append(f"Row {idx+2}: {str(e)}")
    
    return success_count, error_count, errors

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
# CUSTOM CSS (WITH FIXED DROPDOWN VISIBILITY AND LOGIN PAGE)
# ============================================
if st.session_state.theme == "light":
    THEME_CSS = f"""
    <style>
        /* Base styles */
        .stApp, .main, .stMarkdown, .stMarkdown p, .stMarkdown div, 
        .stTextInput label, .stSelectbox label, .stDateInput label,
        .stNumberInput label, .stTextArea label, .stCheckbox label,
        div, span, p, label, .stMetric label, .stMetric div {{
            color: #000000 !important;
        }}
        
        /* CRITICAL FIX: Dropdown visibility - Light Theme */
        .stSelectbox, .stSelectbox div, .stSelectbox div[data-baseweb="select"] {{
            background-color: #ffffff !important;
        }}
        
        .stSelectbox div[data-baseweb="select"] div {{
            background-color: #ffffff !important;
            color: #000000 !important;
        }}
        
        .stSelectbox div[data-baseweb="select"] div[role="combobox"] {{
            background-color: #ffffff !important;
            color: #000000 !important;
        }}
        
        .stSelectbox div[data-baseweb="select"] input {{
            color: #000000 !important;
            background-color: #ffffff !important;
        }}
        
        .stSelectbox div[data-baseweb="select"] div[data-baseweb="popover"] {{
            background-color: #ffffff !important;
        }}
        
        .stSelectbox ul, .stSelectbox li, div[role="listbox"], div[role="option"] {{
            background-color: #ffffff !important;
            color: #000000 !important;
        }}
        
        .stSelectbox div[role="option"]:hover {{
            background-color: #f0f0f0 !important;
            color: #000000 !important;
        }}
        
        .stSelectbox div[data-baseweb="select"] span {{
            color: #000000 !important;
        }}
        
        select, .stSelectbox select, .stSelectbox div[data-baseweb="select"] div {{
            background-color: #ffffff !important;
            color: #000000 !important;
        }}
        
        select option, .stSelectbox select option {{
            background-color: #ffffff !important;
            color: #000000 !important;
        }}
        
        .stSelectbox [data-baseweb="select"] * {{
            color: #000000 !important;
        }}
        
        .stDateInput input, .stDateInput div {{
            background-color: #ffffff !important;
            color: #000000 !important;
        }}
        
        .stTextInput input {{
            background-color: #ffffff !important;
            color: #000000 !important;
        }}
        
        .stNumberInput input {{
            background-color: #ffffff !important;
            color: #000000 !important;
        }}
        
        .stTextArea textarea {{
            background-color: #ffffff !important;
            color: #000000 !important;
        }}
        
        .stMultiSelect div[data-baseweb="select"] {{
            background-color: #ffffff !important;
        }}
        
        .stMultiSelect div[data-baseweb="select"] div {{
            background-color: #ffffff !important;
            color: #000000 !important;
        }}
        
        .stMultiSelect div[data-baseweb="select"] input {{
            color: #000000 !important;
            background-color: #ffffff !important;
        }}
        
        .stMultiSelect div[data-baseweb="select"] span {{
            color: #000000 !important;
        }}
        
        [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] div {{
            background-color: rgba(255,255,255,0.95) !important;
            color: #000000 !important;
        }}
        
        [data-testid="stSidebar"] .stSelectbox div[role="option"] {{
            background-color: #ffffff !important;
            color: #000000 !important;
        }}
        
        [data-testid="stSidebar"] .stSelectbox div[role="option"]:hover {{
            background-color: #f0f0f0 !important;
            color: #000000 !important;
        }}
        
        .stButton > button {{
            background: linear-gradient(135deg, {HELB_GREEN} 0%, {HELB_BLUE} 100%) !important;
            color: white !important;
            border-radius: 8px !important;
            padding: 8px 16px !important;
            font-weight: 600 !important;
        }}
        
        .stButton > button:hover {{
            opacity: 0.9 !important;
        }}
        
        .stButton > button[key*="delete"] {{
            background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%) !important;
            color: white !important;
        }}
        
        [data-testid="stSidebar"] {{
            background-color: {HELB_GREEN} !important;
            padding-top: 1rem;
        }}
        [data-testid="stSidebar"] * {{
            color: white !important;
        }}
        
        .kpi-card {{
            background: linear-gradient(135deg, {HELB_GREEN} 0%, {HELB_BLUE} 100%) !important;
            border-radius: 12px !important;
            padding: 0.8rem !important;
            text-align: center !important;
            min-height: 110px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}
        .kpi-card .kpi-label {{
            font-size: 0.65rem !important;
            text-transform: uppercase !important;
            color: {HELB_GOLD} !important;
            font-weight: 600 !important;
            letter-spacing: 0.5px !important;
            margin-bottom: 0.25rem;
        }}
        .kpi-card .kpi-value {{
            font-size: 1.3rem !important;
            font-weight: 700 !important;
            margin: 0.2rem 0 !important;
            color: #FFFFFF !important;
        }}
        .kpi-card .kpi-sub {{
            font-size: 0.5rem !important;
            color: #FFFFFF !important;
            margin-top: 0.2rem !important;
            opacity: 0.9 !important;
        }}
        .kpi-card .progress-bar {{
            height: 3px !important;
            background: rgba(255,255,255,0.3) !important;
            border-radius: 2px !important;
            margin-top: 0.5rem !important;
            width: 100%;
        }}
        .kpi-card .progress-fill {{
            height: 100% !important;
            background: {HELB_GOLD} !important;
            border-radius: 2px !important;
        }}
        
        .kpi-card-small {{
            background: linear-gradient(135deg, {HELB_GREEN} 0%, {HELB_BLUE} 100%) !important;
            border-radius: 10px !important;
            padding: 0.6rem !important;
            text-align: center !important;
            min-height: 85px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}
        .kpi-card-small .kpi-label {{
            font-size: 0.6rem !important;
            text-transform: uppercase !important;
            color: {HELB_GOLD} !important;
            font-weight: 600 !important;
        }}
        .kpi-card-small .kpi-value {{
            font-size: 1.1rem !important;
            font-weight: 700 !important;
            color: #FFFFFF !important;
        }}
        .kpi-card-small .kpi-sub {{
            font-size: 0.45rem !important;
            color: #FFFFFF !important;
        }}
        
        .comment-box {{
            background: #f0fdf4;
            border-left: 4px solid {HELB_GREEN};
            padding: 0.5rem 0.8rem;
            margin-top: 0.5rem;
            border-radius: 8px;
            font-size: 0.75rem;
            color: #166534;
        }}
        
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
        .status-urgent {{ background-color: #dc2626 !important; color: white !important; }}
        .status-risk-high {{ background-color: #dc2626 !important; color: white !important; }}
        .status-risk-medium {{ background-color: #f59e0b !important; color: white !important; }}
        .status-risk-low {{ background-color: #10b981 !important; color: white !important; }}
        
        .metric-card, .metric-card * {{ color: #000000 !important; }}
        .stTabs [data-baseweb="tab"] {{ color: #000000 !important; }}
        .stTabs [aria-selected="true"] {{ color: #000000 !important; background-color: {HELB_GOLD} !important; }}
        .streamlit-expanderHeader p {{ color: #000000 !important; }}
        
        h1, h2, h3, h4, h5, h6 {{ color: {HELB_GREEN} !important; }}
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        .stAppDeployButton {{display: none;}}
        .main, .stApp {{ background-color: {HELB_WHITE} !important; }}
        
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
            background-color: {HELB_BLUE} !important;
            color: white !important;
        }}
        
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
        
        .footer {{ text-align: center; padding: 1rem; color: #6B7280; font-size: 0.6rem; border-top: 1px solid #E5E7EB; margin-top: 1.5rem; }}
        .dataframe th {{ background-color: {HELB_GREEN} !important; color: white !important; font-size: 0.7rem; }}
        .dataframe td {{ color: #000000 !important; font-size: 0.7rem; }}
        
        /* FIXED LOGIN PAGE - CLEAN, CENTERED, NO HEADROOM */
        .login-wrapper {{
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 1rem;
            background: {HELB_WHITE};
        }}
        .login-container {{
            background: #ffffff;
            border-radius: 16px;
            padding: 0;
            box-shadow: 0 20px 60px rgba(0,0,0,0.12);
            max-width: 400px;
            width: 100%;
            overflow: hidden;
            margin: 0 auto;
        }}
        .login-header {{
            background: linear-gradient(135deg, {HELB_GREEN} 0%, #004d2a 100%);
            padding: 2rem 1.5rem 1.5rem;
            text-align: center;
        }}
        .login-logo {{
            margin-bottom: 0.75rem;
            display: flex;
            justify-content: center;
        }}
        .login-title {{
            color: white !important;
            font-size: 1.1rem !important;
            font-weight: 700 !important;
            margin: 0.25rem 0 0.1rem 0 !important;
            text-align: center !important;
            letter-spacing: 0.5px;
        }}
        .login-subtitle {{
            color: {HELB_GOLD} !important;
            font-size: 0.7rem !important;
            text-align: center !important;
            margin-bottom: 0 !important;
            font-weight: 500;
        }}
        .login-divider {{
            height: 2px;
            background: {HELB_GOLD};
            width: 40px;
            margin: 0.5rem auto 0;
            border-radius: 2px;
        }}
        .login-body {{
            padding: 1.5rem 1.5rem 1rem;
        }}
        .login-footer {{
            text-align: center;
            padding: 0.75rem;
            border-top: 1px solid #e5e7eb;
            font-size: 0.55rem;
            color: #9ca3af;
            background: #f9fafb;
        }}
        .login-footer p {{
            margin: 2px 0;
        }}
        .login-container .stTextInput input {{
            background-color: #f9fafb !important;
            color: #1F2937 !important;
            border: 1px solid #e5e7eb !important;
            border-radius: 8px !important;
            padding: 10px 12px !important;
            font-size: 0.85rem !important;
        }}
        .login-container .stTextInput input:focus {{
            border-color: {HELB_GREEN} !important;
            box-shadow: 0 0 0 3px rgba(0,132,61,0.1) !important;
        }}
        .login-container .stTextInput label {{
            color: #374151 !important;
            font-weight: 600 !important;
            font-size: 0.8rem !important;
        }}
        .login-container .stButton > button {{
            background: linear-gradient(135deg, {HELB_GREEN} 0%, #004d2a 100%) !important;
            color: white !important;
            font-weight: 600 !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 10px !important;
            font-size: 0.9rem !important;
            margin-top: 0.5rem;
        }}
        .login-container .stButton > button:hover {{
            opacity: 0.95;
            transform: translateY(-1px);
        }}
        
        @media (max-width: 768px) {{
            .kpi-card {{
                min-height: 80px !important;
                padding: 0.5rem !important;
            }}
            .kpi-card .kpi-value {{
                font-size: 1rem !important;
            }}
            .kpi-card .kpi-label {{
                font-size: 0.55rem !important;
            }}
            .stTabs [data-baseweb="tab-list"] {{
                flex-wrap: wrap;
            }}
            .stTabs [data-baseweb="tab"] {{
                padding: 0.5rem 1rem !important;
                font-size: 0.8rem !important;
            }}
            .dashboard-header h1 {{
                font-size: 1rem !important;
            }}
            .dashboard-header p {{
                font-size: 0.6rem !important;
            }}
            .login-wrapper {{
                padding: 0.5rem !important;
            }}
            .login-container {{
                margin: 0.5rem !important;
                max-width: 95% !important;
            }}
            .login-title {{
                font-size: 0.9rem !important;
            }}
        }}
    </style>
    """
else:
    THEME_CSS = f"""
    <style>
        .stApp, .main, .stMarkdown, .stMarkdown p, .stMarkdown div, 
        .stTextInput label, .stSelectbox label, .stDateInput label,
        .stNumberInput label, .stTextArea label, .stCheckbox label,
        div, span, p, label, .stMetric label, .stMetric div {{
            color: #FFFFFF !important;
        }}
        
        .stSelectbox, .stSelectbox div, .stSelectbox div[data-baseweb="select"] {{
            background-color: #2d2d44 !important;
        }}
        
        .stSelectbox div[data-baseweb="select"] div {{
            background-color: #2d2d44 !important;
            color: #FFFFFF !important;
        }}
        
        .stSelectbox div[data-baseweb="select"] div[role="combobox"] {{
            background-color: #2d2d44 !important;
            color: #FFFFFF !important;
        }}
        
        .stSelectbox div[data-baseweb="select"] input {{
            color: #FFFFFF !important;
            background-color: #2d2d44 !important;
        }}
        
        .stSelectbox div[data-baseweb="select"] div[data-baseweb="popover"] {{
            background-color: #2d2d44 !important;
        }}
        
        .stSelectbox ul, .stSelectbox li, div[role="listbox"], div[role="option"] {{
            background-color: #2d2d44 !important;
            color: #FFFFFF !important;
        }}
        
        .stSelectbox div[role="option"]:hover {{
            background-color: #3d3d5c !important;
            color: #FFFFFF !important;
        }}
        
        .stSelectbox div[data-baseweb="select"] span {{
            color: #FFFFFF !important;
        }}
        
        select, .stSelectbox select, .stSelectbox div[data-baseweb="select"] div {{
            background-color: #2d2d44 !important;
            color: #FFFFFF !important;
        }}
        
        select option, .stSelectbox select option {{
            background-color: #2d2d44 !important;
            color: #FFFFFF !important;
        }}
        
        .stSelectbox [data-baseweb="select"] * {{
            color: #FFFFFF !important;
        }}
        
        .stDateInput input, .stDateInput div {{
            background-color: #2d2d44 !important;
            color: #FFFFFF !important;
        }}
        
        .stTextInput input {{
            background-color: #2d2d44 !important;
            color: #FFFFFF !important;
        }}
        
        .stNumberInput input {{
            background-color: #2d2d44 !important;
            color: #FFFFFF !important;
        }}
        
        .stTextArea textarea {{
            background-color: #2d2d44 !important;
            color: #FFFFFF !important;
        }}
        
        .stMultiSelect div[data-baseweb="select"] {{
            background-color: #2d2d44 !important;
        }}
        
        .stMultiSelect div[data-baseweb="select"] div {{
            background-color: #2d2d44 !important;
            color: #FFFFFF !important;
        }}
        
        .stMultiSelect div[data-baseweb="select"] input {{
            color: #FFFFFF !important;
            background-color: #2d2d44 !important;
        }}
        
        .stMultiSelect div[data-baseweb="select"] span {{
            color: #FFFFFF !important;
        }}
        
        [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] div {{
            background-color: rgba(255,255,255,0.15) !important;
            color: #FFFFFF !important;
        }}
        
        [data-testid="stSidebar"] .stSelectbox div[role="option"] {{
            background-color: #0f3460 !important;
            color: #FFFFFF !important;
        }}
        
        [data-testid="stSidebar"] .stSelectbox div[role="option"]:hover {{
            background-color: {HELB_GREEN} !important;
            color: #FFFFFF !important;
        }}
        
        .stButton > button {{
            background: linear-gradient(135deg, #0f3460 0%, #16213e 100%) !important;
            color: white !important;
            border-radius: 8px !important;
            padding: 8px 16px !important;
            font-weight: 600 !important;
        }}
        
        .stButton > button:hover {{
            opacity: 0.9 !important;
        }}
        
        .stButton > button[key*="delete"] {{
            background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%) !important;
            color: white !important;
        }}
        
        .kpi-card {{
            background: linear-gradient(135deg, #0f3460 0%, #16213e 100%) !important;
            border-radius: 12px !important;
            padding: 0.8rem !important;
            text-align: center !important;
            min-height: 110px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}
        .kpi-card .kpi-label {{
            font-size: 0.65rem !important;
            text-transform: uppercase !important;
            color: {HELB_GOLD} !important;
            font-weight: 600 !important;
            letter-spacing: 0.5px !important;
            margin-bottom: 0.25rem;
        }}
        .kpi-card .kpi-value {{
            font-size: 1.3rem !important;
            font-weight: 700 !important;
            margin: 0.2rem 0 !important;
            color: #FFFFFF !important;
        }}
        .kpi-card .kpi-sub {{
            font-size: 0.5rem !important;
            color: #FFFFFF !important;
            margin-top: 0.2rem !important;
            opacity: 0.9 !important;
        }}
        .kpi-card .progress-bar {{
            height: 3px !important;
            background: rgba(255,255,255,0.3) !important;
            border-radius: 2px !important;
            margin-top: 0.5rem !important;
            width: 100%;
        }}
        .kpi-card .progress-fill {{
            height: 100% !important;
            background: {HELB_GOLD} !important;
            border-radius: 2px !important;
        }}
        
        .kpi-card-small {{
            background: linear-gradient(135deg, #0f3460 0%, #16213e 100%) !important;
            border-radius: 10px !important;
            padding: 0.6rem !important;
            text-align: center !important;
            min-height: 85px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}
        .kpi-card-small .kpi-label {{
            font-size: 0.6rem !important;
            text-transform: uppercase !important;
            color: {HELB_GOLD} !important;
            font-weight: 600 !important;
        }}
        .kpi-card-small .kpi-value {{
            font-size: 1.1rem !important;
            font-weight: 700 !important;
            color: #FFFFFF !important;
        }}
        .kpi-card-small .kpi-sub {{
            font-size: 0.45rem !important;
            color: #FFFFFF !important;
        }}
        
        .comment-box {{
            background: #1e3a2f;
            border-left: 4px solid {HELB_GOLD};
            padding: 0.5rem 0.8rem;
            margin-top: 0.5rem;
            border-radius: 8px;
            font-size: 0.75rem;
            color: #d1fae5;
        }}
        
        .contract-card, .policy-card {{
            background: #1e293b !important;
            border: 1px solid #334155 !important;
            border-radius: 12px !important;
            padding: 1rem !important;
            margin-bottom: 0.75rem !important;
        }}
        .contract-title, .policy-title {{
            font-size: 1rem !important;
            font-weight: 700 !important;
            color: {HELB_GOLD} !important;
            margin-bottom: 0.5rem !important;
        }}
        .contract-detail, .policy-detail {{
            font-size: 0.75rem !important;
            color: #cbd5e1 !important;
            margin: 0.25rem 0 !important;
        }}
        
        .metric-card, .metric-card * {{ color: #FFFFFF !important; }}
        .stTabs [data-baseweb="tab"] {{ color: #FFFFFF !important; }}
        .stTabs [aria-selected="true"] {{ background-color: {HELB_GOLD} !important; color: #1F2937 !important; }}
        .streamlit-expanderHeader p {{ color: {HELB_GOLD} !important; }}
        
        .stTextInput input, .stSelectbox div, .stDateInput input, 
        .stNumberInput input, .stTextArea textarea {{
            background-color: #2d2d44 !important;
            color: #FFFFFF !important;
            border: 1px solid #4a4a6a !important;
        }}
        
        h1, h2, h3, h4, h5, h6 {{ color: {HELB_GOLD} !important; }}
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        .stAppDeployButton {{display: none;}}
        .main, .stApp {{ background-color: #1a1a2e !important; }}
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
        
        .footer {{ text-align: center; padding: 1rem; color: #6B7280; border-top: 1px solid #2d2d44; margin-top: 1.5rem; }}
        .dataframe th {{ background-color: {HELB_GREEN} !important; color: white !important; font-size: 0.7rem; }}
        .dataframe td {{ color: #FFFFFF !important; font-size: 0.7rem; }}
        
        /* FIXED LOGIN PAGE - CLEAN, CENTERED, NO HEADROOM - DARK THEME */
        .login-wrapper {{
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 1rem;
            background: #1a1a2e;
        }}
        .login-container {{
            background: #1e293b;
            border-radius: 16px;
            padding: 0;
            box-shadow: 0 20px 60px rgba(0,0,0,0.4);
            max-width: 400px;
            width: 100%;
            overflow: hidden;
            margin: 0 auto;
        }}
        .login-header {{
            background: linear-gradient(135deg, {HELB_GREEN} 0%, #004d2a 100%);
            padding: 2rem 1.5rem 1.5rem;
            text-align: center;
        }}
        .login-logo {{
            margin-bottom: 0.75rem;
            display: flex;
            justify-content: center;
        }}
        .login-title {{
            color: white !important;
            font-size: 1.1rem !important;
            font-weight: 700 !important;
            margin: 0.25rem 0 0.1rem 0 !important;
            text-align: center !important;
            letter-spacing: 0.5px;
        }}
        .login-subtitle {{
            color: {HELB_GOLD} !important;
            font-size: 0.7rem !important;
            text-align: center !important;
            margin-bottom: 0 !important;
            font-weight: 500;
        }}
        .login-divider {{
            height: 2px;
            background: {HELB_GOLD};
            width: 40px;
            margin: 0.5rem auto 0;
            border-radius: 2px;
        }}
        .login-body {{
            padding: 1.5rem 1.5rem 1rem;
        }}
        .login-footer {{
            text-align: center;
            padding: 0.75rem;
            border-top: 1px solid #334155;
            font-size: 0.55rem;
            color: #64748b;
            background: #0f172a;
        }}
        .login-footer p {{
            margin: 2px 0;
        }}
        .login-container .stTextInput input {{
            background-color: #334155 !important;
            color: #f1f5f9 !important;
            border: 1px solid #475569 !important;
            border-radius: 8px !important;
            padding: 10px 12px !important;
            font-size: 0.85rem !important;
        }}
        .login-container .stTextInput input:focus {{
            border-color: {HELB_GOLD} !important;
            box-shadow: 0 0 0 3px rgba(255,184,28,0.1) !important;
        }}
        .login-container .stTextInput label {{
            color: #cbd5e1 !important;
            font-weight: 600 !important;
            font-size: 0.8rem !important;
        }}
        .login-container .stButton > button {{
            background: linear-gradient(135deg, {HELB_GREEN} 0%, #004d2a 100%) !important;
            color: white !important;
            font-weight: 600 !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 10px !important;
            font-size: 0.9rem !important;
            margin-top: 0.5rem;
        }}
        .login-container .stButton > button:hover {{
            opacity: 0.95;
            transform: translateY(-1px);
        }}
        
        @media (max-width: 768px) {{
            .kpi-card {{
                min-height: 80px !important;
                padding: 0.5rem !important;
            }}
            .kpi-card .kpi-value {{
                font-size: 1rem !important;
            }}
            .kpi-card .kpi-label {{
                font-size: 0.55rem !important;
            }}
            .stTabs [data-baseweb="tab-list"] {{
                flex-wrap: wrap;
            }}
            .stTabs [data-baseweb="tab"] {{
                padding: 0.5rem 1rem !important;
                font-size: 0.8rem !important;
            }}
            .dashboard-header h1 {{
                font-size: 1rem !important;
            }}
            .dashboard-header p {{
                font-size: 0.6rem !important;
            }}
            .login-wrapper {{
                padding: 0.5rem !important;
            }}
            .login-container {{
                margin: 0.5rem !important;
                max-width: 95% !important;
            }}
            .login-title {{
                font-size: 0.9rem !important;
            }}
        }}
    </style>
    """

st.markdown(THEME_CSS, unsafe_allow_html=True)

# ============================================
# LOGIN PAGE - PERFECT GREEN HEADER & GREEN BUTTON
# ============================================
if not st.session_state.authenticated:
    # Center using Streamlit columns
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Main container with green header covering logo AND title
        st.markdown("""
        <div style='
            background: white;
            border-radius: 16px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            overflow: hidden;
            margin: 1rem 0;
        '>
            <!-- GREEN HEADER - Covers Logo, Title, and Subtitle -->
            <div style='
                background: linear-gradient(135deg, #00843D 0%, #00529B 100%);
                padding: 2rem 1.5rem 1.5rem 1.5rem;
                text-align: center;
            '>
        """, unsafe_allow_html=True)
        
        # Centered Logo (inside green header)
        st.markdown('<div style="display: flex; justify-content: center; margin-bottom: 0.75rem;">', unsafe_allow_html=True)
        if LOGO_BASE64:
            st.markdown(f'''
                <img src="data:image/png;base64,{LOGO_BASE64}" 
                     style="width: 70px; height: auto; background: transparent;">
            ''', unsafe_allow_html=True)
        else:
            st.markdown('<div style="font-size: 3rem;">🏦</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Title and Subtitle (ALL inside green header with white/gold text)
        st.markdown("""
            <h1 style='
                color: white !important;
                font-size: 1.2rem;
                font-weight: 700;
                margin: 0.25rem 0 0.1rem 0;
                text-align: center;
                letter-spacing: 0.5px;
            '>HIGHER EDUCATION LOANS BOARD</h1>
            <p style='
                color: #FFB81C !important;
                font-size: 0.7rem;
                text-align: center;
                margin: 0.25rem 0 0 0;
                font-weight: 500;
            '>Strategy Performance Management System</p>
            <div style='
                height: 2px;
                background: #FFB81C;
                width: 40px;
                margin: 0.5rem auto 0;
                border-radius: 2px;
            '></div>
        </div>
        """, unsafe_allow_html=True)
        
        # Login Form Body (White background)
        st.markdown("""
        <div style='padding: 1.5rem 1.5rem 1rem 1.5rem;'>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input(
                "Username", 
                placeholder="Enter your username",
                key="login_username"
            )
            password = st.text_input(
                "Password", 
                type="password", 
                placeholder="Enter your password",
                key="login_password"
            )
            
            # This will use the green button CSS below
            submitted = st.form_submit_button(
                "Sign In", 
                use_container_width=True
            )
            
            if submitted:
                if username and password:
                    # Your existing authentication logic
                    result = supabase.table("users").select("*").eq("username", username.lower()).execute()
                    if result.data:
                        user = result.data[0]
                        if (password == user["password_hash"] or 
                            hash_password(password) == user["password_hash"] or
                            user["password_hash"] == "password123"):
                            dept_name = get_department_name(user["department_id"])
                            is_strategy_dept = dept_name == "Strategy"
                            
                            st.session_state.authenticated = True
                            st.session_state.user = user
                            st.session_state.user_role = "management" if is_strategy_dept and user["role"] != "admin" else user["role"]
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
                    st.warning("Please enter both username and password")
        
        # Footer
        st.markdown("""
        </div>
        <div style='
            text-align: center;
            padding: 0.75rem;
            border-top: 1px solid #E5E7EB;
            background: #F9FAFB;
        '>
            <p style='
                font-size: 0.55rem;
                color: #9CA3AF;
                margin: 0;
            '>© 2025 HELB - Higher Education Loans Board</p>
            <p style='
                font-size: 0.55rem;
                color: #9CA3AF;
                margin: 2px 0;
            '>Secure System Access</p>
        </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.stop()
# ============================================
# MAIN APPLICATION HEADER WITH COUNTDOWN
# ============================================
col_header, col_theme, col_refresh = st.columns([4, 1, 1])
with col_header:
    if LOGO_BASE64:
        st.image(f"data:image/png;base64,{LOGO_BASE64}", width=40)
    else:
        st.markdown('<div style="font-size: 1.5rem;">🏦</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class='dashboard-header'>
        <div>
            <h1>HELB Strategy Performance Management System</h1>
            <p>Real-time monitoring | Work Plans | Contracts | Policies</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Display countdown timer
    display_countdown_timer()

with col_theme:
    theme_icon = "🌙" if st.session_state.theme == "light" else "☀️"
    theme_label = "Dark" if st.session_state.theme == "light" else "Light"
    if st.button(f"{theme_icon} {theme_label}", key="theme_toggle"):
        toggle_theme()

with col_refresh:
    if st.button("🔄 Refresh", key="global_refresh"):
        st.cache_data.clear()
        st.rerun()

with st.sidebar:
    if LOGO_BASE64:
        st.image(f"data:image/png;base64,{LOGO_BASE64}", width=120)
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
    
    with st.expander("🔐 Account Settings", expanded=False):
        st.markdown("#### Change Password")
        with st.form("change_password_form"):
            current_pwd = st.text_input("Current Password", type="password", key="current_pwd")
            new_pwd = st.text_input("New Password", type="password", key="new_pwd")
            confirm_pwd = st.text_input("Confirm New Password", type="password", key="confirm_pwd")
            
            if st.form_submit_button("Update Password", use_container_width=True):
                if new_pwd == confirm_pwd:
                    success, message = change_user_password(st.session_state.user_name, current_pwd, new_pwd)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
                else:
                    st.error("New passwords do not match")
    
    st.markdown("---")
    
    menu_options = ["📊 Dashboard", "📋 Work Plans", "📄 Contracts", "📋 Policies"]
    if st.session_state.user_role == "admin":
        menu_options.append("⚙️ Admin Panel")
    if st.session_state.user_role in ["admin", "management"]:
        menu_options.append("🏢 Enterprise View")
    
    selected_menu = st.radio(
        "📋 Navigation", 
        menu_options, 
        label_visibility="collapsed",
        key="nav_menu_radio",
        index=menu_options.index(st.session_state.active_menu) if st.session_state.active_menu in menu_options else 0
    )
    
    if selected_menu != st.session_state.active_menu:
        st.session_state.active_menu = selected_menu
        st.rerun()
    
    st.markdown("---")
    
    if st.button("🚪 Logout", use_container_width=True):
        add_audit_log("LOGOUT", "session", None, f"User logged out")
        st.session_state.clear()
        st.cache_data.clear()
        st.rerun()

# ============================================
# WORK PLANS MODULE - COMPLETE
# ============================================
if st.session_state.active_menu == "📋 Work Plans":
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
    
    tab_labels = [
        "➕ Add Work Plan Activity", 
        "📊 View All Activities", 
        "📅 Calendar View",
        "📅 Gantt Chart View",
        "🔮 Predictive Analytics",
        "⚠️ Expiring in 60 Days",
        "📤 Bulk Upload",
        "📈 Performance Dashboard"
    ]
    
    tab_add, tab_view, tab_calendar, tab_gantt, tab_predictive, tab_expiring, tab_bulk, tab_dashboard = st.tabs(tab_labels)
    
    col_export1, col_export2 = st.columns([6, 1])
    with col_export2:
        if filtered_plans:
            df_export = pd.DataFrame(filtered_plans)
            if 'calculated_progress' not in df_export.columns:
                df_export['calculated_progress'] = df_export.apply(lambda x: calculate_progress_from_actual(x.get('annual_target', '0'), x.get('actual_achievement', 0)), axis=1)
            pdf_buffer = generate_work_plan_pdf_report(df_export, f"HELB Work Plan Report - {datetime.now().strftime('%Y-%m-%d')}")
            st.download_button(
                label="📄 Export PDF",
                data=pdf_buffer,
                file_name=f"work_plan_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf",
                key="export_work_plan_pdf"
            )
    
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
                start_date = st.date_input("Start Date*", value=datetime.now().date())
                end_date = st.date_input("End Date*")
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
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat(),
                        "due_date": end_date.isoformat(),
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
                    badge = '<span class="status-badge status-expired">🔴 Pending</span>'
                elif progress_percent >= 100:
                    if exceeded:
                        badge = '<span class="status-badge status-active">✅ Done (Exceeded!)</span>'
                    else:
                        badge = '<span class="status-badge status-active">✅ Done</span>'
                elif progress_percent > 0:
                    badge = '<span class="status-badge status-expiring">🟡 In Progress</span>'
                else:
                    badge = '<span class="status-badge status-expired">🔴 Pending</span>'
                
                if days_left < 0:
                    days_indicator = f"🔴 (EXPIRED)"
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
                        st.markdown(f"**Start Date:** {plan.get('start_date', 'N/A')}")
                        st.markdown(f"**End Date:** {plan.get('end_date', 'N/A')}")
                        st.markdown(f"**Due Date:** {plan['due_date']} ({days_left} days left)")
                        st.markdown(f"**Activity Category:** {plan.get('activity_category', 'N/A')}")
                        st.markdown(f"**Department:** {plan.get('department_name', 'N/A')}")
                        
                        if plan.get('comment'):
                            st.markdown(f"""
                            <div class='comment-box'>
                                <strong>📝 Latest Comment:</strong><br>
                                {plan['comment']}
                            </div>
                            """, unsafe_allow_html=True)
                    
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
                        
                        update_comment = st.text_area("Comment (optional)", placeholder="Add any remarks or notes about this update...", key=f"comment_{plan['id']}", height=68)
                        
                        if st.session_state.user_role == "admin":
                            st.markdown("---")
                            st.markdown("**📅 Admin: Edit Dates**")
                            new_start_date = st.date_input("New Start Date", value=datetime.strptime(plan.get('start_date', plan['due_date']), "%Y-%m-%d").date() if plan.get('start_date') else due_date, key=f"startdate_{plan['id']}")
                            new_end_date = st.date_input("New End Date", value=due_date, key=f"enddate_{plan['id']}")
                            if st.button(f"Update Dates", key=f"updatedates_{plan['id']}"):
                                update_data = {
                                    "start_date": new_start_date.isoformat(),
                                    "end_date": new_end_date.isoformat(),
                                    "due_date": new_end_date.isoformat()
                                }
                                if update_work_plan_admin(plan['id'], update_data):
                                    st.success("✅ Dates updated!")
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
                                if update_work_plan_progress(plan['id'], actual_input, new_progress, new_status, update_comment if update_comment else None):
                                    st.success("✅ Achievement updated successfully!")
                                    if update_comment:
                                        st.info(f"📝 Comment saved: {update_comment}")
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
    
    with tab_calendar:
        st.markdown("### 📅 Calendar View")
        st.markdown("Visualize all activities by month and quarter - **Click on any date to see all activities**")
        
        if filtered_plans:
            col_year, col_quarter, col_month = st.columns(3)
            with col_year:
                current_year = datetime.now().year
                selected_year = st.selectbox("Select Year", [current_year - 1, current_year, current_year + 1], index=1)
            with col_quarter:
                quarters = ["All", "Q1 (Jul-Sep)", "Q2 (Oct-Dec)", "Q3 (Jan-Mar)", "Q4 (Apr-Jun)"]
                selected_quarter = st.selectbox("Select Quarter", quarters, key="calendar_quarter_select")
            with col_month:
                selected_month = st.selectbox("Select Month", list(range(1, 13)), format_func=lambda x: datetime(2000, x, 1).strftime('%B'), index=datetime.now().month - 1)
            
            # Use enhanced calendar with click functionality
            calendar_html = generate_calendar_html(filtered_plans, selected_year, selected_month, selected_quarter)
            st.components.v1.html(calendar_html, height=750, scrolling=True)
            
            # Quick stats below calendar
            st.markdown("---")
            
            # Pillar Performance Summary for Management - RESTORED
            st.markdown("### 📊 Pillar Performance Summary")
            st.markdown("High-level overview of implementation progress by strategic pillar")
            
            pillar_df = generate_pillar_performance_summary(filtered_plans)
            
            if not pillar_df.empty:
                # Display pillar performance as cards
                cols = st.columns(min(len(pillar_df), 5))
                for idx, (_, row) in enumerate(pillar_df.iterrows()):
                    col_idx = idx % len(cols)
                    with cols[col_idx]:
                        pillar_name = row['Pillar'].split('. ')[-1] if '. ' in row['Pillar'] else row['Pillar']
                        # Determine progress color
                        progress_color = "#10B981" if row['Completion Rate'] >= 75 else "#F59E0B" if row['Completion Rate'] >= 40 else "#EF4444"
                        st.markdown(f"""
                        <div style="background: {HELB_GREEN}10; border-radius: 10px; padding: 0.8rem; border: 1px solid {HELB_GREEN}30; margin-bottom: 0.5rem;">
                            <div style="font-size: 0.65rem; font-weight: 600; color: {HELB_GREEN};">{pillar_name[:30]}</div>
                            <div style="font-size: 1.2rem; font-weight: 700; color: #1F2937;">{row['Completion Rate']}%</div>
                            <div style="display: flex; gap: 0.5rem; margin-top: 0.3rem; flex-wrap: wrap;">
                                <span style="font-size: 0.55rem; background: #10B98120; padding: 0.1rem 0.4rem; border-radius: 8px;">✅ {row['Completed']}</span>
                                <span style="font-size: 0.55rem; background: #F59E0B20; padding: 0.1rem 0.4rem; border-radius: 8px;">🟡 {row['In Progress']}</span>
                                <span style="font-size: 0.55rem; background: #EF444420; padding: 0.1rem 0.4rem; border-radius: 8px;">⏳ {row['Pending']}</span>
                            </div>
                            <div style="margin-top: 0.3rem; height: 4px; background: #E5E7EB; border-radius: 2px; overflow: hidden;">
                                <div style="width: {row['Completion Rate']}%; height: 100%; background: {progress_color}; border-radius: 2px; transition: width 0.5s;"></div>
                            </div>
                            <div style="font-size: 0.5rem; color: #6B7280; margin-top: 0.2rem;">Total: {row['Total']} activities</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Display detailed table
                with st.expander("📋 View Detailed Pillar Performance Table", expanded=False):
                    st.dataframe(pillar_df, use_container_width=True, hide_index=True)
                    
                    # Create a bar chart visualization
                    fig = px.bar(pillar_df, x='Pillar', y='Completion Rate', 
                                 color='Completion Rate', 
                                 color_continuous_scale='Greens',
                                 text='Completion Rate',
                                 title="Pillar Completion Rates")
                    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                    fig.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No pillar data available for the selected period.")
            
            # Date Activity Details (popup info)
            st.markdown("---")
            st.markdown("### 📅 Date Activity Details")
            st.info("💡 Click on any date or activity in the calendar above to see all activities for that day in a popup window.")
            
        else:
            st.info("No activities to display. Please add work plan activities with start and end dates.")
    
    with tab_gantt:
        st.markdown("### 📅 Work Plan Gantt Chart")
        st.markdown("Visualize all activities by month and quarter")
        
        if filtered_plans:
            gantt_data = []
            for plan in filtered_plans:
                if plan.get('start_date') and plan.get('end_date'):
                    # Determine status color based on progress
                    progress = plan.get('progress_percent', 0)
                    if progress == 0:
                        status_color = "#EF4444"  # Red for pending
                        status_label = "Pending"
                    elif progress >= 100:
                        status_color = "#00843D"  # HELB Green for completed
                        status_label = "Completed"
                    else:
                        status_color = "#FFB81C"  # HELB Gold for in progress
                        status_label = "In Progress"
                    
                    gantt_data.append({
                        "Activity": plan['planned_activity'][:50] + "..." if len(plan['planned_activity']) > 50 else plan['planned_activity'],
                        "Start": plan['start_date'],
                        "Finish": plan['end_date'],
                        "Department": plan.get('department_name', 'Unknown'),
                        "Progress": progress,
                        "Status": plan.get('status', 'Pending'),
                        "Status_Color": status_color,
                        "Status_Label": status_label,
                        "Progress_Display": f"{progress}%"
                    })
            
            if gantt_data:
                df_gantt = pd.DataFrame(gantt_data)
                
                col_month_filter, col_dept_filter_gantt = st.columns(2)
                with col_month_filter:
                    selected_month = st.selectbox("Filter by Month", ["All"] + ALL_MONTHS)
                with col_dept_filter_gantt:
                    if st.session_state.user_role in ["admin", "management"]:
                        depts = df_gantt['Department'].unique().tolist()
                        selected_dept_gantt = st.selectbox("Filter by Department", ["All"] + depts)
                    else:
                        selected_dept_gantt = "All"
                
                filtered_gantt = df_gantt.copy()
                if selected_month != "All":
                    month_num = ALL_MONTHS.index(selected_month) + 1
                    filtered_gantt = filtered_gantt[
                        (pd.to_datetime(filtered_gantt['Start']).dt.month <= month_num) &
                        (pd.to_datetime(filtered_gantt['Finish']).dt.month >= month_num)
                    ]
                if selected_dept_gantt != "All":
                    filtered_gantt = filtered_gantt[filtered_gantt['Department'] == selected_dept_gantt]
                
                if not filtered_gantt.empty:
                    # Create Gantt chart with status-based colors
                    fig = px.timeline(
                        filtered_gantt, 
                        x_start="Start", 
                        x_end="Finish", 
                        y="Activity",
                        color="Status_Label",
                        color_discrete_map={
                            "Pending": "#EF4444",      # Red for pending
                            "In Progress": "#FFB81C",  # HELB Gold for in progress
                            "Completed": "#00843D"     # HELB Green for completed
                        },
                        hover_data=["Department", "Progress_Display", "Status"],
                        title="Activity Timeline - Status Based Colors"
                    )
                    
                    # Apply theme-aware styling
                    is_dark = st.session_state.theme == "dark"
                    fig.update_layout(
                        height=500, 
                        margin=dict(l=0, r=0, t=40, b=0),
                        plot_bgcolor='rgba(0,0,0,0)' if is_dark else 'rgba(255,255,255,0.8)',
                        paper_bgcolor='rgba(0,0,0,0)' if is_dark else 'rgba(255,255,255,0.8)',
                        font_color='#FFFFFF' if is_dark else '#1F2937',
                        legend=dict(
                            title="Status",
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="center",
                            x=0.5,
                            font_color='#FFFFFF' if is_dark else '#1F2937'
                        )
                    )
                    
                    # Update trace for better visibility
                    fig.update_traces(
                        marker=dict(
                            line=dict(width=1, color='rgba(0,0,0,0.2)')
                        )
                    )
                    
                    # Update axes
                    fig.update_xaxes(
                        gridcolor='rgba(255,255,255,0.1)' if is_dark else 'rgba(0,0,0,0.1)',
                        tickfont_color='#FFFFFF' if is_dark else '#1F2937'
                    )
                    fig.update_yaxes(
                        gridcolor='rgba(255,255,255,0.1)' if is_dark else 'rgba(0,0,0,0.1)',
                        tickfont_color='#FFFFFF' if is_dark else '#1F2937',
                        autorange="reversed"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Status Legend
                    st.markdown("""
                    <div style="display: flex; gap: 2rem; padding: 0.5rem; justify-content: center; background: rgba(0,0,0,0.05); border-radius: 8px; margin: 0.5rem 0;">
                        <div style="display: flex; align-items: center; gap: 0.5rem;">
                            <div style="width: 20px; height: 20px; background: #EF4444; border-radius: 4px;"></div>
                            <span style="font-size: 0.8rem;">🔴 Pending (0%)</span>
                        </div>
                        <div style="display: flex; align-items: center; gap: 0.5rem;">
                            <div style="width: 20px; height: 20px; background: #FFB81C; border-radius: 4px;"></div>
                            <span style="font-size: 0.8rem;">🟡 In Progress (1-99%)</span>
                        </div>
                        <div style="display: flex; align-items: center; gap: 0.5rem;">
                            <div style="width: 20px; height: 20px; background: #00843D; border-radius: 4px;"></div>
                            <span style="font-size: 0.8rem;">✅ Completed (100%)</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("#### Quarterly Activity Summary")
                    
                    # Calculate quarters with proper ordering
                    filtered_gantt['Quarter_Num'] = pd.to_datetime(filtered_gantt['Start']).dt.quarter
                    
                    # Map to proper quarter names in order
                    quarter_map = {
                        1: "Q3 (Jan-Mar)",
                        2: "Q4 (Apr-Jun)", 
                        3: "Q1 (Jul-Sep)",
                        4: "Q2 (Oct-Dec)"
                    }
                    filtered_gantt['Quarter_Name'] = filtered_gantt['Quarter_Num'].map(quarter_map)
                    
                    # Group by quarter
                    quarter_summary = filtered_gantt.groupby(['Quarter_Num', 'Quarter_Name']).size().reset_index(name='Count')
                    
                    # Sort by quarter number (1, 2, 3, 4)
                    quarter_summary = quarter_summary.sort_values('Quarter_Num')
                    
                    # Create bar chart with proper order
                    fig2 = px.bar(
                        quarter_summary, 
                        x='Quarter_Name', 
                        y='Count', 
                        title="Activities by Quarter (Sorted Q1→Q4)",
                        color='Count',
                        color_continuous_scale=["#FFB81C", "#00843D"],
                        text='Count'
                    )
                    
                    fig2.update_traces(textposition='outside')
                    
                    fig2.update_layout(
                        height=300,
                        plot_bgcolor='rgba(0,0,0,0)' if is_dark else 'rgba(255,255,255,0.8)',
                        paper_bgcolor='rgba(0,0,0,0)' if is_dark else 'rgba(255,255,255,0.8)',
                        font_color='#FFFFFF' if is_dark else '#1F2937',
                        xaxis=dict(
                            categoryarray=['Q3 (Jan-Mar)', 'Q4 (Apr-Jun)', 'Q1 (Jul-Sep)', 'Q2 (Oct-Dec)'],
                            categoryorder='array'
                        )
                    )
                    
                    fig2.update_xaxes(
                        gridcolor='rgba(255,255,255,0.1)' if is_dark else 'rgba(0,0,0,0.1)',
                        tickfont_color='#FFFFFF' if is_dark else '#1F2937'
                    )
                    fig2.update_yaxes(
                        gridcolor='rgba(255,255,255,0.1)' if is_dark else 'rgba(0,0,0,0.1)',
                        tickfont_color='#FFFFFF' if is_dark else '#1F2937'
                    )
                    
                    st.plotly_chart(fig2, use_container_width=True)
                    
                    # Additional breakdown by status per quarter
                    st.markdown("#### Quarterly Status Breakdown")
                    
                    status_by_quarter = filtered_gantt.groupby(['Quarter_Name', 'Status_Label']).size().reset_index(name='Count')
                    status_by_quarter['Quarter_Num'] = status_by_quarter['Quarter_Name'].map({v: k for k, v in quarter_map.items()})
                    status_by_quarter = status_by_quarter.sort_values('Quarter_Num')
                    
                    fig3 = px.bar(
                        status_by_quarter,
                        x='Quarter_Name',
                        y='Count',
                        color='Status_Label',
                        color_discrete_map={
                            "Pending": "#EF4444",
                            "In Progress": "#FFB81C",
                            "Completed": "#00843D"
                        },
                        title="Status Distribution by Quarter",
                        barmode='stack',
                        text='Count'
                    )
                    
                    fig3.update_traces(textposition='inside')
                    
                    fig3.update_layout(
                        height=350,
                        plot_bgcolor='rgba(0,0,0,0)' if is_dark else 'rgba(255,255,255,0.8)',
                        paper_bgcolor='rgba(0,0,0,0)' if is_dark else 'rgba(255,255,255,0.8)',
                        font_color='#FFFFFF' if is_dark else '#1F2937',
                        xaxis=dict(
                            categoryarray=['Q3 (Jan-Mar)', 'Q4 (Apr-Jun)', 'Q1 (Jul-Sep)', 'Q2 (Oct-Dec)'],
                            categoryorder='array'
                        ),
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="center",
                            x=0.5,
                            font_color='#FFFFFF' if is_dark else '#1F2937'
                        )
                    )
                    
                    fig3.update_xaxes(
                        gridcolor='rgba(255,255,255,0.1)' if is_dark else 'rgba(0,0,0,0.1)',
                        tickfont_color='#FFFFFF' if is_dark else '#1F2937'
                    )
                    fig3.update_yaxes(
                        gridcolor='rgba(255,255,255,0.1)' if is_dark else 'rgba(0,0,0,0.1)',
                        tickfont_color='#FFFFFF' if is_dark else '#1F2937'
                    )
                    
                    st.plotly_chart(fig3, use_container_width=True)
                    
                else:
                    st.info("No activities found for the selected filters")
            else:
                st.info("No activities with start and end dates found. Please add start and end dates to activities.")
        else:
            st.info("No work plan activities found")
    
    with tab_predictive:
        st.markdown("### 🔮 Predictive Analytics")
        st.markdown("AI-powered predictions for project completion and risk assessment")
        
        if filtered_plans:
            df_predict = pd.DataFrame(filtered_plans)
            df_predict['created_at'] = pd.to_datetime(df_predict['created_at'])
            df_predict['progress_percent'] = pd.to_numeric(df_predict['progress_percent'], errors='coerce').fillna(0)
            df_predict['due_date'] = pd.to_datetime(df_predict['due_date'])
            
            st.markdown("#### 📈 Completion Trend Prediction")
            predictions, future_days, r2 = predict_completion_trend(df_predict)
            
            if predictions is not None:
                col_pred1, col_pred2, col_pred3 = st.columns(3)
                with col_pred1:
                    st.metric("30-Day Prediction", f"{max(0, min(100, predictions[0])):.0f}%", 
                             delta=f"{predictions[0] - df_predict['progress_percent'].iloc[-1]:.0f}%")
                with col_pred2:
                    st.metric("60-Day Prediction", f"{max(0, min(100, predictions[1])):.0f}%",
                             delta=f"{predictions[1] - df_predict['progress_percent'].iloc[-1]:.0f}%")
                with col_pred3:
                    st.metric("90-Day Prediction", f"{max(0, min(100, predictions[2])):.0f}%",
                             delta=f"{predictions[2] - df_predict['progress_percent'].iloc[-1]:.0f}%")
                st.caption(f"Model confidence (R² score): {r2:.2f}")
                
                hist_data = df_predict[['created_at', 'progress_percent']].dropna()
                if len(hist_data) > 1:
                    fig_pred = px.line(hist_data, x='created_at', y='progress_percent', 
                                       title="Historical Progress Trend", markers=True)
                    fig_pred.update_layout(yaxis_title="Progress %", xaxis_title="Date")
                    st.plotly_chart(fig_pred, use_container_width=True)
            else:
                st.info("Need at least 3 data points for prediction. Continue updating progress to enable predictions.")
            
            st.markdown("#### ⚠️ Risk Assessment")
            st.markdown("Activities identified as at-risk based on progress vs. timeline")
            
            today = datetime.now().date()
            risk_data = []
            for plan in filtered_plans:
                due_date = datetime.strptime(plan["due_date"], "%Y-%m-%d").date()
                days_left = (due_date - today).days
                start_date = datetime.strptime(plan.get("start_date", plan["due_date"]), "%Y-%m-%d").date() if plan.get("start_date") else due_date - timedelta(days=90)
                total_days = (due_date - start_date).days
                risk_score = calculate_risk_score(plan.get("progress_percent", 0), days_left, total_days)
                
                if risk_score >= 60:
                    risk_data.append({
                        "Activity": plan["planned_activity"][:60] + "...",
                        "Department": plan.get("department_name", "Unknown"),
                        "Progress": f"{plan.get('progress_percent', 0)}%",
                        "Days Left": days_left,
                        "Risk Level": "High" if risk_score >= 80 else "Medium",
                        "Risk Score": risk_score
                    })
            
            if risk_data:
                df_risk = pd.DataFrame(risk_data)
                df_risk = df_risk.sort_values('Risk Score', ascending=False)
                
                for _, row in df_risk.head(10).iterrows():
                    risk_color = "#dc2626" if row["Risk Level"] == "High" else "#f59e0b"
                    st.markdown(f"""
                    <div style='background-color: {risk_color}20; border-left: 4px solid {risk_color}; padding: 0.75rem; margin-bottom: 0.5rem; border-radius: 8px;'>
                        <strong>{'🔴' if row['Risk Level'] == 'High' else '🟡'} {row['Risk Level']} Risk:</strong> {row['Activity']}<br>
                        <small>Department: {row['Department']} | Progress: {row['Progress']} | Days Left: {row['Days Left']}</small>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.caption(f"Found {len(risk_data)} at-risk activities requiring attention")
            else:
                st.success("✅ No high-risk activities found! All activities are on track.")
        else:
            st.info("No data available for predictive analytics")
    
    with tab_expiring:
        st.markdown("### ⚠️ Activities Expiring in 60 Days")
        
        if filtered_plans:
            today = datetime.now().date()
            expiring_activities = []
            for plan in filtered_plans:
                due_date = datetime.strptime(plan["due_date"], "%Y-%m-%d").date()
                days_left = (due_date - today).days
                if 0 <= days_left <= 60:
                    expiring_activities.append({
                        "Activity": plan['planned_activity'],
                        "Department": plan.get('department_name', 'Unknown'),
                        "Due Date": plan['due_date'],
                        "Days Left": days_left,
                        "Progress": f"{plan.get('progress_percent', 0)}%",
                        "Status": plan.get('status', 'Pending')
                    })
            
            if expiring_activities:
                df_expiring = pd.DataFrame(expiring_activities)
                df_expiring = df_expiring.sort_values('Days Left')
                
                for _, row in df_expiring.iterrows():
                    if row['Days Left'] <= 14:
                        st.markdown(f"""
                        <div style='background-color: #7f1a1a; border-left: 4px solid #ef4444; padding: 0.75rem; margin-bottom: 0.5rem; border-radius: 8px;'>
                            <strong>🔴 URGENT:</strong> {row['Activity']}<br>
                            <small>Department: {row['Department']} | Due: {row['Due Date']} | {row['Days Left']} days left | Progress: {row['Progress']}</small>
                        </div>
                        """, unsafe_allow_html=True)
                    elif row['Days Left'] <= 30:
                        st.markdown(f"""
                        <div style='background-color: #92400e; border-left: 4px solid #f59e0b; padding: 0.75rem; margin-bottom: 0.5rem; border-radius: 8px;'>
                            <strong>🟡 WARNING:</strong> {row['Activity']}<br>
                            <small>Department: {row['Department']} | Due: {row['Due Date']} | {row['Days Left']} days left | Progress: {row['Progress']}</small>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style='background-color: #1e3a5f; border-left: 4px solid #3b82f6; padding: 0.75rem; margin-bottom: 0.5rem; border-radius: 8px;'>
                            <strong>🔵 APPROACHING:</strong> {row['Activity']}<br>
                            <small>Department: {row['Department']} | Due: {row['Due Date']} | {row['Days Left']} days left | Progress: {row['Progress']}</small>
                        </div>
                        """, unsafe_allow_html=True)
                
                st.metric("Total Activities Expiring in 60 Days", len(expiring_activities))
            else:
                st.success("✅ No activities expiring in the next 60 days!")
        else:
            st.info("No work plan activities found")
    
    with tab_bulk:
        st.markdown("### 📤 Bulk Upload Work Plan Activities")
        st.markdown("Download the template, fill it with your activities, and upload back to the system.")
        
        col_info, col_download = st.columns([2, 1])
        with col_info:
            st.info("""
            **Instructions:**
            1. Download the Excel template below
            2. Fill in your work plan activities (do not change column names)
            3. Save as Excel file (.xlsx)
            4. Upload the file using the upload button below
            
            **Note for Strategy/Admin users:** You can select which department to assign these activities to.
            """)
        with col_download:
            template_df = generate_work_plan_template()
            template_buffer = io.BytesIO()
            with pd.ExcelWriter(template_buffer, engine='openpyxl') as writer:
                template_df.to_excel(writer, index=False, sheet_name='Work Plan Template')
            template_buffer.seek(0)
            st.download_button(
                label="📥 Download Excel Template",
                data=template_buffer,
                file_name="helb_work_plan_template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        st.markdown("---")
        st.markdown("#### Upload Filled Template")
        
        selected_upload_dept = None
        selected_dept_name = None
        
        if st.session_state.user_role in ["admin", "management"]:
            departments_list = get_cached_departments()
            dept_options = {d["name"]: d["id"] for d in departments_list}
            dept_names = ["Same as my department"] + sorted(list(dept_options.keys()))
            
            selected_dept_option = st.selectbox(
                "📋 Select Department for these activities", 
                dept_names,
                help="Choose which department these work plan activities belong to"
            )
            
            if selected_dept_option != "Same as my department":
                selected_dept_name = selected_dept_option
                selected_upload_dept = dept_options.get(selected_dept_option)
                dept_details = get_department_by_id(selected_upload_dept)
                if dept_details:
                    directorate_name = dept_details.get("directorate_name", "Unknown")
                    st.success(f"✅ Activities will be assigned to: **{selected_dept_name}**")
                    st.caption(f"🏛️ This maps to directorate: **{directorate_name}**")
            else:
                selected_upload_dept = st.session_state.user_dept
                selected_dept_name = st.session_state.user_dept_name
                dept_details = get_department_by_id(selected_upload_dept)
                if dept_details:
                    directorate_name = dept_details.get("directorate_name", "Unknown")
                    st.info(f"📌 Activities will be assigned to your department: **{selected_dept_name}**")
                    st.caption(f"🏛️ This maps to directorate: **{directorate_name}**")
        else:
            selected_upload_dept = st.session_state.user_dept
            selected_dept_name = st.session_state.user_dept_name
            dept_details = get_department_by_id(selected_upload_dept)
            if dept_details:
                directorate_name = dept_details.get("directorate_name", "Unknown")
                st.info(f"📌 Activities will be assigned to: **{selected_dept_name}**")
                st.caption(f"🏛️ This maps to directorate: **{directorate_name}**")
        
        st.markdown("---")
        
        uploaded_file = st.file_uploader("Choose Excel file", type=["xlsx", "xls"], key="bulk_upload")
        
        if uploaded_file is not None:
            try:
                df_upload = pd.read_excel(uploaded_file)
                st.success(f"✅ File loaded successfully! Found {len(df_upload)} rows.")
                
                st.markdown("**Preview of uploaded data:**")
                st.dataframe(df_upload.head(10), use_container_width=True)
                
                col_confirm1, col_confirm2 = st.columns([3, 1])
                with col_confirm2:
                    if st.button("🚀 Start Bulk Upload", use_container_width=True, type="primary"):
                        with st.spinner("Uploading work plan activities..."):
                            success_count, error_count, errors = bulk_upload_work_plans(
                                df_upload, 
                                selected_upload_dept,
                                selected_dept_name,
                                st.session_state.user_id
                            )
                            
                            if success_count > 0:
                                st.success(f"✅ Successfully uploaded {success_count} activities to {selected_dept_name}!")
                                st.balloons()
                                add_audit_log("BULK_UPLOAD", "work_plan", None, f"Bulk uploaded {success_count} activities to {selected_dept_name}")
                            if error_count > 0:
                                st.error(f"❌ Failed to upload {error_count} activities")
                                with st.expander("View Errors"):
                                    for err in errors[:20]:
                                        st.write(f"- {err}")
                            
                            if success_count > 0:
                                st.rerun()
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
    
    with tab_dashboard:
        if filtered_plans:
            df = pd.DataFrame(filtered_plans)
            df['calculated_progress'] = df.apply(lambda x: calculate_progress_from_actual(x.get('annual_target', '0'), x.get('actual_achievement', 0)), axis=1)
            df['exceeded'] = df.apply(lambda x: is_target_exceeded(x.get('actual_achievement', 0), x.get('annual_target', '0')), axis=1)
            
            total_activities = len(df)
            completed_count = len(df[df['calculated_progress'] >= 100])
            in_progress_count = len(df[(df['calculated_progress'] > 0) & (df['calculated_progress'] < 100)])
            not_started_count = len(df[df['calculated_progress'] == 0])
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-label'>📋 TOTAL ACTIVITIES</div>
                    <div class='kpi-value'>{total_activities}</div>
                    <div class='kpi-sub'>All Activities</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                completed_rate = (completed_count/total_activities*100) if total_activities > 0 else 0
                st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-label'>✅ COMPLETED</div>
                    <div class='kpi-value'>{completed_count} ({completed_rate:.0f}%)</div>
                    <div class='progress-bar'><div class='progress-fill' style='width:{completed_rate}%;'></div></div>
                    <div class='kpi-sub'>Activities Completed</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                in_progress_rate = (in_progress_count/total_activities*100) if total_activities > 0 else 0
                st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-label'>🟡 IN PROGRESS</div>
                    <div class='kpi-value'>{in_progress_count} ({in_progress_rate:.0f}%)</div>
                    <div class='progress-bar'><div class='progress-fill' style='width:{in_progress_rate}%; background: {HELB_GOLD};'></div></div>
                    <div class='kpi-sub'>In Progress</div>
                </div>
                """, unsafe_allow_html=True)
            with col4:
                not_started_rate = (not_started_count/total_activities*100) if total_activities > 0 else 0
                st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-label'>🔴 NOT STARTED</div>
                    <div class='kpi-value'>{not_started_count} ({not_started_rate:.0f}%)</div>
                    <div class='progress-bar'><div class='progress-fill' style='width:{not_started_rate}%; background: #dc2626;'></div></div>
                    <div class='kpi-sub'>Not Started</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            col_budget, col_exceeded = st.columns(2)
            with col_budget:
                total_budget = df['budget_allocation'].fillna(0).sum()
                st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-label'>💰 TOTAL BUDGET</div>
                    <div class='kpi-value'>KES {total_budget/1e6:.1f}M</div>
                    <div class='kpi-sub'>Total Budget Allocation</div>
                </div>
                """, unsafe_allow_html=True)
            with col_exceeded:
                exceeded_count = len(df[df['exceeded'] == True])
                st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-label'>🏆 TARGETS EXCEEDED</div>
                    <div class='kpi-value'>{exceeded_count}</div>
                    <div class='kpi-sub'>Exceeded Targets</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            col_chart1, col_chart2 = st.columns(2)
            with col_chart1:
                st.markdown("#### Status Distribution")
                # Create status groups with correct colors
                df['status_group'] = df['calculated_progress'].apply(
                    lambda x: 'Completed' if x >= 100 else ('In Progress' if x > 0 else 'Not Started')
                )
                status_counts = df['status_group'].value_counts().reset_index()
                status_counts.columns = ['Status', 'Count']
                
                # Define correct colors: Red for Not Started, Gold for In Progress, Green for Completed
                color_map = {
                    'Completed': '#00843D',      # HELB Green
                    'In Progress': '#FFB81C',    # HELB Gold
                    'Not Started': '#EF4444'     # Red
                }
                
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
                pillar_progress = df.groupby('strategic_pillar')['calculated_progress'].mean().reset_index()
                pillar_progress.columns = ['Pillar', 'Progress %']
                pillar_progress = pillar_progress.sort_values('Progress %', ascending=True)
                fig = px.bar(pillar_progress, y='Pillar', x='Progress %', orientation='h',
                            color='Progress %', color_continuous_scale=["#FFB81C", "#00843D"],
                            text='Progress %')
                fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                fig.update_layout(height=350, xaxis_title="Progress %", yaxis_title="", margin=dict(l=20, r=20, t=30, b=20))
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("#### Department Performance")
            dept_progress = df.groupby('department_name')['calculated_progress'].mean().reset_index()
            dept_progress.columns = ['Department', 'Progress %']
            dept_progress = dept_progress.sort_values('Progress %', ascending=True)
            fig = px.bar(dept_progress, y='Department', x='Progress %', orientation='h',
                        color='Progress %', color_continuous_scale=["#FFB81C", "#00843D"],
                        text='Progress %')
            fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig.update_layout(height=max(400, len(dept_progress) * 30), xaxis_title="Progress %", yaxis_title="", margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig, use_container_width=True)
            
            col_chart3, col_chart4 = st.columns(2)
            with col_chart3:
                st.markdown("#### Activity Category Breakdown")
                category_stats = df['activity_category'].value_counts().reset_index()
                category_stats.columns = ['Category', 'Count']
                fig = px.bar(category_stats, x='Category', y='Count',
                            color='Count', color_discrete_sequence=['#00843D'],
                            text='Count')
                fig.update_traces(textposition='outside')
                fig.update_layout(height=350, margin=dict(l=20, r=20, t=30, b=20))
                st.plotly_chart(fig, use_container_width=True)
            
            with col_chart4:
                st.markdown("#### Quarterly Performance Trend")
                if 'quarter' in df.columns:
                    quarterly_data = df.groupby('quarter').agg({
                        'id': 'count',
                        'calculated_progress': 'mean'
                    }).reset_index()
                    quarterly_data.columns = ['Quarter', 'Activities', 'Avg Progress %']
                    quarter_order = ["Q1 (Jul-Sep)", "Q2 (Oct-Dec)", "Q3 (Jan-Mar)", "Q4 (Apr-Jun)"]
                    quarterly_data['Quarter'] = pd.Categorical(quarterly_data['Quarter'], categories=quarter_order, ordered=True)
                    quarterly_data = quarterly_data.sort_values('Quarter')
                    
                    fig = go.Figure()
                    fig.add_trace(go.Bar(x=quarterly_data['Quarter'], y=quarterly_data['Activities'],
                                         name='Activities', marker_color='#00843D',
                                         text=quarterly_data['Activities'], textposition='outside'))
                    fig.add_trace(go.Scatter(x=quarterly_data['Quarter'], y=quarterly_data['Avg Progress %'],
                                             name='Avg Progress %', marker_color='#FFB81C',
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
            
            df['days_left'] = (pd.to_datetime(df['due_date']) - pd.Timestamp.now()).dt.days
            overdue_df = df[(df['days_left'] < 0) & (df['calculated_progress'] < 100)]
            urgent_df = df[(df['days_left'] >= 0) & (df['days_left'] <= 14) & (df['calculated_progress'] < 80)]
            
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
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download Work Plan Data", csv, f"work_plan_data_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")
        else:
            st.info("No data available for the selected period.")
# ============================================
# DASHBOARD
# ============================================
elif st.session_state.active_menu == "📊 Dashboard":
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
            total_activities = len(filtered_work_df)
            completed_count = len(filtered_work_df[filtered_work_df['calculated_progress'] >= 100])
            in_progress_count = len(filtered_work_df[(filtered_work_df['calculated_progress'] > 0) & (filtered_work_df['calculated_progress'] < 100)])
            not_started_count = len(filtered_work_df[filtered_work_df['calculated_progress'] == 0])
            
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-label'>📋 TOTAL</div>
                    <div class='kpi-value'>{total_activities}</div>
                    <div class='kpi-sub'>Activities</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                completed_rate = (completed_count/total_activities*100) if total_activities > 0 else 0
                st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-label'>✅ COMPLETED</div>
                    <div class='kpi-value'>{completed_count} ({completed_rate:.0f}%)</div>
                    <div class='progress-bar'><div class='progress-fill' style='width:{completed_rate}%;'></div></div>
                    <div class='kpi-sub'>Completed</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                in_progress_rate = (in_progress_count/total_activities*100) if total_activities > 0 else 0
                st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-label'>🟡 IN PROGRESS</div>
                    <div class='kpi-value'>{in_progress_count} ({in_progress_rate:.0f}%)</div>
                    <div class='progress-bar'><div class='progress-fill' style='width:{in_progress_rate}%; background: {HELB_GOLD};'></div></div>
                    <div class='kpi-sub'>In Progress</div>
                </div>
                """, unsafe_allow_html=True)
            with col4:
                not_started_rate = (not_started_count/total_activities*100) if total_activities > 0 else 0
                st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-label'>🔴 NOT STARTED</div>
                    <div class='kpi-value'>{not_started_count} ({not_started_rate:.0f}%)</div>
                    <div class='progress-bar'><div class='progress-fill' style='width:{not_started_rate}%; background: #dc2626;'></div></div>
                    <div class='kpi-sub'>Not Started</div>
                </div>
                """, unsafe_allow_html=True)
            with col5:
                avg_progress_val = filtered_work_df['calculated_progress'].mean()
                st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-label'>📈 AVG PROGRESS</div>
                    <div class='kpi-value'>{avg_progress_val:.0f}%</div>
                    <div class='kpi-sub'>Overall Progress</div>
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
            col1, col2, col3, col4, col5 = st.columns(5)
            
            total_value = filtered_contracts_df['contract_value'].sum()
            total_spent = filtered_contracts_df['amount_spent_to_date'].sum()
            utilization = (total_spent/total_value*100) if total_value > 0 else 0
            active_count = len(filtered_contracts_df[filtered_contracts_df['status'] == 'active'])
            expiring_count = len(filtered_contracts_df[filtered_contracts_df['status'] == 'expiring_soon'])
            expired_count = len(filtered_contracts_df[filtered_contracts_df['status'] == 'expired'])
            
            with col1:
                st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-label'>💰 TOTAL VALUE</div>
                    <div class='kpi-value'>KES {total_value/1e6:.1f}M</div>
                    <div class='kpi-sub'>Contract Value</div>
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
                    <div class='kpi-value'>{active_count}</div>
                    <div class='kpi-sub'>Active Contracts</div>
                </div>
                """, unsafe_allow_html=True)
            with col4:
                st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-label'>⚠️ EXPIRING SOON</div>
                    <div class='kpi-value'>{expiring_count}</div>
                    <div class='kpi-sub'>Within 30 days</div>
                </div>
                """, unsafe_allow_html=True)
            with col5:
                st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-label'>🔴 EXPIRED</div>
                    <div class='kpi-value'>{expired_count}</div>
                    <div class='kpi-sub'>Expired Contracts</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Department filter for contracts
            if st.session_state.user_role in ["admin", "management"]:
                depts_in_contracts = sorted([c.get('department_name', 'Unassigned') for c in filtered_contracts_df.to_dict('records')])
                unique_depts = list(set(depts_in_contracts))
                if unique_depts:
                    selected_dept_filter_contracts = st.multiselect("Filter by Department", unique_depts, default=[])
                    if selected_dept_filter_contracts:
                        filtered_contracts_df = filtered_contracts_df[filtered_contracts_df['department_name'].isin(selected_dept_filter_contracts)]
            
            st.markdown("#### 📄 Contracts List")
            
            for _, contract in filtered_contracts_df.iterrows():
                end_date = datetime.strptime(contract["end_date"], "%Y-%m-%d").date()
                days_left = (end_date - datetime.now().date()).days
                
                if days_left > 30:
                    status_class = "active"
                    status_text = "Active"
                elif days_left > 0:
                    status_class = "expiring"
                    status_text = f"Expiring in {days_left} days"
                else:
                    status_class = "expired"
                    status_text = "Expired"
                
                expander_title = f"📄 {contract['contract_title']} - {contract['vendor_name']} ({status_text})"
                if contract.get('department_name'):
                    expander_title += f" | 🏢 {contract['department_name']}"
                
                with st.expander(expander_title, expanded=False):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Contract Title:** {contract['contract_title']}")
                        st.markdown(f"**Vendor:** {contract['vendor_name']}")
                        st.markdown(f"**Department:** {contract.get('department_name', 'Unassigned')}")
                        st.markdown(f"**Duration:** {contract.get('contract_duration', 'N/A')}")
                        st.markdown(f"**Start Date:** {contract['start_date']}")
                        st.markdown(f"**End Date:** {contract['end_date']}")
                        st.markdown(f"**Signed Date:** {contract.get('signed_date', 'N/A')}")
                    with col2:
                        st.markdown(f"**Contract Value:** KES {contract.get('contract_value', 0):,.0f}")
                        st.markdown(f"**Amount Spent:** KES {contract.get('amount_spent_to_date', 0):,.0f}")
                        st.markdown(f"**Utilization:** {contract.get('utilization_rate', 0):.1f}%")
                        st.markdown(f"**Payment Terms:** {contract.get('payment_terms', 'N/A')}")
                        st.markdown(f"**Compliance:** {contract.get('compliance_status', 'N/A')}")
                        st.markdown(f"**Vendor Rating:** ⭐ {contract.get('vendor_performance', 0)}/5")
                    
                    st.markdown("---")
                    if contract.get('contract_url'):
                        st.markdown(f"📄 **Contract Document:** [View Document]({contract['contract_url']})", unsafe_allow_html=True)
                    if contract.get('breach_notes'):
                        st.warning(f"⚠️ **Breach Notes:** {contract['breach_notes']}")
                    if contract.get('budget_alert'):
                        st.error("⚠️ **Budget Alert:** Utilization has exceeded 80%!")
            
            pdf_buffer_contracts = generate_contracts_pdf_report(filtered_contracts_df, f"HELB Contracts Report - {datetime.now().strftime('%Y-%m-%d')}")
            st.download_button(
                label="📄 Export Contracts to PDF",
                data=pdf_buffer_contracts,
                file_name=f"contracts_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf",
                key="export_contracts_pdf"
            )
        else:
            st.info("No contracts found for the selected filters.")
    
    with tab_policies:
        if not filtered_policies_df.empty:
            col1, col2, col3, col4 = st.columns(4)
            
            total_policies = len(filtered_policies_df)
            active_policies = len(filtered_policies_df[filtered_policies_df['status'] == 'active'])
            expiring_soon = len(filtered_policies_df[filtered_policies_df['status'] == 'expiring_soon'])
            expired_policies = len(filtered_policies_df[filtered_policies_df['status'] == 'expired'])
            
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
            st.markdown("#### 📜 Policies List")
            
            for _, policy in filtered_policies_df.iterrows():
                expiry = datetime.strptime(policy["expiry_date"], "%Y-%m-%d").date()
                days_left = (expiry - datetime.now().date()).days
                
                if days_left > 90:
                    status_class = "active"
                    status_text = "Active"
                elif days_left > 0:
                    status_class = "expiring"
                    status_text = f"Expires in {days_left} days"
                else:
                    status_class = "expired"
                    status_text = "Expired"
                
                expander_title = f"📜 {policy['policy_name']} (v{policy.get('version', '1.0')}) - {status_text}"
                
                with st.expander(expander_title, expanded=False):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Policy Name:** {policy['policy_name']}")
                        st.markdown(f"**Category:** {policy.get('category', 'Uncategorized')}")
                        st.markdown(f"**Version:** {policy.get('version', 'v1.0')}")
                        st.markdown(f"**Scope:** {policy.get('policy_scope', 'Not specified')}")
                        st.markdown(f"**Affected Entities:** {policy.get('affected_entities', 'N/A')}")
                        st.markdown(f"**Policy Owner:** {policy.get('policy_owner', 'Not assigned')}")
                    with col2:
                        st.markdown(f"**Effective Date:** {policy.get('effective_date', 'N/A')}")
                        st.markdown(f"**Expiry Date:** {policy['expiry_date']}")
                        st.markdown(f"**Next Review:** {policy.get('review_date', 'Not scheduled')}")
                        st.markdown(f"**Status:** {status_text}")
                        if policy.get('requires_acknowledgment'):
                            st.info("📋 Requires Staff Acknowledgment")
                        if policy.get('requires_sensitization'):
                            st.info("🎓 Requires Sensitization")
                    
                    st.markdown("---")
                    if policy.get('policy_url'):
                        st.markdown(f"📄 **Policy Document:** [View Document]({policy['policy_url']})", unsafe_allow_html=True)
                    if policy.get('change_log'):
                        st.markdown(f"**Change Log:** {policy['change_log']}")
            
            pdf_buffer_policies = generate_policies_pdf_report(filtered_policies_df, f"HELB Policies Report - {datetime.now().strftime('%Y-%m-%d')}")
            st.download_button(
                label="📄 Export Policies to PDF",
                data=pdf_buffer_policies,
                file_name=f"policies_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf",
                key="export_policies_pdf"
            )
        else:
            st.info("No policies found for the selected filters.")
    
    st.success(f"👋 Welcome, {st.session_state.user_fullname}!")

# ============================================
# CONTRACT MANAGEMENT - UPDATED WITH FULL ADMIN EDITING
# ============================================
elif st.session_state.active_menu == "📄 Contracts":
    st.subheader("Contract Management")
    
    # Show department info for current user
    if st.session_state.user_role not in ["admin", "management"]:
        dept_name = get_department_name(st.session_state.user_dept)
        st.info(f"📌 Viewing contracts for: **{dept_name}**")
    
    tab_overview, tab_active, tab_expiring, tab_add, tab_update, tab_admin_edit = st.tabs([
        "📊 Overview & Analytics", 
        "✅ Active Contracts", 
        "⚠️ Expiring & Expired", 
        "➕ New Contract", 
        "✏️ Update Contract",
        "🔧 Admin Full Edit"
    ])
    
    with tab_overview:
        contracts = get_cached_contracts(st.session_state.user_role, st.session_state.user_dept)
        if contracts:
            df_contracts = pd.DataFrame(contracts)
            
            # Handle missing department_name column
            if 'department_name' not in df_contracts.columns:
                df_contracts['department_name'] = 'Unassigned'
            
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
            
            st.markdown("---")
            
            # Department filter for contracts
            if st.session_state.user_role in ["admin", "management"]:
                depts_in_contracts = sorted([c.get('department_name', 'Unassigned') for c in df_contracts.to_dict('records')])
                unique_depts = list(set(depts_in_contracts))
                if unique_depts:
                    selected_dept_filter_contracts = st.multiselect("Filter by Department", unique_depts, default=[])
                    if selected_dept_filter_contracts:
                        df_contracts = df_contracts[df_contracts['department_name'].isin(selected_dept_filter_contracts)]
            
            st.markdown("#### All Contracts")
            
            for _, contract in df_contracts.iterrows():
                end_date = datetime.strptime(contract["end_date"], "%Y-%m-%d").date()
                days_left = (end_date - datetime.now().date()).days
                
                if days_left > 30:
                    status_text = "Active"
                elif days_left > 0:
                    status_text = f"Expiring in {days_left} days"
                else:
                    status_text = "Expired"
                
                expander_title = f"📄 {contract['contract_title']} - {contract['vendor_name']} ({status_text})"
                if contract.get('department_name'):
                    expander_title += f" | 🏢 {contract['department_name']}"
                
                with st.expander(expander_title, expanded=False):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Contract Title:** {contract['contract_title']}")
                        st.markdown(f"**Vendor:** {contract['vendor_name']}")
                        st.markdown(f"**Department:** {contract.get('department_name', 'Unassigned')}")
                        st.markdown(f"**Duration:** {contract.get('contract_duration', 'N/A')}")
                        st.markdown(f"**Start Date:** {contract['start_date']}")
                        st.markdown(f"**End Date:** {contract['end_date']}")
                        st.markdown(f"**Signed Date:** {contract.get('signed_date', 'N/A')}")
                    with col2:
                        st.markdown(f"**Contract Value:** KES {contract.get('contract_value', 0):,.0f}")
                        st.markdown(f"**Amount Spent:** KES {contract.get('amount_spent_to_date', 0):,.0f}")
                        st.markdown(f"**Utilization:** {contract.get('utilization_rate', 0):.1f}%")
                        st.markdown(f"**Payment Terms:** {contract.get('payment_terms', 'N/A')}")
                        st.markdown(f"**Compliance:** {contract.get('compliance_status', 'N/A')}")
                        st.markdown(f"**Vendor Rating:** ⭐ {contract.get('vendor_performance', 0)}/5")
                    
                    st.markdown("---")
                    if contract.get('contract_url'):
                        st.markdown(f"📄 **Contract Document:** [View Document]({contract['contract_url']})", unsafe_allow_html=True)
                    if contract.get('breach_notes'):
                        st.warning(f"⚠️ **Breach Notes:** {contract['breach_notes']}")
                    
                    # Show multi-year details if applicable
                    if contract.get('is_multi_year'):
                        st.markdown("#### 📅 Multi-Year Breakdown")
                        years = get_contract_years(contract['id'])
                        if years:
                            year_data = []
                            for y in years:
                                year_data.append({
                                    "Year": f"Year {y['year_number']}",
                                    "Start": y.get('year_start_date', 'N/A'),
                                    "End": y.get('year_end_date', 'N/A'),
                                    "Value": f"KES {y.get('annual_value', 0):,.0f}",
                                    "Spent": f"KES {y.get('amount_spent_to_date', 0):,.0f}",
                                    "Status": y.get('status', 'active')
                                })
                            df_years = pd.DataFrame(year_data)
                            st.dataframe(df_years, use_container_width=True, hide_index=True)
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
                    
                    expander_title = f"📄 {contract['contract_title']} - {contract['vendor_name']} (Active, {days_left} days left)"
                    if contract.get('department_name'):
                        expander_title += f" | 🏢 {contract['department_name']}"
                    
                    with st.expander(expander_title, expanded=False):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**Contract Title:** {contract['contract_title']}")
                            st.markdown(f"**Vendor:** {contract['vendor_name']}")
                            st.markdown(f"**Department:** {contract.get('department_name', 'Unassigned')}")
                            st.markdown(f"**Duration:** {contract.get('contract_duration', 'N/A')}")
                            st.markdown(f"**Start Date:** {contract['start_date']}")
                            st.markdown(f"**End Date:** {contract['end_date']}")
                        with col2:
                            st.markdown(f"**Contract Value:** KES {contract.get('contract_value', 0):,.0f}")
                            st.markdown(f"**Amount Spent:** KES {contract.get('amount_spent_to_date', 0):,.0f}")
                            st.markdown(f"**Payment Terms:** {contract.get('payment_terms', 'N/A')}")
                            st.markdown(f"**Compliance:** {contract.get('compliance_status', 'N/A')}")
                        
                        st.markdown("---")
                        if contract.get('contract_url'):
                            st.markdown(f"📄 **Contract Document:** [View Document]({contract['contract_url']})", unsafe_allow_html=True)
                        
                        if contract.get('is_multi_year'):
                            st.markdown("#### 📅 Multi-Year Breakdown")
                            years = get_contract_years(contract['id'])
                            if years:
                                year_data = []
                                for y in years:
                                    year_data.append({
                                        "Year": f"Year {y['year_number']}",
                                        "Value": f"KES {y.get('annual_value', 0):,.0f}",
                                        "Spent": f"KES {y.get('amount_spent_to_date', 0):,.0f}",
                                        "Status": y.get('status', 'active')
                                    })
                                df_years = pd.DataFrame(year_data)
                                st.dataframe(df_years, use_container_width=True, hide_index=True)
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
                    status_text = f"Expires in {days_left} days" if days_left > 0 else "Expired"
                    
                    expander_title = f"⚠️ {contract['contract_title']} - {contract['vendor_name']} ({status_text})"
                    if contract.get('department_name'):
                        expander_title += f" | 🏢 {contract['department_name']}"
                    
                    with st.expander(expander_title, expanded=False):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**Contract Title:** {contract['contract_title']}")
                            st.markdown(f"**Vendor:** {contract['vendor_name']}")
                            st.markdown(f"**Department:** {contract.get('department_name', 'Unassigned')}")
                            st.markdown(f"**Duration:** {contract.get('contract_duration', 'N/A')}")
                            st.markdown(f"**Start Date:** {contract['start_date']}")
                            st.markdown(f"**End Date:** {contract['end_date']}")
                        with col2:
                            st.markdown(f"**Contract Value:** KES {contract.get('contract_value', 0):,.0f}")
                            st.markdown(f"**Amount Spent:** KES {contract.get('amount_spent_to_date', 0):,.0f}")
                            st.markdown(f"**Payment Terms:** {contract.get('payment_terms', 'N/A')}")
                            st.markdown(f"**Compliance:** {contract.get('compliance_status', 'N/A')}")
                        
                        st.markdown("---")
                        if contract.get('contract_url'):
                            st.markdown(f"📄 **Contract Document:** [View Document]({contract['contract_url']})", unsafe_allow_html=True)
                        if contract.get('breach_notes'):
                            st.warning(f"⚠️ **Notes:** {contract['breach_notes']}")
            else:
                st.success("No expiring or expired contracts!")
        else:
            st.info("No contracts found.")
    
    with tab_add:
        st.markdown("### Add New Contract")
        
        contract_type = st.radio("Contract Type", ["Single Year Contract", "Multi-Year Contract"], horizontal=True)
        
        # Use session state to store year values
        if "contract_year_values" not in st.session_state:
            st.session_state.contract_year_values = {}
        
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
                payment_terms = st.selectbox("Payment Terms*", ["Monthly", "Quarterly", "Bi-annually", "Annually", "Milestone-based", "One-time"])
                auto_renewal = st.checkbox("Auto-renewal")
            
            st.markdown("---")
            
            # Multi-Year Contract Section - USING SESSION STATE
            if contract_type == "Multi-Year Contract":
                st.markdown("#### 📅 Multi-Year Contract Breakdown")
                st.info("Please enter the annual value for each year of the contract. The total contract value will be calculated automatically.")
                
                # Calculate number of years from duration
                num_years = 1
                if "2 years" in contract_duration:
                    num_years = 2
                elif "3 years" in contract_duration:
                    num_years = 3
                elif "4 years" in contract_duration:
                    num_years = 4
                elif "5 years" in contract_duration:
                    num_years = 5
                
                st.markdown(f"**📆 Contract Duration: {num_years} year(s)**")
                st.markdown("---")
                
                # Initialize session state for this contract
                contract_key = f"contract_{contract_title}_{start_date}"
                if contract_key not in st.session_state.contract_year_values:
                    st.session_state.contract_year_values[contract_key] = {}
                
                # Initialize year start/end dates
                year_start_dates = {}
                year_end_dates = {}
                
                # Create dynamic year inputs with UNIQUE KEYS using session state
                for year_num in range(1, num_years + 1):
                    st.markdown(f"**📆 Year {year_num}**")
                    col_y1, col_y2, col_y3 = st.columns(3)
                    
                    # Get current value from session state or default to 0
                    current_value = st.session_state.contract_year_values[contract_key].get(f"year_{year_num}_value", 0.0)
                    
                    # Calculate default dates for each year
                    if year_num == 1:
                        default_start = start_date
                    else:
                        default_start = start_date + relativedelta(years=year_num-1)
                    
                    if year_num == num_years:
                        default_end = end_date
                    else:
                        default_end = start_date + relativedelta(years=year_num)
                    
                    with col_y1:
                        year_value = st.number_input(
                            f"Annual Value - Year {year_num} (KES)*", 
                            min_value=0.0, 
                            step=10000.0, 
                            format="%.2f", 
                            value=current_value,
                            key=f"year_value_{year_num}_{contract_key}",
                            help=f"Enter the budget for Year {year_num}"
                        )
                        # Update session state
                        st.session_state.contract_year_values[contract_key][f"year_{year_num}_value"] = year_value
                    
                    with col_y2:
                        year_start = st.date_input(
                            f"Year {year_num} Start Date", 
                            value=default_start,
                            key=f"year_start_{year_num}_{contract_key}"
                        )
                        year_start_dates[year_num] = year_start
                    
                    with col_y3:
                        year_end = st.date_input(
                            f"Year {year_num} End Date", 
                            value=default_end,
                            key=f"year_end_{year_num}_{contract_key}"
                        )
                        year_end_dates[year_num] = year_end
                    
                    st.markdown("---")
                
                # Calculate total from session state values
                total_value = 0
                years_data = []
                for year_num in range(1, num_years + 1):
                    year_val = st.session_state.contract_year_values[contract_key].get(f"year_{year_num}_value", 0.0)
                    if year_val > 0:
                        total_value += year_val
                        
                        # Get start and end dates for this year
                        year_start = year_start_dates.get(year_num, start_date)
                        year_end = year_end_dates.get(year_num, end_date)
                        
                        years_data.append({
                            "year_number": year_num,
                            "year_start_date": year_start.isoformat() if year_start else start_date.isoformat(),
                            "year_end_date": year_end.isoformat() if year_end else end_date.isoformat(),
                            "annual_value": year_val,
                            "amount_spent_to_date": 0,
                            "status": "active"
                        })
                
                # Display total
                if total_value > 0:
                    st.success(f" **Total Contract Value: KES {total_value:,.2f}**")
                    st.info(f"📊 {len(years_data)} year(s) configured")
                    
                    # Show breakdown table
                    if years_data:
                        df_years_preview = pd.DataFrame([
                            {
                                "Year": f"Year {y['year_number']}",
                                "Annual Value": f"KES {y['annual_value']:,.2f}",
                                "Start": y['year_start_date'],
                                "End": y['year_end_date']
                            } for y in years_data
                        ])
                        st.dataframe(df_years_preview, use_container_width=True, hide_index=True)
                else:
                    st.warning("⚠️ Please add values for each year (greater than 0)")
                
                # Calculate payment schedule based on payment terms
                if total_value > 0 and payment_terms:
                    st.markdown("#### 💳 Payment Schedule")
                    
                    if payment_terms == "Monthly":
                        months_per_year = 12
                        payment_data = []
                        for y in years_data:
                            if y['annual_value'] > 0:
                                monthly = y['annual_value'] / months_per_year
                                payment_data.append({
                                    "Year": f"Year {y['year_number']}",
                                    "Monthly Payment": f"KES {monthly:,.2f}",
                                    "Annual Total": f"KES {y['annual_value']:,.2f}"
                                })
                        df_payment = pd.DataFrame(payment_data)
                        st.dataframe(df_payment, use_container_width=True, hide_index=True)
                        
                    elif payment_terms == "Quarterly":
                        quarters_per_year = 4
                        payment_data = []
                        for y in years_data:
                            if y['annual_value'] > 0:
                                quarterly = y['annual_value'] / quarters_per_year
                                payment_data.append({
                                    "Year": f"Year {y['year_number']}",
                                    "Quarterly Payment": f"KES {quarterly:,.2f}",
                                    "Annual Total": f"KES {y['annual_value']:,.2f}"
                                })
                        df_payment = pd.DataFrame(payment_data)
                        st.dataframe(df_payment, use_container_width=True, hide_index=True)
                        
                    elif payment_terms == "Bi-annually":
                        periods_per_year = 2
                        payment_data = []
                        for y in years_data:
                            if y['annual_value'] > 0:
                                bi_annual = y['annual_value'] / periods_per_year
                                payment_data.append({
                                    "Year": f"Year {y['year_number']}",
                                    "Bi-Annual Payment": f"KES {bi_annual:,.2f}",
                                    "Annual Total": f"KES {y['annual_value']:,.2f}"
                                })
                        df_payment = pd.DataFrame(payment_data)
                        st.dataframe(df_payment, use_container_width=True, hide_index=True)
                        
                    elif payment_terms == "Annually":
                        payment_data = []
                        for y in years_data:
                            if y['annual_value'] > 0:
                                payment_data.append({
                                    "Year": f"Year {y['year_number']}",
                                    "Annual Payment": f"KES {y['annual_value']:,.2f}"
                                })
                        df_payment = pd.DataFrame(payment_data)
                        st.dataframe(df_payment, use_container_width=True, hide_index=True)
                        
                    elif payment_terms == "Milestone-based":
                        st.info("📌 Milestone-based payment schedule requires manual entry of payment milestones.")
                        milestone_input = st.text_area("Payment Milestones", placeholder="e.g., 30% upon signing, 40% at mid-term, 30% upon completion", height=80)
                        
                    else:  # One-time
                        st.info(f" One-time payment of KES {total_value:,.2f} due upon contract signing.")
                
                # Store years_data in session state for form submission
                st.session_state.contract_years_data = years_data
                        
            else:
                # Single Year Contract
                st.markdown("####  Contract Value")
                contract_value = st.number_input("Contract Value (KES)*", min_value=0.0, step=10000.0, format="%.2f", key="single_contract_value")
                amount_spent_to_date = st.number_input("Amount Spent to Date (KES)", min_value=0.0, step=10000.0, format="%.2f", value=0.0, key="single_amount_spent")
                
                # Calculate payment schedule for single year
                if contract_value > 0 and payment_terms:
                    st.markdown("#### 💳 Payment Schedule")
                    if payment_terms == "Monthly":
                        monthly = contract_value / 12
                        st.info(f" Monthly Payment: KES {monthly:,.2f}")
                        st.info(f" Total Annual Value: KES {contract_value:,.2f}")
                    elif payment_terms == "Quarterly":
                        quarterly = contract_value / 4
                        st.info(f" Quarterly Payment: KES {quarterly:,.2f}")
                        st.info(f" Total Annual Value: KES {contract_value:,.2f}")
                    elif payment_terms == "Bi-annually":
                        bi_annual = contract_value / 2
                        st.info(f" Bi-Annual Payment: KES {bi_annual:,.2f}")
                        st.info(f" Total Annual Value: KES {contract_value:,.2f}")
                    elif payment_terms == "Annually":
                        st.info(f" Annual Payment: KES {contract_value:,.2f}")
                    elif payment_terms == "One-time":
                        st.info(f" One-time Payment: KES {contract_value:,.2f}")
            
            st.markdown("---")
            
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
            
            # Submit button
            submitted = st.form_submit_button("Save Contract", use_container_width=True)
            
            if submitted:
                if not contract_title or not vendor_name or not contract_duration:
                    st.error("❌ Please fill all required fields (*)")
                else:
                    if contract_type == "Multi-Year Contract":
                        # Get years data from session state
                        years_data = st.session_state.get("contract_years_data", [])
                        
                        # Validate that all years have values > 0
                        valid_years = [y for y in years_data if y['annual_value'] > 0]
                        if not valid_years or len(valid_years) != num_years:
                            st.error("❌ Please add valid values for all years (greater than 0)")
                        else:
                            # Calculate totals
                            total_value = sum(y['annual_value'] for y in years_data)
                            total_spent = sum(y.get('amount_spent_to_date', 0) for y in years_data)
                            utilization = (total_spent / total_value * 100) if total_value > 0 else 0
                            
                            # Map department name to ID
                            dept_id = st.session_state.user_dept
                            dept_name = get_department_name(st.session_state.user_dept)
                            if department_id != "None":
                                dept_map = {d["name"]: d["id"] for d in get_cached_departments()}
                                dept_id = dept_map.get(department_id, st.session_state.user_dept)
                                dept_name = department_id
                            
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
                                "department_id": dept_id,
                                "department_name": dept_name
                            }
                            
                            success, message = add_multi_year_contract(contract_data, years_data)
                            if success:
                                st.success(f"✅ {message}")
                                st.balloons()
                                # Clear session state
                                st.session_state.contract_year_values = {}
                                st.session_state.contract_years_data = []
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")
                    else:
                        if contract_value <= 0:
                            st.error("❌ Please enter a valid contract value (greater than 0)")
                        else:
                            end_date_obj = end_date
                            days_left = (end_date_obj - datetime.now().date()).days
                            status = "active" if days_left > 30 else ("expiring_soon" if days_left > 0 else "expired")
                            utilization = (amount_spent_to_date / contract_value * 100) if contract_value > 0 else 0
                            
                            # Map department name to ID
                            dept_id = st.session_state.user_dept
                            dept_name = get_department_name(st.session_state.user_dept)
                            if department_id != "None":
                                dept_map = {d["name"]: d["id"] for d in get_cached_departments()}
                                dept_id = dept_map.get(department_id, st.session_state.user_dept)
                                dept_name = department_id
                            
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
                                "department_id": dept_id,
                                "department_name": dept_name
                            }
                            success, message = add_enhanced_contract(contract_data)
                            if success:
                                st.success(f"✅ {message}")
                                st.balloons()
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")
    
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
                                    st.error("❌ Failed to update contract")
            else:
                st.info("No updatable contracts found. Only active and expiring soon contracts can be updated.")
        else:
            st.info("No contracts found.")
    
    with tab_admin_edit:
        st.markdown("### 🔧 Admin: Full Contract Edit")
        st.warning("⚠️ This section is for **Admin/Management** only. You can edit **ALL** contract fields here.")
        
        if st.session_state.user_role in ["admin", "management"]:
            contracts = get_cached_contracts(st.session_state.user_role, st.session_state.user_dept)
            
            if contracts:
                # Handle missing department_name
                for c in contracts:
                    if 'department_name' not in c or not c['department_name']:
                        if c.get('department_id'):
                            dept_name = get_department_name(c['department_id'])
                            c['department_name'] = dept_name if dept_name else 'Unassigned'
                        else:
                            c['department_name'] = 'Unassigned'
                
                # Filter contracts by department if management
                if st.session_state.user_role == "management":
                    depts = sorted(set([c.get('department_name', 'Unassigned') for c in contracts]))
                    dept_filter = st.selectbox("Filter by Department", ["All"] + depts)
                    if dept_filter != "All":
                        contracts = [c for c in contracts if c.get('department_name') == dept_filter]
                
                contract_options = {
                    c["id"]: f"{c['contract_title']} - {c['vendor_name']} ({c.get('department_name', 'Unassigned')})" 
                    for c in contracts
                }
                
                selected_contract_id = st.selectbox(
                    "Select Contract to Fully Edit", 
                    list(contract_options.keys()), 
                    format_func=lambda x: contract_options[x]
                )
                
                if selected_contract_id:
                    selected_contract = next((c for c in contracts if c["id"] == selected_contract_id), None)
                    
                    if selected_contract:
                        st.markdown(f"#### Editing: **{selected_contract['contract_title']}**")
                        st.caption(f"Current Department: {selected_contract.get('department_name', 'Unassigned')}")
                        
                        with st.form("admin_full_edit_contract_form"):
                            st.markdown("##### Basic Information")
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                edit_title = st.text_input("Contract Title*", value=selected_contract.get("contract_title", ""))
                                edit_vendor = st.text_input("Vendor Name*", value=selected_contract.get("vendor_name", ""))
                                edit_duration = st.selectbox(
                                    "Contract Duration*", 
                                    ["3 months", "6 months", "1 year", "2 years", "3 years", "4 years", "5 years"],
                                    index=["3 months", "6 months", "1 year", "2 years", "3 years", "4 years", "5 years"].index(
                                        selected_contract.get("contract_duration", "1 year")
                                    ) if selected_contract.get("contract_duration") in ["3 months", "6 months", "1 year", "2 years", "3 years", "4 years", "5 years"] else 2
                                )
                                
                            with col2:
                                edit_start_date = st.date_input(
                                    "Start Date*", 
                                    value=datetime.strptime(selected_contract["start_date"], "%Y-%m-%d").date()
                                )
                                edit_end_date = st.date_input(
                                    "End Date*", 
                                    value=datetime.strptime(selected_contract["end_date"], "%Y-%m-%d").date()
                                )
                                edit_signed_date = st.date_input(
                                    "Signed Date", 
                                    value=datetime.strptime(selected_contract.get("signed_date", selected_contract["start_date"]), "%Y-%m-%d").date()
                                )
                            
                            st.markdown("##### Financial Details")
                            col3, col4 = st.columns(2)
                            
                            with col3:
                                edit_contract_value = st.number_input(
                                    "Contract Value (KES)*", 
                                    min_value=0.0, 
                                    step=10000.0, 
                                    format="%.2f",
                                    value=float(selected_contract.get("contract_value", 0))
                                )
                                edit_amount_spent = st.number_input(
                                    "Amount Spent to Date (KES)", 
                                    min_value=0.0, 
                                    step=10000.0, 
                                    format="%.2f",
                                    value=float(selected_contract.get("amount_spent_to_date", 0))
                                )
                                
                            with col4:
                                edit_payment_terms = st.selectbox(
                                    "Payment Terms*", 
                                    ["Monthly", "Quarterly", "Bi-annually", "Annually", "Milestone-based", "One-time"],
                                    index=["Monthly", "Quarterly", "Bi-annually", "Annually", "Milestone-based", "One-time"].index(
                                        selected_contract.get("payment_terms", "Monthly")
                                    ) if selected_contract.get("payment_terms") in ["Monthly", "Quarterly", "Bi-annually", "Annually", "Milestone-based", "One-time"] else 0
                                )
                                edit_auto_renewal = st.checkbox(
                                    "Auto-renewal", 
                                    value=selected_contract.get("auto_renewal", False)
                                )
                            
                            st.markdown("##### Compliance & Performance")
                            col5, col6 = st.columns(2)
                            
                            with col5:
                                edit_compliance = st.selectbox(
                                    "Compliance Status", 
                                    ["Fully Compliant", "Partially Compliant", "Non-Compliant"],
                                    index=["Fully Compliant", "Partially Compliant", "Non-Compliant"].index(
                                        selected_contract.get("compliance_status", "Fully Compliant")
                                    ) if selected_contract.get("compliance_status") in ["Fully Compliant", "Partially Compliant", "Non-Compliant"] else 0
                                )
                                edit_performance = st.slider(
                                    "Vendor Performance Rating", 
                                    0.0, 5.0, 
                                    value=float(selected_contract.get("vendor_performance", 3.0)), 
                                    step=0.5
                                )
                                
                            with col6:
                                edit_contract_url = st.text_input(
                                    "Contract Document URL", 
                                    value=selected_contract.get("contract_url", ""),
                                    placeholder="https://..."
                                )
                                edit_breach_notes = st.text_area(
                                    "Breach/Compliance Notes", 
                                    value=selected_contract.get("breach_notes", ""),
                                    height=80
                                )
                            
                            st.markdown("##### Department Assignment")
                            departments = get_cached_departments()
                            dept_list = ["None"] + [d["name"] for d in departments]
                            current_dept = selected_contract.get("department_name", "None")
                            dept_index = dept_list.index(current_dept) if current_dept in dept_list else 0
                            
                            edit_department = st.selectbox(
                                "Assign Contract to Department", 
                                dept_list, 
                                index=dept_index,
                                help="Select which department this contract belongs to"
                            )
                            
                            st.markdown("---")
                            
                            # Show multi-year indicator
                            if selected_contract.get("is_multi_year"):
                                st.info("📅 This is a **multi-year contract**. Edit the total value carefully.")
                                years = get_contract_years(selected_contract_id)
                                if years:
                                    with st.expander("📅 View Multi-Year Breakdown", expanded=False):
                                        year_data = []
                                        for y in years:
                                            year_data.append({
                                                "Year": f"Year {y['year_number']}",
                                                "Annual Value": f"KES {y.get('annual_value', 0):,.0f}",
                                                "Spent": f"KES {y.get('amount_spent_to_date', 0):,.0f}",
                                                "Status": y.get('status', 'active')
                                            })
                                        df_years = pd.DataFrame(year_data)
                                        st.dataframe(df_years, use_container_width=True, hide_index=True)
                            
                            # Submit button with better error handling
                            submitted = st.form_submit_button("💾 Update All Contract Fields", use_container_width=True, type="primary")
                            
                            if submitted:
                                # Validate required fields
                                if not edit_title:
                                    st.error("❌ Contract Title is required")
                                elif not edit_vendor:
                                    st.error("❌ Vendor Name is required")
                                elif edit_contract_value <= 0:
                                    st.error("❌ Contract value must be greater than 0")
                                else:
                                    try:
                                        # Map department name to ID
                                        dept_map = {d["name"]: d["id"] for d in departments}
                                        dept_id = dept_map.get(edit_department) if edit_department != "None" else None
                                        dept_name = edit_department if edit_department != "None" else "Unassigned"
                                        
                                        # Prepare update data with ALL fields
                                        update_data = {
                                            "contract_title": edit_title,
                                            "vendor_name": edit_vendor,
                                            "contract_duration": edit_duration,
                                            "contract_value": float(edit_contract_value),
                                            "total_contract_value": float(edit_contract_value),
                                            "amount_spent_to_date": float(edit_amount_spent),
                                            "start_date": edit_start_date.isoformat(),
                                            "end_date": edit_end_date.isoformat(),
                                            "signed_date": edit_signed_date.isoformat(),
                                            "payment_terms": edit_payment_terms,
                                            "auto_renewal": edit_auto_renewal,
                                            "compliance_status": edit_compliance,
                                            "vendor_performance": float(edit_performance),
                                            "contract_url": edit_contract_url if edit_contract_url else None,
                                            "breach_notes": edit_breach_notes if edit_breach_notes else None,
                                            "department_id": dept_id,
                                            "department_name": dept_name,
                                            "is_multi_year": selected_contract.get("is_multi_year", False)
                                        }
                                        
                                        # Show what we're updating
                                        with st.spinner("Updating contract..."):
                                            if update_contract_admin_full(selected_contract_id, update_data):
                                                st.success("✅ Contract updated successfully with all fields!")
                                                add_audit_log("FULL_UPDATE", "contract", selected_contract_id, 
                                                             f"Admin full updated contract: {edit_title}")
                                                st.balloons()
                                                st.rerun()
                                            else:
                                                st.error("❌ Failed to update contract. Please check the logs for details.")
                                    except Exception as e:
                                        st.error(f"❌ Error: {str(e)}")
            else:
                st.info("No contracts found to edit.")
        else:
            st.error("❌ You do not have permission to access this section. Admin/Management only.")

# ============================================
# POLICIES SECTION
# ============================================
elif st.session_state.active_menu == "📋 Policies":
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
                policy_duration = st.selectbox("Policy Duration", ["Custom"] + POLICY_DURATIONS, help="Select duration to auto-calculate expiry date")
                
                if policy_duration != "Custom":
                    duration_years = int(policy_duration.split()[0])
                    expiry_date_calculated = effective_date + relativedelta(years=duration_years)
                    st.info(f"📅 Expiry date set to: {expiry_date_calculated.strftime('%Y-%m-%d')} ({policy_duration})")
                    expiry_date_input = st.date_input("Expiry Date*", value=expiry_date_calculated)
                else:
                    expiry_date_input = st.date_input("Expiry Date*")
                
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
                if policy_name and category and policy_owner and expiry_date_input:
                    policy_data = {
                        "policy_name": policy_name,
                        "category": category,
                        "version": version,
                        "policy_scope": policy_scope,
                        "affected_entities": affected_entities,
                        "policy_owner": policy_owner,
                        "effective_date": effective_date.isoformat(),
                        "expiry_date": expiry_date_input.isoformat(),
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
                    status_class = "active"
                    status_text = "Active"
                elif days_left > 0:
                    status_class = "expiring"
                    status_text = f"Expires in {days_left} days"
                else:
                    status_class = "expired"
                    status_text = "Expired"
                
                category = policy.get('category', 'Uncategorized')
                policy_scope = policy.get('policy_scope', 'Not specified')
                version = policy.get('version', 'v1.0')
                owner = policy.get('policy_owner', 'Not assigned')
                review_date = policy.get('review_date', 'Not scheduled')
                
                expander_title = f"📜 {policy['policy_name']} (v{version}) - {status_text}"
                
                with st.expander(expander_title, expanded=False):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Policy Name:** {policy['policy_name']}")
                        st.markdown(f"**Category:** {category}")
                        st.markdown(f"**Version:** {version}")
                        st.markdown(f"**Scope:** {policy_scope}")
                        st.markdown(f"**Affected Entities:** {policy.get('affected_entities', 'N/A')}")
                        st.markdown(f"**Policy Owner:** {owner}")
                    with col2:
                        st.markdown(f"**Effective Date:** {policy.get('effective_date', 'N/A')}")
                        st.markdown(f"**Expiry Date:** {policy['expiry_date']}")
                        st.markdown(f"**Next Review:** {review_date}")
                        st.markdown(f"**Status:** {status_text}")
                        if policy.get('requires_acknowledgment'):
                            st.info("📋 Requires Staff Acknowledgment")
                        if policy.get('requires_sensitization'):
                            st.info("🎓 Requires Sensitization")
                    
                    st.markdown("---")
                    if policy.get('policy_url'):
                        st.markdown(f"📄 **Policy Document:** [View Document]({policy['policy_url']})", unsafe_allow_html=True)
                    if policy.get('change_log'):
                        st.markdown(f"**Change Log:** {policy['change_log']}")
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
# ADMIN PANEL
# ============================================
elif st.session_state.active_menu == "⚙️ Admin Panel" and st.session_state.user_role == "admin":
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
                            
                            reset_password = st.checkbox("Reset Password to 'password123'")
                            
                            if st.button("Save Changes", use_container_width=True):
                                dept_id = dept_options.get(new_department) if new_department != "None" else None
                                if update_user_role(selected_username, new_role, dept_id):
                                    st.success(f"✅ Role and department updated for {selected_username}")
                                else:
                                    st.error("Failed to update role/department")
                                
                                if reset_password:
                                    success, message = admin_reset_password(selected_username, "password123")
                                    if success:
                                        st.success(f"✅ {message}")
                                    else:
                                        st.error(f"❌ {message}")
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
                    policy_duration = st.selectbox("Policy Duration", ["Custom"] + POLICY_DURATIONS)
                    
                    if policy_duration != "Custom":
                        duration_years = int(policy_duration.split()[0])
                        expiry_date_calculated = effective_date + relativedelta(years=duration_years)
                        st.info(f"📅 Expiry date set to: {expiry_date_calculated.strftime('%Y-%m-%d')} ({policy_duration})")
                        expiry_date_input = st.date_input("Expiry Date*", value=expiry_date_calculated)
                    else:
                        expiry_date_input = st.date_input("Expiry Date*")
                    
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
                                "expiry_date": expiry_date_input.isoformat(),
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
                    payment_terms = st.selectbox("Payment Terms", ["Monthly", "Quarterly", "Bi-annually", "Annually", "Milestone-based", "One-time"])
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
                            dept_name = department_id if department_id != "None" else "Unassigned"
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
                                "department_id": dept_id,
                                "department_name": dept_name
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
                    contract_options = {c["id"]: f"{c['contract_title']} - {c['vendor_name']} ({c.get('department_name', 'Unassigned')})" for c in contracts}
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
                                    edit_department = st.selectbox("Department", ["None"] + list(dept_options.keys()), 
                                                                  index=0 if selected_contract.get("department_name") not in dept_options else list(dept_options.keys()).index(selected_contract.get("department_name", "")) + 1)
                                    
                                    if st.form_submit_button("Update Contract", use_container_width=True):
                                        dept_id = dept_options.get(edit_department) if edit_department != "None" else None
                                        dept_name = edit_department if edit_department != "None" else "Unassigned"
                                        
                                        update_data = {
                                            "contract_title": edit_title,
                                            "vendor_name": edit_vendor,
                                            "contract_value": edit_value,
                                            "amount_spent_to_date": edit_spent,
                                            "end_date": edit_end_date.isoformat(),
                                            "status": edit_status,
                                            "compliance_status": edit_compliance,
                                            "vendor_performance": edit_performance,
                                            "department_id": dept_id,
                                            "department_name": dept_name,
                                            "updated_at": datetime.now().isoformat()
                                        }
                                        if update_contract_admin_full(selected_contract_id, update_data):
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
            # Handle missing department_name
            if 'department_name' not in df_contracts_admin.columns:
                df_contracts_admin['department_name'] = 'Unassigned'
            display_cols = ['contract_title', 'vendor_name', 'contract_value', 'amount_spent_to_date', 'status', 'end_date', 'compliance_status', 'vendor_performance', 'department_name', 'is_multi_year']
            # Only show columns that exist
            available_cols = [col for col in display_cols if col in df_contracts_admin.columns]
            st.dataframe(df_contracts_admin[available_cols], use_container_width=True, hide_index=True)
    
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
                    start_date = st.date_input("Start Date*", value=datetime.now().date())
                    end_date = st.date_input("End Date*")
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
                                "start_date": start_date.isoformat(),
                                "end_date": end_date.isoformat(),
                                "due_date": end_date.isoformat(),
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
                                    edit_start_date = st.date_input("Start Date", value=datetime.strptime(selected_wp.get("start_date", selected_wp["due_date"]), "%Y-%m-%d").date() if selected_wp.get("start_date") else datetime.strptime(selected_wp["due_date"], "%Y-%m-%d").date())
                                    edit_end_date = st.date_input("End Date", value=datetime.strptime(selected_wp["due_date"], "%Y-%m-%d").date())
                                    edit_progress = st.number_input("Progress %", min_value=0, max_value=100, value=int(selected_wp.get("progress_percent", 0)))
                                    edit_status = st.selectbox("Status", ["Pending", "In Progress", "Done"], index=["Pending", "In Progress", "Done"].index(selected_wp.get("status", "Pending")))
                                    edit_actual = st.number_input("Actual Achievement", value=float(selected_wp.get("actual_achievement", 0)))
                                    
                                    if st.form_submit_button("Update Work Plan", use_container_width=True):
                                        update_data = {
                                            "planned_activity": edit_activity,
                                            "annual_target": edit_target,
                                            "start_date": edit_start_date.isoformat(),
                                            "end_date": edit_end_date.isoformat(),
                                            "due_date": edit_end_date.isoformat(),
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
            display_cols = ['planned_activity', 'department_name', 'annual_target', 'progress_percent', 'status', 'start_date', 'end_date', 'due_date']
            st.dataframe(df_wp_admin[display_cols], use_container_width=True, hide_index=True)
    
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
            st.info("No audit logs found.")

# ============================================
# ENTERPRISE VIEW
# ============================================
elif st.session_state.active_menu == "🏢 Enterprise View" and st.session_state.user_role in ["admin", "management"]:
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
                           'department_name', 'status', 'progress_percent', 'start_date', 'end_date', 'due_date']
            st.dataframe(df[display_cols], use_container_width=True, hide_index=True)
        else:
            st.info("No work plans found")
    
    with tabs[1]:
        all_contracts = get_cached_contracts(st.session_state.user_role, st.session_state.user_dept)
        if all_contracts:
            df = pd.DataFrame(all_contracts)
            display_cols = ["contract_title", "vendor_name", "contract_value", "amount_spent_to_date", "end_date", "status", "compliance_status", "department_name", "is_multi_year"]
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
