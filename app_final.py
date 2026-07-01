import streamlit as st
import os
from dotenv import load_dotenv
import json
from report_processing.extractor import BloodReportExtractor
from report_processing.parser import ReportParser
from report_processing.normalizer import DataNormalizer
from report_processing.report_generator import ReportGenerator
from analytics.analyzer import HealthAnalyzer
from ai.summary_generator import SummaryGenerator
from ai.chatbot import HealthChatbot
from dashboard.charts import DashboardCharts
import pandas as pd
from datetime import datetime

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI Health Diagnostics Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .patient-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 1rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .patient-card h3 {
        color: white;
        margin-top: 0;
    }
    .info-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 1rem;
        margin: 1rem 0;
    }
    .download-section {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 1rem;
        margin: 1rem 0;
        border: 2px solid #e9ecef;
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
if 'patient_info' not in st.session_state:
    st.session_state.patient_info = {}

def main():
    # Header
    st.markdown('<h1 class="main-header">🏥 AI Health Diagnostics Assistant</h1>', unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666; font-size: 1.1rem;'> Real-time Patient Info • Multi-format Reports</p>", unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🎯 Navigation")
        
        page = st.radio(
            "Select Page",
            ["🏠 Home", "📤 Upload & Analyze", "📥 Download Reports", "💬 AI Assistant", "ℹ️ About"],
            index=0,
            label_visibility="collapsed"
        )
        
        st.divider()
        
        st.markdown("### ⚙️ Settings")
        gender = st.selectbox("👤 Gender", ["male", "female", "None"], help="Select your gender for accurate reference ranges")
        
        st.divider()
        
        # Patient Info Display in Sidebar
        if st.session_state.patient_info and any(st.session_state.patient_info.values()):
            st.markdown("### 👤 Patient Info")
            if st.session_state.patient_info.get('name'):
                st.info(f"**{st.session_state.patient_info['name']}**")
            if st.session_state.patient_info.get('age'):
                st.metric("Age", f"{st.session_state.patient_info['age']} yrs")
            if st.session_state.patient_info.get('gender'):
                st.metric("Gender", st.session_state.patient_info['gender'])
            st.divider()
        
        if st.button("🗑️ Clear All Data", use_container_width=True):
            st.session_state.analysis_complete = False
            st.session_state.chat_messages = []
            st.session_state.chatbot = None
            st.session_state.upload_mode = None
            st.session_state.patient_info = {}
            st.success("✅ Data cleared!")
            st.rerun()
        
        st.divider()
        st.markdown("### 📊 Quick Stats")
        if st.session_state.analysis_complete:
            st.metric("Parameters", len(st.session_state.analysis['results']))
            st.metric("Risk Level", st.session_state.analysis['risk_assessment']['risk_level'])
    
    # Check API Key
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key or api_key == 'your_groq_api_key_here':
        st.error("⚠️ Please configure your GROQ_API_KEY in the .env file!")
        st.info("Get your API key from: https://console.groq.com/keys")
        st.stop()
    
    # Page routing
    if page == "🏠 Home":
        home_page()
    elif page == "📤 Upload & Analyze":
        upload_analyze_page(gender)
    elif page == "📥 Download Reports":
        download_reports_page()
    elif page == "💬 AI Assistant":
        ai_assistant_page()
    elif page == "ℹ️ About":
        about_page()

def home_page():
    """Enhanced home page"""
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="info-box">
            <h3 style="color: white;">📤 Upload Reports</h3>
            <p>PDF, Images, Scanned docs<br/>OCR supported!</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); padding: 1.5rem; border-radius: 1rem; color: white;'>
            <h3 style="color: white;">👤 Patient Info</h3>
            <p>Auto-extracts name,<br/>age, gender in real-time</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); padding: 1.5rem; border-radius: 1rem; color: white;'>
            <h3 style="color: white;">📥 Download</h3>
            <p>PDF, CSV, JSON<br/>Multiple formats!</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("## ✨ What's New in V2.0")
    
    features_col1, features_col2 = st.columns(2)
    
    with features_col1:
        st.markdown("""
        ### 🆕 Real-time Patient Information
        - **Auto-extract** patient name
        - **Age detection** from reports
        - **Gender identification**
        - **Report date & ID**
        - **Referring doctor** information
        - Displayed instantly as you upload!
        
        ### 📥 Multiple Download Formats
        - **PDF Report** - Professional layout
        - **CSV Export** - For Excel/Sheets
        - **JSON Data** - For developers
        - All formats include patient info
        """)
    
    with features_col2:
        st.markdown("""
        ### 🔍 Enhanced OCR
        - Upload scanned documents
        - Take photos with phone
        - Image file support (JPG/PNG)
        - Smart text extraction
        
        ### 🤖 AI-Powered Analysis
        - 18+ blood parameters
        - Risk assessment
        - Severity classification
        - Patient-friendly summaries
        - Interactive chatbot
        """)
    
    if not st.session_state.analysis_complete:
        st.info("👉 Go to **Upload & Analyze** to get started!")

