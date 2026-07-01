import streamlit as st
import os
from dotenv import load_dotenv
import json
from report_processing.extractor import BloodReportExtractor
from report_processing.parser import ReportParser
from report_processing.normalizer import DataNormalizer
from analytics.analyzer import HealthAnalyzer
from ai.summary_generator import SummaryGenerator
from ai.chatbot import HealthChatbot
from dashboard.charts import DashboardCharts
import pandas as pd

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
    .sub-header {
        font-size: 1.8rem;
        color: #2c3e50;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    .info-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 1rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .success-box {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 1rem;
        margin: 1rem 0;
    }
    .critical-box {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        margin: 1rem 0;
    }
    .stButton>button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 0.5rem;
        border: none;
        padding: 0.5rem 2rem;
        font-weight: 600;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 0.8rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: bold;
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
if 'use_ocr' not in st.session_state:
    st.session_state.use_ocr = False

def main():
    # Header
    st.markdown('<h1 class="main-header">🏥 AI Health Diagnostics Assistant</h1>', unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666; font-size: 1.1rem;'>Powered by Groq AI • Advanced Blood Report Analysis with OCR</p>", unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🎯 Navigation")
        
        page = st.radio(
            "Select Page",
            ["🏠 Home", "📤 Upload & Analyze", "💬 AI Assistant", "ℹ️ About"],
            index=0,
            label_visibility="collapsed"
        )
        
        st.divider()
        
        st.markdown("### ⚙️ Settings")
        gender = st.selectbox("👤 Gender", ["male", "female"], help="Select your gender for accurate reference ranges")
        
        st.divider()
        
        if st.button("🗑️ Clear All Data", use_container_width=True):
            st.session_state.analysis_complete = False
            st.session_state.chat_messages = []
            st.session_state.chatbot = None
            st.session_state.upload_mode = None
            st.success("✅ Data cleared!")
            st.rerun()
        
        st.divider()
        st.markdown("### 📊 Quick Stats")
        if st.session_state.analysis_complete:
            st.metric("Parameters Analyzed", len(st.session_state.analysis['results']))
            st.metric("Risk Level", st.session_state.analysis['risk_assessment']['risk_level'])
    
    # Check API Key
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        st.error("⚠️ Please configure your GROQ_API_KEY in the .env file!")
        st.info("Get your API key from: https://console.groq.com/keys")
        st.stop()
    
    # Validate API key format
    if not api_key.startswith('gsk_') or len(api_key) < 30:
        st.error("⚠️ Invalid GROQ_API_KEY format!")
        st.warning("🔑 API key should start with 'gsk_' and be at least 30 characters")
        st.info("Get a valid API key from: https://console.groq.com/keys")
        st.stop()
    
    # Page routing
    if page == "🏠 Home":
        home_page()
    elif page == "📤 Upload & Analyze":
        upload_analyze_page(gender)
    elif page == "💬 AI Assistant":
        ai_assistant_page()
    elif page == "ℹ️ About":
        about_page()

def home_page():
    """Enhanced home page with better UI"""
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="info-box">
            <h3 style="color: white;">📤 Upload Reports</h3>
            <p>Upload PDF blood reports or images. OCR supported for scanned documents!</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="success-box">
            <h3 style="color: white;">🤖 AI Analysis</h3>
            <p>Get instant AI-powered health insights and risk assessments.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="warning-box">
            <h3 style="color: white;">💬 Chat Assistant</h3>
            <p>Ask questions about your results and get personalized advice.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Features section
    st.markdown('<h2 class="sub-header">✨ Key Features</h2>', unsafe_allow_html=True)
    
    features = {
        "🔍 OCR Support": "Upload scanned PDFs or images - our OCR engine extracts text automatically",
        "🩺 18+ Parameters": "Analyzes Hemoglobin, HbA1c, Cholesterol, LDL, HDL, Kidney, Liver, Thyroid & more",
        "⚡ Instant Analysis": "Get results in seconds with severity classification and risk scoring",
        "🤖 AI Summaries": "Patient-friendly explanations powered by Groq's Llama 3.3 70B",
        "📊 Visual Dashboards": "Interactive charts, gauges, and graphs to visualize your health",
        "💬 Smart Chatbot": "RAG-powered Q&A system with medical knowledge base"
    }
    
    cols = st.columns(2)
    for idx, (feature, description) in enumerate(features.items()):
        with cols[idx % 2]:
            with st.expander(feature, expanded=False):
                st.write(description)
    
    # Quick start guide
    st.markdown('<h2 class="sub-header">🚀 Quick Start</h2>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        **Step 1**  
        📤 Upload Report  
        Go to Upload & Analyze
        """)
    
    with col2:
        st.markdown("""
        **Step 2**  
        🔍 Enable OCR  
        For scanned PDFs
        """)
    
    with col3:
        st.markdown("""
        **Step 3**  
        📊 View Analysis  
        See risks & insights
        """)
    
    with col4:
        st.markdown("""
        **Step 4**  
        💬 Ask Questions  
        Chat with AI assistant
        """)
    
    if not st.session_state.analysis_complete:
        st.info("👉 Go to **Upload & Analyze** to get started!")

def upload_analyze_page(gender):
    st.markdown('<h2 class="sub-header">📤 Upload Blood Report</h2>', unsafe_allow_html=True)
    
    # Upload options in prominent cards
    st.markdown("### Choose Upload Method:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 1rem; color: white; text-align: center;'>
            <h3 style='color: white; margin: 0;'>📄 Digital PDF</h3>
            <p style='margin: 0.5rem 0;'>Text-based reports</p>
            <p style='font-size: 0.9rem; margin: 0;'>✅ Fastest processing</p>
        </div>
        """, unsafe_allow_html=True)
        digital_pdf = st.button("Upload Digital PDF", key="btn_digital", use_container_width=True)
    
    with col2:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 1.5rem; border-radius: 1rem; color: white; text-align: center;'>
            <h3 style='color: white; margin: 0;'>🔍 Scanned PDF</h3>
            <p style='margin: 0.5rem 0;'>Image-based PDFs</p>
            <p style='font-size: 0.9rem; margin: 0;'>📸 Uses OCR</p>
        </div>
        """, unsafe_allow_html=True)
        scanned_pdf = st.button("Upload Scanned PDF (OCR)", key="btn_scanned", use_container_width=True)
    
    with col3:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); padding: 1.5rem; border-radius: 1rem; color: white; text-align: center;'>
            <h3 style='color: white; margin: 0;'>🖼️ Image File</h3>
            <p style='margin: 0.5rem 0;'>JPG, PNG photos</p>
            <p style='font-size: 0.9rem; margin: 0;'>📱 Phone photos</p>
        </div>
        """, unsafe_allow_html=True)
        image_file = st.button("Upload Image (OCR)", key="btn_image", use_container_width=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Set upload mode based on button click
    if 'upload_mode' not in st.session_state:
        st.session_state.upload_mode = None
    
    if digital_pdf:
        st.session_state.upload_mode = 'digital_pdf'
    elif scanned_pdf:
        st.session_state.upload_mode = 'scanned_pdf'
    elif image_file:
        st.session_state.upload_mode = 'image'
    
    # Show file uploader based on selected mode
    if st.session_state.upload_mode:
        st.divider()
        
        if st.session_state.upload_mode == 'digital_pdf':
            st.info("📄 **Digital PDF Mode** - For text-based PDFs (fastest)")
            uploaded_file = st.file_uploader(
                "Upload your digital blood report PDF",
                type=['pdf'],
                help="Upload a text-based PDF file",
                key="uploader_digital"
            )
            use_ocr = False
            
        elif st.session_state.upload_mode == 'scanned_pdf':
            st.warning("🔍 **Scanned PDF Mode** - OCR will extract text from images (30-60 seconds)")
            
            # Check if OCR is available
            try:
                from report_processing.ocr_processor import OCRProcessor
                st.success("✅ OCR is available and ready!")
                ocr_available = True
            except ImportError:
                st.error("❌ OCR not installed. See OCR_SETUP.md for installation instructions.")
                st.info("Install with: `pip install pytesseract pdf2image opencv-python`")
                ocr_available = False
            
            uploaded_file = st.file_uploader(
                "Upload your scanned blood report PDF",
                type=['pdf'],
                help="Upload a scanned PDF - OCR will extract text",
                key="uploader_scanned"
            )
            use_ocr = True
            
        elif st.session_state.upload_mode == 'image':
            st.warning("🖼️ **Image Mode** - OCR will extract text from image (20-40 seconds)")
            
            # Check if OCR is available
            try:
                from report_processing.ocr_processor import OCRProcessor
                st.success("✅ OCR is available and ready!")
                ocr_available = True
            except ImportError:
                st.error("❌ OCR not installed. See OCR_SETUP.md for installation instructions.")
                st.info("Install with: `pip install pytesseract pdf2image opencv-python`")
                ocr_available = False
            
            uploaded_file = st.file_uploader(
                "Upload blood report image (photo from phone or scanner)",
                type=['jpg', 'jpeg', 'png'],
                help="Upload an image file - OCR will extract text",
                key="uploader_image"
            )
            use_ocr = True
        
        # OCR tips
        if st.session_state.upload_mode in ['scanned_pdf', 'image']:
            with st.expander("💡 Tips for Better OCR Results", expanded=False):
                st.markdown("""
                **For best results:**
                - ✅ Use good lighting when taking photos
                - ✅ Keep the document flat and straight
                - ✅ Use high resolution (300 DPI+)
                - ✅ Ensure text is clear and readable
                - ❌ Avoid blurry or skewed images
                - ❌ Avoid shadows on the document
                
                **Processing Time:**
                - Single page: 30-60 seconds
                - Multiple pages: +15 seconds per page
                """)
    else:
        st.info("👆 **Select an upload method above to get started!**")
        uploaded_file = None
    
    if uploaded_file:
        # Show file info
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.success(f"✅ File uploaded: {uploaded_file.name}")
        with col2:
            st.info(f"📏 Size: {uploaded_file.size / 1024:.1f} KB")
        with col3:
            mode_label = {
                'digital_pdf': '⚡ Fast',
                'scanned_pdf': '🔍 OCR',
                'image': '🖼️ OCR'
            }
            st.info(mode_label.get(st.session_state.upload_mode, 'Processing'))
        
        # Add analyze button
        if st.button("🔬 Analyze Report", type="primary", use_container_width=True):
            with st.spinner("🔄 Processing your blood report..."):
                try:
                    # Save uploaded file temporarily
                    temp_path = f"temp_{uploaded_file.name}"
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Extract data
                    extractor = BloodReportExtractor()
                    
                    if st.session_state.upload_mode == 'image':
                        with st.status("Extracting text from image using OCR...", expanded=True) as status:
                            st.write("📸 Reading image...")
                            extracted_data = extractor.extract_from_image(temp_path)
                            status.update(label="✅ Text extraction complete!", state="complete")
                    else:
                        if use_ocr:
                            with st.status("Extracting text from scanned PDF using OCR...", expanded=True) as status:
                                st.write("📄 Converting PDF to images...")
                                st.write("🔍 Running OCR...")
                                extracted_data = extractor.extract_from_pdf(temp_path, use_ocr=True)
                                status.update(label="✅ Text extraction complete!", state="complete")
                        else:
                            extracted_data = extractor.extract_from_pdf(temp_path, use_ocr=False)
                    
                    # Clean up temp file
                    os.remove(temp_path)
                    
                    if not extracted_data:
                        st.error("❌ No blood parameters found in the file.")
                        if not use_ocr and st.session_state.upload_mode == 'digital_pdf':
                            st.warning("💡 **Tip**: This might be a scanned PDF. Try using 'Upload Scanned PDF (OCR)' instead.")
                        return
                    
                    st.success(f"✅ Successfully extracted {len(extracted_data)} parameters!")
                    
                    # Show extracted parameters
                    with st.expander("📋 View Extracted Parameters", expanded=True):
                        param_cols = st.columns(3)
                        for idx, (param, data) in enumerate(extracted_data.items()):
                            with param_cols[idx % 3]:
                                st.metric(
                                    param.replace('_', ' ').title(),
                                    f"{data['value']} {data.get('unit', '')}"
                                )
                    
                    # Parse and analyze
                    with st.spinner("🧮 Analyzing results..."):
                        parser = ReportParser()
                        parsed_results = parser.parse_report(extracted_data, gender)
                        
                        analyzer = HealthAnalyzer()
                        analysis = analyzer.analyze(parsed_results)
                    
                    # Generate AI summary
                    with st.spinner("🤖 Generating AI summary..."):
                        summary_gen = SummaryGenerator()
                        ai_summary = summary_gen.generate_summary(analysis)
                    
                    # Store in session state
                    st.session_state.analysis = analysis
                    st.session_state.ai_summary = ai_summary
                    st.session_state.analysis_complete = True
                    
                    # Initialize chatbot
                    if not st.session_state.chatbot:
                        st.session_state.chatbot = HealthChatbot()
                        st.session_state.chatbot.set_report_context(ai_summary)
                    
                    st.success("✅ Analysis complete!")
                    
                    # Display results
                    display_results(analysis, ai_summary)
                    
                except Exception as e:
                    st.error(f"❌ Error processing report: {str(e)}")
                    if "tesseract" in str(e).lower():
                        st.error("🔍 **Tesseract OCR not found!**")
                        st.info("Please install Tesseract OCR. See OCR_SETUP.md for instructions.")
                        st.code("pip install pytesseract\npip install pdf2image\npip install opencv-python")
                    st.exception(e)
    
    elif st.session_state.analysis_complete:
        st.divider()
        st.info("📊 Showing previous analysis results. Upload a new file to analyze again.")
        display_results(st.session_state.analysis, st.session_state.ai_summary)

def display_results(analysis, ai_summary):
    st.divider()
    
    # Risk Score Card with enhanced design
    st.markdown('<h2 class="sub-header">📊 Health Risk Assessment</h2>', unsafe_allow_html=True)
    
    risk_data = analysis['risk_assessment']
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Overall Risk Score",
            f"{risk_data['overall_risk_score']}/100",
            delta=f"{risk_data['risk_level']} Risk"
        )
    
    with col2:
        risk_level = risk_data['risk_level']
        color_map = {
            'Minimal': '🟢',
            'Low': '🟡',
            'Moderate': '🟠',
            'High': '🔴',
            'Critical': '🔴'
        }
        st.metric("Risk Level", f"{color_map.get(risk_level, '⚪')} {risk_level}")
    
    with col3:
        critical_count = len(analysis.get('critical_findings', []))
        st.metric("Critical Findings", critical_count, delta="Needs attention" if critical_count > 0 else "All good")
    
    # Visualizations
    charts = DashboardCharts()
    
    col1, col2 = st.columns(2)
    
    with col1:
        risk_gauge = charts.create_risk_gauge(risk_data['overall_risk_score'], risk_data['risk_level'])
        st.plotly_chart(risk_gauge, use_container_width=True)
    
    with col2:
        risk_breakdown = charts.create_risk_breakdown(risk_data['risks'])
        if risk_breakdown:
            st.plotly_chart(risk_breakdown, use_container_width=True)
    
    st.divider()
    
    # AI Summary with better styling
    st.markdown('<h2 class="sub-header">🤖 AI-Generated Health Summary</h2>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    st.markdown(ai_summary)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()
    
    # Results Table
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
    
    st.dataframe(results_df, use_container_width=True, hide_index=True)
    
    # More charts
    col1, col2 = st.columns(2)
    
    with col1:
        param_chart = charts.create_parameter_comparison(analysis['results'])
        if param_chart:
            st.plotly_chart(param_chart, use_container_width=True)
    
    with col2:
        severity_pie = charts.create_severity_pie(analysis['results'])
        st.plotly_chart(severity_pie, use_container_width=True)
    
    # Critical Findings
    if analysis.get('critical_findings'):
        st.markdown('<h2 class="sub-header">⚠️ Critical Findings</h2>', unsafe_allow_html=True)
        st.markdown('<div class="critical-box">', unsafe_allow_html=True)
        for finding in analysis['critical_findings']:
            st.warning(f"**{finding['parameter'].replace('_', ' ').title()}**: {finding['value']} {finding.get('unit', '')} - {finding.get('severity', 'Critical')}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Download Report
    st.divider()
    col1, col2 = st.columns([3, 1])
    with col2:
        report_json = json.dumps({'analysis': analysis, 'ai_summary': ai_summary}, indent=2)
        st.download_button(
            label="📥 Download Report",
            data=report_json,
            file_name="health_report.json",
            mime="application/json",
            use_container_width=True
        )

def ai_assistant_page():
    st.markdown('<h2 class="sub-header">💬 AI Health Assistant</h2>', unsafe_allow_html=True)
    
    if not st.session_state.analysis_complete:
        st.info("👆 Please upload and analyze a blood report first!")
        st.markdown("Go to **Upload & Analyze** to get started.")
        return
    
    if not st.session_state.chatbot:
        st.session_state.chatbot = HealthChatbot()
        st.session_state.chatbot.set_report_context(st.session_state.ai_summary)
    
    # Example questions
    st.markdown("""
    <div class="info-box">
    <h4 style="color: white; margin-top: 0;">💡 Example Questions</h4>
    <ul style="color: white;">
        <li>What does my LDL level mean?</li>
        <li>Is my HbA1c dangerous?</li>
        <li>What foods can improve my hemoglobin?</li>
        <li>Should I see a doctor immediately?</li>
        <li>How can I lower my cholesterol naturally?</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Display chat history
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
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
    
    # Clear chat button
    if st.session_state.chat_messages:
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.chat_messages = []
            st.session_state.chatbot.clear_history()
            st.rerun()

def about_page():
    st.markdown('<h2 class="sub-header">ℹ️ About This Application</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    ### 🏥 AI Health Diagnostics Assistant
    
    An advanced AI-powered blood report analysis system with OCR support.
    
    #### ✨ Key Features:
    - **🔍 OCR Support**: Upload scanned PDFs or images
    - **📤 PDF Upload**: Upload digital blood test reports
    - **🩺 18+ Parameters**: Comprehensive blood parameter analysis
    - **⚡ Instant Analysis**: Risk assessment and severity classification
    - **🤖 AI Summaries**: Patient-friendly explanations
    - **💬 Smart Chatbot**: RAG-powered medical Q&A
    - **📊 Visual Dashboards**: Interactive charts and graphs
    
    #### 🛠️ Technology Stack:
    - **Frontend**: Streamlit
    - **AI Model**: Groq (Llama 3.3 70B)
    - **OCR**: Tesseract + OpenCV
    - **Vector DB**: FAISS
    - **Embeddings**: Sentence Transformers
    
    #### ⚠️ Important Disclaimer:
    This tool is for informational purposes only and should not replace professional medical advice.
    
    #### 🔒 Privacy:
    - Local processing
    - No permanent storage
    - No third-party data sharing
    
    ---
    **Version**: 2.0.0 (OCR Enhanced)  
    **Powered by**: Groq AI  
    """)

if __name__ == "__main__":
    main()
