import streamlit as st
import os
from dotenv import load_dotenv
import json
import traceback
import pdfplumber
from report_processing.extractor import BloodReportExtractor
from report_processing.parser import ReportParser
from analytics.analyzer import HealthAnalyzer
from ai.summary_generator import SummaryGenerator
from ai.chatbot import HealthChatbot
from dashboard.charts import DashboardCharts
import pandas as pd
from auth import verify_user, register_user, create_default_admin, derive_username_from_email
from utils import validate_api_key, setup_logger, sanitize_filename
from database import init_db, db_save_report, db_get_user_reports, db_get_report_detail, db_delete_report

# Load environment variables
load_dotenv()

# Setup logger
logger = setup_logger("app")

# Initialize database on startup
try:
    init_db()
except Exception as _db_err:
    print(f"DB init warning: {_db_err}")

# ── Cached heavy singletons (load once, reuse across all reruns) ──────────────
@st.cache_resource(show_spinner="Loading OCR & extraction engine...")
def _get_extractor():
    return BloodReportExtractor()

@st.cache_resource(show_spinner="Loading analytics engine...")
def _get_analyzer():
    return HealthAnalyzer()

@st.cache_resource(show_spinner="Loading AI summary engine...")
def _get_summary_gen():
    return SummaryGenerator()

@st.cache_resource(show_spinner="Loading AI chatbot...")
def _get_chatbot():
    return HealthChatbot()
# ─────────────────────────────────────────────────────────────────────────────