def upload_analyze_page(gender):
    st.markdown("## 📤 Upload Blood Report")
    
    # Upload options
    st.markdown("### Choose Upload Method:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 1rem; color: white; text-align: center;'>
            <h3 style='color: white; margin: 0;'>📄 Digital PDF</h3>
            <p style='margin: 0.5rem 0;'>Text-based reports</p>
            <p style='font-size: 0.9rem; margin: 0;'>✅ Fastest</p>
        </div>
        """, unsafe_allow_html=True)
        digital_pdf = st.button("Upload Digital PDF", key="btn_digital", use_container_width=True)
    
    with col2:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 1.5rem; border-radius: 1rem; color: white; text-align: center;'>
            <h3 style='color: white; margin: 0;'>🔍 Scanned PDF</h3>
            <p style='margin: 0.5rem 0;'>Image-based PDFs</p>
            <p style='font-size: 0.9rem; margin: 0;'>📸 OCR</p>
        </div>
        """, unsafe_allow_html=True)
        scanned_pdf = st.button("Upload Scanned PDF (OCR)", key="btn_scanned", use_container_width=True)
    
    with col3:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); padding: 1.5rem; border-radius: 1rem; color: white; text-align: center;'>
            <h3 style='color: white; margin: 0;'>🖼️ Image</h3>
            <p style='margin: 0.5rem 0;'>JPG, PNG photos</p>
            <p style='font-size: 0.9rem; margin: 0;'>📱 Phone</p>
        </div>
        """, unsafe_allow_html=True)
        image_file = st.button("Upload Image (OCR)", key="btn_image", use_container_width=True)
    
    # Set upload mode
    if 'upload_mode' not in st.session_state:
        st.session_state.upload_mode = None
    
    if digital_pdf:
        st.session_state.upload_mode = 'digital_pdf'
    elif scanned_pdf:
        st.session_state.upload_mode = 'scanned_pdf'
    elif image_file:
        st.session_state.upload_mode = 'image'
    
    # Show file uploader
    if st.session_state.upload_mode:
        st.divider()
        
        if st.session_state.upload_mode == 'digital_pdf':
            st.info("📄 **Digital PDF Mode** - Fast processing")
            uploaded_file = st.file_uploader("Upload PDF", type=['pdf'], key="uploader_digital")
            use_ocr = False
        elif st.session_state.upload_mode == 'scanned_pdf':
            st.warning("🔍 **Scanned PDF Mode** - OCR enabled (30-60 sec)")
            uploaded_file = st.file_uploader("Upload Scanned PDF", type=['pdf'], key="uploader_scanned")
            use_ocr = True
        elif st.session_state.upload_mode == 'image':
            st.warning("🖼️ **Image Mode** - OCR enabled (20-40 sec)")
            uploaded_file = st.file_uploader("Upload Image", type=['jpg', 'jpeg', 'png'], key="uploader_image")
            use_ocr = True
    else:
        st.info("👆 **Select an upload method above!**")
        uploaded_file = None
    
    if uploaded_file:
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.success(f"✅ {uploaded_file.name}")
        with col2:
            st.info(f"📏 {uploaded_file.size / 1024:.1f} KB")
        with col3:
            mode_icons = {'digital_pdf': '⚡', 'scanned_pdf': '🔍', 'image': '🖼️'}
            st.info(mode_icons.get(st.session_state.upload_mode, ''))
        
        if st.button("🔬 Analyze Report", type="primary", use_container_width=True):
            with st.spinner("🔄 Processing..."):
                try:
                    temp_path = f"temp_{uploaded_file.name}"
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    extractor = BloodReportExtractor()
                    
                    # Extract with patient info
                    if st.session_state.upload_mode == 'image':
                        extracted_data, patient_info = extractor.extract_from_image(temp_path)
                    else:
                        extracted_data, patient_info = extractor.extract_from_pdf(temp_path, use_ocr=use_ocr)
                    
                    os.remove(temp_path)
                    
                    # Store patient info
                    st.session_state.patient_info = patient_info
                    
                    # Display patient info immediately
                    if patient_info and any(patient_info.values()):
                        st.markdown("### 👤 Patient Information (Real-time)")
                        st.markdown('<div class="patient-card">', unsafe_allow_html=True)
                        
                        pcol1, pcol2, pcol3, pcol4 = st.columns(4)
                        with pcol1:
                            if patient_info.get('name'):
                                st.metric("Name", patient_info['name'])
                        with pcol2:
                            if patient_info.get('age'):
                                st.metric("Age", f"{patient_info['age']} years")
                        with pcol3:
                            if patient_info.get('gender'):
                                st.metric("Gender", patient_info['gender'])
                        with pcol4:
                            if patient_info.get('report_date'):
                                st.metric("Report Date", patient_info['report_date'])
                        
                        if patient_info.get('report_id'):
                            st.info(f"📋 **Report ID:** {patient_info['report_id']}")
                        if patient_info.get('doctor'):
                            st.info(f"👨⚕️ **Referred By:** Dr. {patient_info['doctor']}")
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    if not extracted_data:
                        st.error("❌ No blood parameters found")
                        return
                    
                    st.success(f"✅ Extracted {len(extracted_data)} parameters!")
                    
                    # Continue analysis
                    parser = ReportParser()
                    parsed_results = parser.parse_report(extracted_data, gender)
                    
                    analyzer = HealthAnalyzer()
                    analysis = analyzer.analyze(parsed_results)
                    
                    summary_gen = SummaryGenerator()
                    ai_summary = summary_gen.generate_summary(analysis)
                    
                    st.session_state.analysis = analysis
                    st.session_state.ai_summary = ai_summary
                    st.session_state.analysis_complete = True
                    
                    if not st.session_state.chatbot:
                        st.session_state.chatbot = HealthChatbot()
                        st.session_state.chatbot.set_report_context(ai_summary)
                    
                    display_results(analysis, ai_summary)
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.exception(e)
    
    elif st.session_state.analysis_complete:
        st.divider()
        st.info("📊 Showing previous analysis")
        display_results(st.session_state.analysis, st.session_state.ai_summary)

def display_results(analysis, ai_summary):
    """Display analysis results"""
    st.divider()
    st.markdown("## 📊 Analysis Results")
    
    # Risk metrics
    risk_data = analysis['risk_assessment']
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Risk Score", f"{risk_data['overall_risk_score']}/100")
    with col2:
        colors_map = {'Minimal': '🟢', 'Low': '🟡', 'Moderate': '🟠', 'High': '🔴', 'Critical': '🔴'}
        st.metric("Risk Level", f"{colors_map.get(risk_data['risk_level'], '⚪')} {risk_data['risk_level']}")
    with col3:
        st.metric("Critical Findings", len(analysis.get('critical_findings', [])))
    
    # Charts
    charts = DashboardCharts()
    col1, col2 = st.columns(2)
    
    with col1:
        risk_gauge = charts.create_risk_gauge(risk_data['overall_risk_score'], risk_data['risk_level'])
        st.plotly_chart(risk_gauge, use_container_width=True)
    
    with col2:
        risk_breakdown = charts.create_risk_breakdown(risk_data['risks'])
        if risk_breakdown:
            st.plotly_chart(risk_breakdown, use_container_width=True)
    
    # AI Summary
    st.markdown("## 🤖 AI Health Summary")
    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    st.markdown(ai_summary)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Results table
    st.markdown("## 📋 Test Results")
    results_df = pd.DataFrame([
        {
            'Parameter': r['parameter'].replace('_', ' ').title(),
            'Value': f"{r['value']} {r.get('unit', '')}",
            'Status': r['status'],
            'Severity': r.get('severity', 'Normal'),
            'Reference': f"{r['reference_min']}-{r['reference_max']}"
        }
        for r in analysis['results']
    ])
    st.dataframe(results_df, use_container_width=True, hide_index=True)

def download_reports_page():
    """Download reports page with multiple formats"""
    st.markdown("## 📥 Download Reports")
    
    if not st.session_state.analysis_complete:
        st.warning("⚠️ No analysis available. Please upload and analyze a report first!")
        st.info("Go to **Upload & Analyze** to get started.")
        return
    
    st.success("✅ Reports ready for download!")
    
    # Generate reports
    generator = ReportGenerator()
    
    st.markdown('<div class="download-section">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📄 PDF Report")
        st.markdown("Professional formatted report with patient info, analysis, and charts.")
        
        try:
            pdf_bytes = generator.generate_pdf_report(
                st.session_state.analysis,
                st.session_state.ai_summary,
                st.session_state.patient_info
            )
            
            patient_name = st.session_state.patient_info.get('name', 'Patient').replace(' ', '_')
            filename = f"Health_Report_{patient_name}_{datetime.now().strftime('%Y%m%d')}.pdf"
            
            st.download_button(
                label="📥 Download PDF",
                data=pdf_bytes,
                file_name=filename,
                mime="application/pdf",
                use_container_width=True,
                type="primary"
            )
        except Exception as e:
            st.error(f"Error generating PDF: {str(e)}")
    
    with col2:
        st.markdown("### 📊 CSV Export")
        st.markdown("Spreadsheet format for Excel, Google Sheets, or data analysis.")
        
        try:
            csv_data = generator.generate_csv_report(
                st.session_state.analysis,
                st.session_state.patient_info
            )
            
            patient_name = st.session_state.patient_info.get('name', 'Patient').replace(' ', '_')
            filename = f"Health_Report_{patient_name}_{datetime.now().strftime('%Y%m%d')}.csv"
            
            st.download_button(
                label="📥 Download CSV",
                data=csv_data,
                file_name=filename,
                mime="text/csv",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Error generating CSV: {str(e)}")
    
    with col3:
        st.markdown("### 💾 JSON Data")
        st.markdown("Machine-readable format for developers and integrations.")
        
        try:
            json_data = generator.generate_json_report(
                st.session_state.analysis,
                st.session_state.ai_summary,
                st.session_state.patient_info
            )
            
            patient_name = st.session_state.patient_info.get('name', 'Patient').replace(' ', '_')
            filename = f"Health_Report_{patient_name}_{datetime.now().strftime('%Y%m%d')}.json"
            
            st.download_button(
                label="📥 Download JSON",
                data=json_data,
                file_name=filename,
                mime="application/json",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Error generating JSON: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Preview section
    st.divider()
    st.markdown("### 👁️ Preview Report Content")
    
    preview_format = st.selectbox("Select format to preview:", ["Patient Info", "Test Results", "Risk Assessment"])
    
    if preview_format == "Patient Info":
        if st.session_state.patient_info:
            st.json(st.session_state.patient_info)
        else:
            st.info("No patient information extracted")
    
    elif preview_format == "Test Results":
        st.dataframe(pd.DataFrame(st.session_state.analysis['results']), use_container_width=True)
    
    elif preview_format == "Risk Assessment":
        st.json(st.session_state.analysis['risk_assessment'])

def ai_assistant_page():
    """AI Chat assistant page"""
    st.markdown("## 💬 AI Health Assistant")
    
    if not st.session_state.analysis_complete:
        st.info("👆 Upload a report first!")
        return
    
    if not st.session_state.chatbot:
        st.session_state.chatbot = HealthChatbot()
        st.session_state.chatbot.set_report_context(st.session_state.ai_summary)
    
    st.markdown('<div class="info-box"><h4 style="color: white;">💡 Ask me anything about your results!</h4></div>', unsafe_allow_html=True)
    
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
        st.rerun()
    
    if st.session_state.chat_messages and st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.chat_messages = []
        st.session_state.chatbot.clear_history()
        st.rerun()

def about_page():
    """About page"""
    st.markdown("## ℹ️ About")
    st.markdown("""
    ### AI Health Diagnostics Assistant V2.0
    
    **New Features:**
    - 👤 Real-time patient information extraction
    - 📥 Multiple download formats (PDF, CSV, JSON)
    - 🔍 Enhanced OCR support
    - 📱 Image upload from phone
    - 🎨 Modern UI/UX
    
    **Technology:** Groq AI • LangChain • FAISS • Tesseract OCR • ReportLab
    
    **Disclaimer:** For informational purposes only. Consult healthcare professionals for medical advice.
    """)

if __name__ == "__main__":
    main()