# Page configuration
st.set_page_config(
    page_title="AI Health Diagnostics Assistant",
    page_icon="⚕️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Medical Green Theme
st.markdown("""
<style>
    /* Color Palette */
    :root {
        --primary-green: #1ABC9C;
        --dark-green: #16A085;
        --light-green: #D5F4E6;
        --accent-green: #27AE60;
        --text-dark: #2C3E50;
        --text-light: #ECF0F1;
    }
    
    /* Main Header */
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(135deg, #1ABC9C 0%, #16A085 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 1rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Sub Header */
    .sub-header {
        font-size: 1.8rem;
        color: #16A085;
        margin-top: 1.5rem;
        font-weight: 600;
        border-left: 4px solid #1ABC9C;
        padding-left: 1rem;
    }
    
    /* Header Bar */
    .header-bar {
        background: linear-gradient(135deg, #1ABC9C 0%, #16A085 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(26, 188, 156, 0.3);
        text-align: center;
    }
    
    .header-bar h1 {
        margin: 0;
        font-size: 2.5rem;
        color: white;
    }
    
    .header-bar p {
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.95;
    }
    
    /* Info Box */
    .info-box {
        background: linear-gradient(135deg, #D5F4E6 0%, #E8F8F5 100%);
        border-left: 5px solid #1ABC9C;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(26, 188, 156, 0.15);
    }
    
    .info-box ul {
        margin-left: 1.5rem;
    }
    
    .info-box li {
        margin: 0.5rem 0;
        color: #2C3E50;
    }
    
    /* Warning Box */
    .warning-box {
        background-color: #FEF5E7;
        border-left: 5px solid #F39C12;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(243, 156, 18, 0.15);
    }
    
    /* Critical Box */
    .critical-box {
        background: linear-gradient(135deg, #FADBD8 0%, #F5B7B1 100%);
        border-left: 5px solid #E74C3C;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(231, 76, 60, 0.15);
    }
    
    /* Login Container */
    .login-container {
        max-width: 420px;
        margin: 30px auto;
        padding: 35px 30px;
        background: linear-gradient(135deg, #FFFFFF 0%, #F0FDFB 100%);
        border-radius: 15px;
        box-shadow: 0 10px 40px rgba(26, 188, 156, 0.2);
        border: 2px solid #E8F8F5;
    }
    
    /* Login Title */
    .login-title {
        text-align: center;
        background: linear-gradient(135deg, #1ABC9C 0%, #16A085 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 5px;
        font-size: 2rem;
        font-weight: bold;
    }
    
    .login-subtitle {
        text-align: center;
        color: #16A085;
        font-size: 0.95rem;
        margin-bottom: 20px;
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #1ABC9C 0%, #16A085 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        box-shadow: 0 6px 20px rgba(26, 188, 156, 0.4);
        transform: translateY(-2px);
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: #F0FDFB;
        padding: 3px;
        border-radius: 10px;
        margin-bottom: 15px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #E8F8F5;
        border-radius: 8px;
        color: #16A085;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #1ABC9C;
        color: white;
    }
    
    /* Tab Content Spacing */
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 10px;
    }
    
    /* Input Styling */
    .stTextInput > div > div > input {
        border: 2px solid #D5F4E6;
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 0.95rem;
    }
    
    /* Label Styling */
    .stTextInput > label {
        font-size: 0.9rem;
        font-weight: 500;
        color: #2C3E50;
        margin-bottom: 4px;
    }
    
    /* Reduce spacing between elements */
    .stTextInput {
        margin-bottom: 12px;
    }
    
    .stTextInput > div > div > input:focus {
        border: 2px solid #1ABC9C;
        box-shadow: 0 0 10px rgba(26, 188, 156, 0.3);
    }
    
    /* Slider Container */
    .slider-container {
        background: linear-gradient(135deg, #D5F4E6 0%, #E8F8F5 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
        border: 2px solid #1ABC9C;
        box-shadow: 0 4px 15px rgba(26, 188, 156, 0.15);
    }
    
    .slider-title {
        color: #16A085;
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    
    /* Health Metric Cards */
    .health-metric {
        background: linear-gradient(135deg, #FFFFFF 0%, #F0FDFB 100%);
        border: 2px solid #1ABC9C;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(26, 188, 156, 0.1);
    }
    
    .health-metric-title {
        color: #16A085;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .health-metric-value {
        font-size: 1.5rem;
        color: #1ABC9C;
        font-weight: bold;
    }
    
    /* Footer */
    .footer {
        background: linear-gradient(135deg, #16A085 0%, #0E6251 100%);
        color: white;
        text-align: center;
        padding: 2rem;
        margin-top: 3rem;
        border-radius: 0 0 0 0;
        box-shadow: 0 -4px 15px rgba(26, 188, 156, 0.2);
    }
    
    .footer p {
        margin: 0.5rem 0;
        opacity: 0.9;
    }
    
    .footer a {
        color: #1ABC9C;
        text-decoration: none;
        font-weight: 600;
    }
    
    .footer a:hover {
        text-decoration: underline;
    }
    
    /* Divider */
    .divider-green {
        background: linear-gradient(90deg, transparent, #1ABC9C, transparent);
        height: 2px;
        margin: 2rem 0;
    }
    
    /* Metric Badge */
    .metric-badge {
        display: inline-block;
        background: linear-gradient(135deg, #1ABC9C 0%, #16A085 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: bold;
        margin: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []
if 'chatbot' not in st.session_state:
    st.session_state.chatbot = None
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'patient_info' not in st.session_state:
    st.session_state.patient_info = {}

def login_page():
    # Header with medical theme
    st.markdown("""
    <div class="header-bar">
        <h1>🩺 AIMedi Health Assistant</h1>
        <p>Advanced Blood Report Analysis & AI-Powered Health Insights</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container():
            st.markdown('<div class="login-container">', unsafe_allow_html=True)
            
            st.markdown('<h2 class="login-title">Welcome Back</h2>', unsafe_allow_html=True)
            st.markdown('<p class="login-subtitle">Sign in to your account</p>', unsafe_allow_html=True)
            
            tab_login, tab_register = st.tabs(["🔐 Login", "📝 Register"])
            
            with tab_login:
                login_username = st.text_input("Username", key="login_user", placeholder="Enter your username")
                login_password = st.text_input("Password", type="password", key="login_pass", placeholder="Enter your password")
                
                if st.button("🔓 Login", use_container_width=True, key="login_btn"):
                    if login_username and login_password:
                        if verify_user(login_username, login_password):
                            st.session_state.logged_in = True
                            st.session_state.username = login_username
                            st.success("✅ Login successful! Redirecting...")
                            st.rerun()
                        else:
                            st.error("❌ Invalid username or password. Please try again.")
                    else:
                        st.warning("⚠️ Please enter both username and password")
            
            with tab_register:
                st.caption("Choose a username or leave it blank to use your email name.")
                reg_username = st.text_input("Username", key="reg_username", placeholder="Choose a username")
                reg_email = st.text_input("Email Address", key="reg_email", placeholder="Enter your email (e.g. user@email.com)")
                reg_password = st.text_input("Password", type="password", key="reg_pass", placeholder="Create a password (min 6 chars)")
                reg_confirm = st.text_input("Confirm Password", type="password", key="reg_confirm", placeholder="Confirm your password")

                if st.button("✅ Register", use_container_width=True, key="register_btn"):
                    reg_username = reg_username.strip()
                    reg_email = reg_email.strip()
                    reg_password = reg_password.strip()
                    reg_confirm = reg_confirm.strip()
                    if not reg_email or not reg_password or not reg_confirm:
                        st.warning("⚠️ Email and Password are required")
                    elif reg_password != reg_confirm:
                        st.error("❌ Passwords do not match. Please try again.")
                    elif len(reg_password) < 6:
                        st.error("❌ Password must be at least 6 characters")
                    else:
                        username_to_use = reg_username or derive_username_from_email(reg_email)
                        success, msg = register_user(
                            username_to_use, reg_password,
                            email=reg_email,
                            full_name="",
                            dob=""
                        )
                        if success:
                            st.success(f"✅ {msg} Logging you in...")
                            st.session_state.logged_in = True
                            st.session_state.username = username_to_use
                            st.balloons()
                            st.rerun()
                        else:
                            st.error(f"❌ {msg}")
            
            st.markdown('</div>', unsafe_allow_html=True)

def main():
    if not st.session_state.logged_in:
        create_default_admin()
        login_page()
        return
    
    # Enhanced Header
    st.markdown("""
    <div class="header-bar">
        <h1>🩺 AIMedi Health Diagnostics Assistant</h1>
        <p>Powered by Advanced AI | Comprehensive Blood Report Analysis System</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        from auth import get_user_info as _get_sidebar_user
        _sidebar_user = _get_sidebar_user(st.session_state.username)
        _display_name = _sidebar_user.get('full_name') or st.session_state.username
        _display_name = _display_name.replace("<", "&lt;").replace(">", "&gt;")
        _email_line = f"<p style='margin:2px 0; font-size:0.82rem; opacity:0.85;'>📧 {_sidebar_user['email']}</p>" if _sidebar_user.get('email') else ""

        # Patient info from uploaded report
        _pi = st.session_state.get('patient_info', {})
        _patient_block = ""
        if _pi and any(_pi.values()):
            _p_name   = _pi.get('name') or ''
            _p_age    = _pi.get('age') or ''
            _p_gender = _pi.get('gender') or ''
            _p_date   = _pi.get('report_date') or ''
            _p_rows = ""
            if _p_name:   _p_rows += f'<p style="margin:2px 0;font-size:0.8rem;">👤 {_p_name}</p>'
            if _p_age:    _p_rows += f'<p style="margin:2px 0;font-size:0.8rem;">🎂 Age: {_p_age}</p>'
            if _p_gender: _p_rows += f'<p style="margin:2px 0;font-size:0.8rem;">⚕️ {_p_gender}</p>'
            if _p_date:   _p_rows += f'<p style="margin:2px 0;font-size:0.8rem;">📅 {_p_date}</p>'
            _patient_block = f"""<div style='margin-top:10px;background:rgba(255,255,255,0.15);border-radius:8px;padding:8px 10px;text-align:left;'><p style='margin:0 0 4px 0;font-weight:bold;font-size:0.85rem;'>🩺 Last Report</p>{_p_rows}</div>"""

        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1ABC9C 0%, #16A085 100%);
                    color: white; padding: 1.5rem; border-radius: 10px; text-align: center;">
            <h2 style="margin-top: 0; color: white;">👤 User Profile</h2>
            <p style="margin: 0; font-size: 1.1rem; font-weight: bold;">{_display_name}</p>
            {_email_line}
            {_patient_block}
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.analysis_complete = False
            st.session_state.chat_messages = []
            st.success("✅ Logged out successfully!")
            st.rerun()
        
        st.divider()
        st.title("📋 Navigation")
        
        page = st.radio(
            "Select Page",
            ["🔬 Upload & Analyze", "📋 Report History", "ℹ️ About"],
            index=0
        )
        
        st.divider()
        st.markdown("### ⚙️ Settings")

        gender = st.selectbox("👥 Select Gender", ["👨 Male", "👩 Female"])

        if st.button("🗑️ Clear All Data", use_container_width=True):
            st.session_state.analysis_complete = False
            st.session_state.chat_messages = []
            st.session_state.chatbot = None
            st.success("✅ Data cleared!")
            st.rerun()

        st.divider()
        st.markdown("### 👤 My Profile")

        from auth import get_user_info, update_user_info, change_password
        user_info = get_user_info(st.session_state.username)

        with st.expander("✏️ Edit Profile", expanded=False):
            new_full_name = st.text_input(
                "Full Name",
                value=user_info.get("full_name", ""),
                placeholder="Enter your full name",
                key="settings_full_name"
            )
            new_email = st.text_input(
                "Email",
                value=user_info.get("email", ""),
                placeholder="Enter your email",
                key="settings_email"
            )
            if st.button("💾 Save Profile", use_container_width=True, key="save_profile_btn"):
                success, msg = update_user_info(
                    st.session_state.username,
                    full_name=new_full_name,
                    email=new_email if new_email else None,
                    dob=""
                )
                if success:
                    st.success(f"✅ {msg}")
                else:
                    st.error(f"❌ {msg}")

        with st.expander("🔑 Change Password", expanded=False):
            old_pass = st.text_input("Current Password", type="password", key="old_pass")
            new_pass = st.text_input("New Password", type="password", key="new_pass", placeholder="Min 6 characters")
            confirm_pass = st.text_input("Confirm New Password", type="password", key="confirm_pass")
            if st.button("🔒 Update Password", use_container_width=True, key="update_pass_btn"):
                if not old_pass or not new_pass or not confirm_pass:
                    st.warning("⚠️ Please fill all password fields")
                elif new_pass != confirm_pass:
                    st.error("❌ New passwords do not match")
                else:
                    success, msg = change_password(st.session_state.username, old_pass, new_pass)
                    if success:
                        st.success(f"✅ {msg}")
                    else:
                        st.error(f"❌ {msg}")

        # Show current profile info
        if user_info.get("full_name") or user_info.get("email"):
            st.markdown("""
            <div class="info-box" style="font-size:0.85rem;">
            """, unsafe_allow_html=True)
            if user_info.get("full_name"):
                st.markdown(f"👤 **Name:** {user_info['full_name']}")
            if user_info.get("email"):
                st.markdown(f"📧 **Email:** {user_info['email']}")
            st.markdown("</div>", unsafe_allow_html=True)

        st.divider()
        st.markdown("""
        <div class="info-box">
        <strong>📞 Need Help?</strong><br>
        Contact our Team at ansarisalmanmd091@gmail.com .
        </div>
        """, unsafe_allow_html=True)
    
    # Check API Key
    api_key = os.getenv('GROQ_API_KEY')
    if not validate_api_key(api_key):
        st.error("⚠️ Please configure a valid GROQ_API_KEY in the .env file!")
        st.info("🔑 Get your API key from: https://console.groq.com/keys")
        st.warning("💡 Make sure your API key starts with 'gsk_' and is not a placeholder")
        logger.error("Invalid or missing GROQ_API_KEY")
        st.stop()
    
    # Page routing
    if page == "🔬 Upload & Analyze":
        gender_value = "male" if "Male" in gender else "female"
        upload_analyze_page(gender_value)
    elif page == "📋 Report History":
        report_history_page()
    elif page == "ℹ️ About":
        about_page()
    
    # Footer
    display_footer()

def upload_analyze_page(gender):
    st.markdown('<h2 class="sub-header">📄 Upload Blood Report</h2>', unsafe_allow_html=True)
    
    # Health Metrics Overview
    st.markdown("""
    <div class="slider-container">
        <div class="slider-title">📊 Quick Health Metrics Guide</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="health-metric">
            <div class="health-metric-title">💪 Hemoglobin</div>
            <div class="health-metric-value">Normal: 12-16 g/dL</div>
            <small>Oxygen carrier in blood</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="health-metric">
            <div class="health-metric-title">🩸 Platelets</div>
            <div class="health-metric-value">Normal: 150-400 K/µL</div>
            <small>Blood clotting cells</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="health-metric">
            <div class="health-metric-title">🧬 HbA1c</div>
            <div class="health-metric-value">Normal: &lt;5.7%</div>
            <small>Blood sugar level</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="health-metric">
            <div class="health-metric-title">❤️ Cholesterol</div>
            <div class="health-metric-value">Normal: &lt;200 mg/dL</div>
            <small>Heart health indicator</small>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Upload your blood report",
            type=['pdf', 'png', 'jpg', 'jpeg'],
            help="Upload a PDF or image file containing your blood test results"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        use_ocr = st.checkbox("🔍 Use OCR", value=False, help="Enable for scanned PDFs or images")
    
    if uploaded_file:
        with st.spinner("⏳ Processing your blood report..."):
            temp_path = None
            try:
                # Validate file size (max 10MB)
                if uploaded_file.size > 10 * 1024 * 1024:
                    st.error("❌ File size exceeds 10MB limit")
                    return
                
                temp_path = f"temp_{sanitize_filename(uploaded_file.name)}"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                st.info(f"📁 File uploaded: {uploaded_file.name} ({uploaded_file.size} bytes)")
                
                extractor = _get_extractor()
                
                file_ext = uploaded_file.name.lower().split('.')[-1]
                
                # Extract full text for patient info extraction
                full_text = ""
                try:
                    if file_ext in ['png', 'jpg', 'jpeg']:
                        st.info("🔍 Using OCR to extract text from image...")
                        extracted_data = extractor.extract_from_image(temp_path)
                        # Get OCR text stored by extractor for patient info
                        full_text = getattr(extractor, '_last_ocr_text', '') or ''
                    else:
                        # For PDFs, extract full text first
                        try:
                            with pdfplumber.open(temp_path) as pdf:
                                for page in pdf.pages:
                                    full_text += (page.extract_text() or "") + "\n"
                        except:
                            full_text = ""
                        
                        if use_ocr:
                            st.info("🔍 Using OCR to extract text from PDF...")
                        else:
                            st.info("📄 Extracting text from PDF...")
                        extracted_data = extractor.extract_from_pdf(temp_path, use_ocr=use_ocr)
                except Exception as text_extract_error:
                    print(f"Error extracting full text: {text_extract_error}")
                    full_text = ""
                
                # Debug: Log the type and structure
                print(f"\n{'='*60}")
                print(f"DEBUG: extract_from_pdf/image returned:")
                print(f"  Type: {type(extracted_data)}")
                print(f"  Is tuple: {isinstance(extracted_data, tuple)}")
                if isinstance(extracted_data, tuple):
                    print(f"  Tuple length: {len(extracted_data)}")
                elif isinstance(extracted_data, dict):
                    print(f"  Dict keys: {list(extracted_data.keys())}")
                print(f"{'='*60}\n")
                
                if not extracted_data:
                    st.error("❌ No blood parameters found in the file.")
                    
                    # Show what OCR actually extracted for debugging
                    _ocr_debug = getattr(_get_extractor(), '_last_ocr_text', '') or ''
                    if _ocr_debug:
                        with st.expander("🔍 View Raw OCR Text (for debugging)"):
                            st.text(_ocr_debug)
                    
                    st.markdown("""
                    <div class="warning-box">
                    <strong>Possible reasons:</strong>
                    <ul>
                        <li>Image quality is too low (try a clearer photo)</li>
                        <li>Text is not readable (ensure good lighting)</li>
                        <li>File doesn't contain blood test parameters</li>
                        <li>OCR failed (check if Tesseract is installed)</li>
                    </ul>
                    <strong>Tips:</strong>
                    <ul>
                        <li>For scanned PDFs: Check "Use OCR" ✅</li>
                        <li>For images: Use high resolution (300 DPI or more)</li>
                        <li>Ensure text is horizontal and not rotated</li>
                        <li>Make sure parameter names are visible (Hemoglobin, HbA1c, etc.)</li>
                    </ul>
                    </div>
                    """, unsafe_allow_html=True)
                    return
                
                # Handle tuple returns - unwrap if tuple contains dict
                if isinstance(extracted_data, tuple):
                    print(f"DEBUG: extracted_data is tuple with {len(extracted_data)} elements")
                    for i, item in enumerate(extracted_data):
                        print(f"  Element {i}: type={type(item).__name__}")
                        if isinstance(item, dict) and ('hemoglobin' in item or 'rbc' in item or 'glucose' in item):
                            extracted_data = item
                            print(f"DEBUG: Unwrapped tuple, using element {i}")
                            break
                    else:
                        # If no dict with blood params found, use first element if it's a dict
                        if len(extracted_data) > 0 and isinstance(extracted_data[0], dict):
                            extracted_data = extracted_data[0]
                            print(f"DEBUG: Unwrapped tuple, using first element")
                        else:
                            st.error(f"❌ Invalid data format: tuple with unexpected content")
                            with st.expander("Debug Information"):
                                st.write(f"Tuple elements: {[type(x).__name__ for x in extracted_data]}")
                            return
                
                # Validate extracted data type
                if not isinstance(extracted_data, dict):
                    st.error(f"❌ Invalid data format: expected dictionary, got {type(extracted_data).__name__}")
                    with st.expander("Debug Information"):
                        st.write(f"Data type: {type(extracted_data)}")
                        st.write(f"Data content: {str(extracted_data)[:500]}")
                    return
                
                st.success(f"✅ Successfully extracted {len(extracted_data)} parameters!")
                
                # Display patient information in real-time from full text
                st.divider()
                st.markdown('<h2 class="sub-header">👤 Patient Information</h2>', unsafe_allow_html=True)
                
                # Extract patient info from the full text
                patient_info = {}
                try:
                    from report_processing.patient_info import PatientInfoExtractor
                    patient_extractor = PatientInfoExtractor()
                    
                    # Use the full text extracted from PDF/image
                    if full_text:
                        patient_info = patient_extractor.extract_patient_info(full_text)
                        print(f"Extracted patient info: {patient_info}")
                    else:
                        print("No full text available for patient info extraction")
                        patient_info = {}
                except Exception as e:
                    print(f"Error extracting patient info: {e}")
                    import traceback
                    traceback.print_exc()
                    patient_info = {}
                
                # Display patient info in a professional card format
                if patient_info and any(patient_info.values()):
                    # Patient info found - display it
                    patient_col1, patient_col2 = st.columns(2)
                    
                    with patient_col1:
                        st.markdown(f"""
                        <div class="info-box">
                            <strong>👤 Patient Name:</strong><br>
                            <span style="font-size: 1.1rem; color: #1ABC9C; font-weight: bold;">{patient_info.get('name', 'Not found')}</span><br><br>
                            <strong>🎂 Age:</strong><br>
                            <span style="font-size: 1.1rem; color: #1ABC9C; font-weight: bold;">{patient_info.get('age', 'Not found')} years</span><br><br>
                            <strong>⚕️ Gender:</strong><br>
                            <span style="font-size: 1.1rem; color: #1ABC9C; font-weight: bold;">{patient_info.get('gender', 'Not found').title() if patient_info.get('gender') else 'Not found'}</span>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with patient_col2:
                        st.markdown(f"""
                        <div class="info-box">
                            <strong>📅 Report Date:</strong><br>
                            <span style="font-size: 1.1rem; color: #1ABC9C; font-weight: bold;">{patient_info.get('report_date', 'Not found')}</span><br><br>
                            <strong>🆔 Report ID:</strong><br>
                            <span style="font-size: 1.1rem; color: #1ABC9C; font-weight: bold;">{patient_info.get('report_id', 'Not found')}</span><br><br>
                            <strong>👨‍⚕️ Referring Doctor:</strong><br>
                            <span style="font-size: 1.1rem; color: #1ABC9C; font-weight: bold;">{patient_info.get('doctor', 'Not found')}</span>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    # No patient info found
                    st.info("ℹ️ Patient information could not be extracted from the report. This is optional and analysis can proceed without it.")
                
                st.divider()
                try:
                    parser = ReportParser()
                    parsed_results = parser.parse_report(extracted_data, gender)
                except Exception as parse_error:
                    st.error(f"❌ Error parsing report: {str(parse_error)}")
                    with st.expander("Debug Information"):
                        st.write(f"Data type: {type(extracted_data)}")
                        st.write(f"Data keys: {list(extracted_data.keys()) if isinstance(extracted_data, dict) else 'N/A'}")
                        st.code(traceback.format_exc())
                    return
                
                if not parsed_results:
                    st.warning("⚠️ No valid blood parameters were parsed from the extracted data.")
                    return
                
                analyzer = _get_analyzer()
                analysis = analyzer.analyze(parsed_results)
                
                summary_gen = _get_summary_gen()
                ai_summary = summary_gen.generate_summary(analysis)
                
                st.session_state.analysis = analysis
                st.session_state.ai_summary = ai_summary
                st.session_state.analysis_complete = True
                st.session_state.patient_info = patient_info

                # Auto-save report to MySQL
                try:
                    db_save_report(
                        st.session_state.username,
                        uploaded_file.name,
                        patient_info,
                        analysis,
                        ai_summary
                    )
                except Exception as _save_err:
                    print(f"Report save warning: {_save_err}")
                
                if not st.session_state.chatbot:
                    chatbot = _get_chatbot()
                    chatbot.set_report_context(ai_summary)
                    st.session_state.chatbot = chatbot
                
                display_results(analysis, ai_summary)
                display_ai_assistant()
                
            except Exception as e:
                st.error(f"❌ Error processing report: {str(e)}")
                with st.expander("Error Details"):
                    st.code(traceback.format_exc())
            finally:
                # Clean up temp file
                if temp_path and os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except:
                        pass
    
    elif st.session_state.analysis_complete:
        display_results(st.session_state.analysis, st.session_state.ai_summary)
        display_ai_assistant()

def _generate_pdf_report(analysis: dict, ai_summary: str) -> bytes:
    """Generate a patient-friendly PDF report using ReportLab."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from io import BytesIO
    import datetime

    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    green = colors.HexColor('#16A085')
    light_green = colors.HexColor('#D5F4E6')
    red = colors.HexColor('#E74C3C')
    orange = colors.HexColor('#F39C12')

    title_style = ParagraphStyle('title', parent=styles['Title'],
                                  textColor=green, fontSize=20, spaceAfter=4)
    h2_style    = ParagraphStyle('h2', parent=styles['Heading2'],
                                  textColor=green, fontSize=13, spaceBefore=12, spaceAfter=4)
    body_style  = ParagraphStyle('body', parent=styles['Normal'], fontSize=9, leading=13)
    small_style = ParagraphStyle('small', parent=styles['Normal'], fontSize=8,
                                  textColor=colors.grey)

    story = []

    # Header
    story.append(Paragraph('🩺 AIMedi Health Diagnostics Report', title_style))
    story.append(Paragraph(f'Generated: {datetime.datetime.now().strftime("%d %b %Y, %I:%M %p")}', small_style))
    story.append(HRFlowable(width='100%', color=green, thickness=1.5, spaceAfter=8))

    # Risk summary
    risk = analysis['risk_assessment']
    story.append(Paragraph('Health Risk Summary', h2_style))
    risk_color = {'Minimal': green, 'Low': green, 'Moderate': orange,
                  'High': red, 'Critical': red}.get(risk['risk_level'], colors.black)
    risk_data = [
        ['Overall Risk Score', 'Risk Level', 'Critical Findings'],
        [str(risk['overall_risk_score']) + '/100',
         risk['risk_level'],
         str(len(analysis.get('critical_findings', [])))]
    ]
    risk_table = Table(risk_data, colWidths=[5.5*cm, 5.5*cm, 5.5*cm])
    risk_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), green),
        ('TEXTCOLOR',  (0,0), (-1,0), colors.white),
        ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',   (0,0), (-1,-1), 9),
        ('ALIGN',      (0,0), (-1,-1), 'CENTER'),
        ('BACKGROUND', (0,1), (-1,1), light_green),
        ('GRID',       (0,0), (-1,-1), 0.5, colors.white),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [light_green]),
        ('TEXTCOLOR',  (1,1), (1,1), risk_color),
        ('FONTNAME',   (1,1), (1,1), 'Helvetica-Bold'),
    ]))
    story.append(risk_table)
    story.append(Spacer(1, 0.4*cm))

    # Detailed results table
    story.append(Paragraph('Detailed Test Results', h2_style))
    table_data = [['Parameter', 'Value', 'Unit', 'Status', 'Reference Range']]
    for r in analysis['results']:
        status = r['status']
        table_data.append([
            r['parameter'].replace('_', ' ').title(),
            str(r['value']),
            r.get('unit', ''),
            status,
            f"{r['reference_min']} – {r['reference_max']}"
        ])
    col_w = [4.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 4.5*cm]
    results_table = Table(table_data, colWidths=col_w, repeatRows=1)
    row_styles = [
        ('BACKGROUND', (0,0), (-1,0), green),
        ('TEXTCOLOR',  (0,0), (-1,0), colors.white),
        ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',   (0,0), (-1,-1), 8),
        ('ALIGN',      (0,0), (-1,-1), 'CENTER'),
        ('GRID',       (0,0), (-1,-1), 0.4, colors.lightgrey),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_green]),
    ]
    for i, r in enumerate(analysis['results'], start=1):
        if r['status'] == 'High':
            row_styles.append(('TEXTCOLOR', (3,i), (3,i), red))
            row_styles.append(('FONTNAME',  (3,i), (3,i), 'Helvetica-Bold'))
        elif r['status'] == 'Low':
            row_styles.append(('TEXTCOLOR', (3,i), (3,i), orange))
            row_styles.append(('FONTNAME',  (3,i), (3,i), 'Helvetica-Bold'))
    results_table.setStyle(TableStyle(row_styles))
    story.append(results_table)
    story.append(Spacer(1, 0.4*cm))

    # AI Summary
    story.append(Paragraph('AI-Generated Health Summary', h2_style))
    story.append(HRFlowable(width='100%', color=light_green, thickness=1))
    story.append(Spacer(1, 0.2*cm))
    # Strip markdown bold/italic for PDF
    import re
    clean_summary = re.sub(r'\*{1,2}(.*?)\*{1,2}', r'\1', ai_summary)
    for line in clean_summary.split('\n'):
        line = line.strip()
        if line:
            story.append(Paragraph(line, body_style))

    # Disclaimer
    story.append(Spacer(1, 0.6*cm))
    story.append(HRFlowable(width='100%', color=colors.lightgrey, thickness=0.5))
    story.append(Paragraph(
        '⚠️ Disclaimer: This report is for informational purposes only and is not a substitute '
        'for professional medical advice. Always consult a qualified healthcare provider.',
        ParagraphStyle('disc', parent=styles['Normal'], fontSize=7,
                       textColor=colors.grey, spaceBefore=4)
    ))

    doc.build(story)
    return buf.getvalue()


def display_results(analysis, ai_summary):
    st.divider()
    
    st.markdown('<h2 class="sub-header">📊 Health Risk Assessment</h2>', unsafe_allow_html=True)
    
    risk_data = analysis['risk_assessment']
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="health-metric" style="text-align: center;">
            <div style="font-size: 2rem; font-weight: bold; color: #1ABC9C;">
                {risk_data['overall_risk_score']}/100
            </div>
            <div class="health-metric-title">Overall Risk Score</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        risk_level = risk_data['risk_level']
        color_emoji = {
            'Minimal': '🟢',
            'Low': '🟡',
            'Moderate': '🟠',
            'High': '🔴',
            'Critical': '🔴'
        }.get(risk_level, '⚪')
        st.markdown(f"""
        <div class="health-metric" style="text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">
                {color_emoji}
            </div>
            <div class="health-metric-title">{risk_level}</div>
            <div style="color: #16A085; font-size: 0.9rem;">Risk Level</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        critical_count = len(analysis.get('critical_findings', []))
        st.markdown(f"""
        <div class="health-metric" style="text-align: center;">
            <div style="font-size: 2rem; font-weight: bold; color: #E74C3C;">
                {critical_count}
            </div>
            <div class="health-metric-title">Critical Findings</div>
        </div>
        """, unsafe_allow_html=True)
    
    charts = DashboardCharts()
    risk_gauge = charts.create_risk_gauge(
        risk_data['overall_risk_score'],
        risk_data['risk_level']
    )
    st.plotly_chart(risk_gauge, use_container_width=True)
    
    risk_breakdown = charts.create_risk_breakdown(risk_data['risks'])
    if risk_breakdown:
        st.plotly_chart(risk_breakdown, use_container_width=True)
    
    st.divider()
    
    st.markdown('<h2 class="sub-header">🤖 AI-Generated Health Summary</h2>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    st.markdown(ai_summary)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()
    
    st.markdown('<h2 class="sub-header">📋 Detailed Test Results</h2>', unsafe_allow_html=True)
    
    results_df = pd.DataFrame([
        {
            'Parameter': r['parameter'].replace('_', ' ').title(),
            'Value': f"{r['value']} {r.get('unit', '')}",
            'Status': r['status'],
            'Severity': r.get('severity', 'Normal'),
            'Reference Range': f"{r['reference_min']}-{r['reference_max']}"
        }
        for r in analysis['results']
    ])
    
    st.dataframe(
        results_df,
        use_container_width=True,
        hide_index=True
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        param_chart = charts.create_parameter_comparison(analysis['results'])
        if param_chart:
            st.plotly_chart(param_chart, use_container_width=True)
    
    with col2:
        severity_pie = charts.create_severity_pie(analysis['results'])
        st.plotly_chart(severity_pie, use_container_width=True)
    
    if analysis.get('critical_findings'):
        st.markdown('<h2 class="sub-header">⚠️ Critical Findings</h2>', unsafe_allow_html=True)
        st.markdown('<div class="critical-box">', unsafe_allow_html=True)
        for finding in analysis['critical_findings']:
            st.warning(f"**{finding['parameter'].replace('_', ' ').title()}**: {finding['value']} {finding.get('unit', '')} - {finding.get('severity', 'Critical')}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<h3 style="color: #16A085;">📥 Download Report</h3>', unsafe_allow_html=True)

        # --- PDF ---
        try:
            pdf_bytes = _generate_pdf_report(analysis, ai_summary)
            st.download_button(
                label="📄 Download PDF Report",
                data=pdf_bytes,
                file_name="health_report.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as _e:
            st.warning(f"PDF generation failed: {_e}")

        # --- CSV ---
        results_csv = pd.DataFrame([
            {
                'Parameter': r['parameter'].replace('_', ' ').title(),
                'Value': r['value'],
                'Unit': r.get('unit', ''),
                'Status': r['status'],
                'Severity': r.get('severity', 'Normal'),
                'Reference Min': r['reference_min'],
                'Reference Max': r['reference_max']
            }
            for r in analysis['results']
        ]).to_csv(index=False)
        st.download_button(
            label="📊 Download CSV (Results Table)",
            data=results_csv,
            file_name="health_report.csv",
            mime="text/csv",
            use_container_width=True
        )

        # --- JSON ---
        report_json = json.dumps({'analysis': analysis, 'ai_summary': ai_summary}, indent=2)
        st.download_button(
            label="🗂️ Download JSON (Full Data)",
            data=report_json,
            file_name="health_report.json",
            mime="application/json",
            use_container_width=True
        )

    with col2:
        st.markdown('<h3 style="color: #16A085;">📊 Health Tips</h3>', unsafe_allow_html=True)
        st.markdown("""
        <div class="info-box">
        <strong>💡 Healthy Lifestyle Tips:</strong>
        <ul>
            <li>🥗 Eat a balanced diet with vegetables and fruits</li>
            <li>💪 Exercise regularly for 30 minutes daily</li>
            <li>😴 Get 7-8 hours of quality sleep</li>
            <li>💧 Drink plenty of water</li>
            <li>🚫 Avoid smoking and excessive alcohol</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

def display_ai_assistant():
    if not st.session_state.analysis_complete:
        return
    
    st.divider()
    st.markdown('<h2 class="sub-header">💬 AI Health Assistant</h2>', unsafe_allow_html=True)
    
    if not st.session_state.chatbot:
        chatbot = _get_chatbot()
        chatbot.set_report_context(st.session_state.ai_summary)
        st.session_state.chatbot = chatbot
    
    st.markdown("""
    <div class="info-box">
    <strong>💡 Ask me anything about your blood test results!</strong><br>
    <em>Example questions:</em>
    <ul>
        <li>What does my LDL level mean?</li>
        <li>How can I increase my hemoglobin levels?</li>
        <li>What foods can improve my hemoglobin?</li>
        <li>Should I see a doctor immediately?</li>
        <li>How can I lower my cholesterol naturally?</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("Ask about your health..."):
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = st.session_state.chatbot.chat(prompt)
                st.markdown(response)
        
        st.session_state.chat_messages.append({"role": "assistant", "content": response})
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        pass
    
    with col2:
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.chat_messages = []
            st.session_state.chatbot.clear_history()
            st.success("✅ Chat history cleared!")
            st.rerun()

def report_history_page():
    st.markdown('<h2 class="sub-header">📋 Report History</h2>', unsafe_allow_html=True)

    reports = db_get_user_reports(st.session_state.username)

    if not reports:
        st.info("ℹ️ No reports found. Upload a blood report to get started!")
        return

    st.success(f"✅ Found **{len(reports)}** report(s) in your history")

    for r in reports:
        risk_emoji = {'Minimal': '🟢', 'Low': '🟡', 'Moderate': '🟠',
                      'High': '🔴', 'Critical': '🔴'}.get(r['risk_level'], '⚪')
        label = f"{risk_emoji} {r['created_at'].strftime('%d %b %Y %I:%M %p')} — {r['filename'] or 'Report'} | Risk: {r['risk_level']} ({r['risk_score']}/100)"

        with st.expander(label):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"**👤 Patient:** {r['patient_name'] or 'N/A'}")
                st.markdown(f"**🎂 Age:** {r['patient_age'] or 'N/A'}")
            with col2:
                st.markdown(f"**⚕️ Gender:** {r['patient_gender'] or 'N/A'}")
                st.markdown(f"**📅 Report Date:** {r['report_date'] or 'N/A'}")
            with col3:
                st.markdown(f"**🎯 Risk Score:** {r['risk_score']}/100")
                st.markdown(f"**🚨 Risk Level:** {r['risk_level']}")

            # Load full details
            detail = db_get_report_detail(r['id'])
            if detail.get('parameters'):
                st.markdown("**🩸 Blood Parameters:**")
                params_df = pd.DataFrame([
                    {
                        'Parameter': p['parameter'].replace('_', ' ').title(),
                        'Value': p['value'],
                        'Unit': p['unit'],
                        'Status': p['status'],
                        'Reference Range': f"{p['ref_min']} - {p['ref_max']}"
                    }
                    for p in detail['parameters']
                ])
                st.dataframe(params_df, use_container_width=True, hide_index=True)

            if detail.get('ai_summary'):
                with st.expander("🤖 View AI Summary"):
                    st.markdown(detail['ai_summary'])

            if st.button(f"🗑️ Delete Report", key=f"del_{r['id']}"):
                if db_delete_report(r['id']):
                    st.success("✅ Report deleted!")
                    st.rerun()


def about_page():
    st.markdown('<h2 class="sub-header">ℹ️ About This Application</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    ### 🏥 AI Health Diagnostics Assistant
    
    An advanced AI-powered blood report analysis system that helps you understand your health better.
    
    #### ✨ Features:
    - **PDF & Image Upload**: Upload blood test reports in PDF or image format (PNG, JPG)
    - **OCR Support**: Extract text from scanned documents using advanced OCR technology
    - **Smart Extraction**: Automatically extracts blood parameters
    - **Risk Assessment**: Analyzes potential health risks
    - **AI Summaries**: Generates easy-to-understand health summaries
    - **Personalized Recommendations**: Get tailored health advice
    - **Integrated AI Assistant**: Ask questions directly below your results
    - **RAG-based Chat**: Ask questions with knowledge-grounded responses
    - **Interactive Dashboards**: Visualize your health data
    
    #### 🛠️ Technology Stack:
    - **Frontend**: Streamlit
    - **AI Model**: Groq (Llama 3.3 70B)
    - **OCR**: Tesseract OCR with OpenCV preprocessing
    - **Vector Database**: FAISS
    - **Embeddings**: Sentence Transformers
    - **PDF Processing**: PDFPlumber
    - **Visualization**: Plotly
    
    #### 📝 How to Use:
    1. **Login** with your credentials
    2. **Upload your report**: Choose PDF or image file
    3. **Enable OCR**: Check "Use OCR" for scanned documents
    4. **View Results**: See risk assessment and detailed analysis
    5. **Chat with AI**: Ask questions about your results below the recommendations
    
    #### ⚠️ Important Disclaimer:
    This tool is for informational purposes only and should not replace professional medical advice. 
    Always consult with a qualified healthcare provider for medical decisions.
    
    #### 🔒 Privacy:
    - Your data is processed locally
    - Reports are not stored permanently
    - No data is shared with third parties
    
    ---
    **Version**: 1.3.0  
    **Theme**: Medical Green Design  
    **Developer**: AI Health Team  
     """)

def display_footer():
    st.markdown("""
    <div class="footer">
        <hr style="border: 1px solid rgba(255,255,255,0.3); margin: 1rem 0;">
        <p>💚 <strong>AIMedi Health Diagnostics</strong> - Your AI-Powered Health Partner</p>
        <p>📧 Email: <a href="mailto:ansarisalmanmd091@gmail.com">ansarisalmanmd091@gmail.com</a> | 📱 Phone: <a href="tel:+919199510341">+91 9199510341</a></p>
        <p>
            <span class="metric-badge">Privacy Protected 🔒</span>
            <span class="metric-badge">AI Powered 🤖</span>
            <span class="metric-badge">HIPAA Compliant ✓</span>
        </p>
        <p style="margin-top: 1rem; opacity: 0.8;">
            ⚕️ <em>This application is for educational purposes only. Always consult with a licensed healthcare professional.</em>
        </p>
        <p style="opacity: 0.7; font-size: 0.9rem;">
            © 2026 AIMedi Health Assistant. All rights reserved.
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()