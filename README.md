# AI Health Diagnostics Assistant 🏥

An advanced AI-powered blood report analysis system using Groq AI, LangChain, RAG, and Streamlit.

## 🚀 Features

- **Secure Login System** - User authentication with password hashing and session management
- **PDF & Image Blood Report Upload** - Upload blood test reports in PDF or image format (PNG, JPG, JPEG)
- **OCR Support** - Process scanned documents with advanced OCR technology (Tesseract)
- **Smart Parameter Extraction** - Automatically extracts key blood parameters
- **Risk Assessment** - Identifies potential health risks (anemia, diabetes, cholesterol, kidney, liver, thyroid)
- **Severity Classification** - Classifies abnormalities from Normal to Critical
- **AI-Powered Summaries** - Generates patient-friendly health summaries using Groq's Llama 3.3
- **Personalized Recommendations** - Provides actionable health advice
- **Integrated AI Assistant** - Chat about your test results directly below recommendations
- **RAG Knowledge Base** - Question answering grounded in medical knowledge
- **Interactive Dashboards** - Visual health data representation
- **Error Logging** - Comprehensive logging for debugging and monitoring
- **Rate Limiting** - API rate limiting to prevent abuse

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **AI/LLM**: Groq API (Llama 3.3 70B Versatile)
- **Framework**: LangChain
- **OCR Engine**: Tesseract OCR with OpenCV preprocessing
- **Vector Database**: FAISS
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **PDF Processing**: PDFPlumber, pdf2image
- **Image Processing**: OpenCV, Pillow
- **Visualization**: Plotly
- **Language**: Python 3.8+

## 📋 Prerequisites

- Python 3.8 or higher
- Groq API Key (Get from https://console.groq.com/keys)
- pip package manager

## 🔧 Installation

### Step 1: Clone the Repository
```bash
cd c:\Users\MD SALMAN\OneDrive\Desktop\AIMedi_RepoScan
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure API Key
Edit the `.env` file and add your Groq API key:
```
GROQ_API_KEY=your_actual_groq_api_key_here
```

## 🚀 Running the Application

### Start the Streamlit App
streamlit run app.py

The application will open in your browser at `http://localhost:8501`

## 📖 Usage Guide

### 1. Upload Blood Report
- Click on "Upload & Analyze" in the sidebar
- Upload your PDF blood report or image (PNG, JPG)
- **Enable OCR**: Check the "Use OCR" checkbox for scanned documents or images
- Select your gender for accurate reference ranges
- Wait for automatic extraction and analysis

### 2. View Analysis
- **Risk Score**: Overall health risk assessment (0-100)
- **Risk Level**: Minimal, Low, Moderate, High, or Critical
- **AI Summary**: Comprehensive health summary with findings and recommendations
- **Detailed Results**: Table with all parameters, values, and status
- **Visualizations**: Charts showing abnormal parameters and severity distribution

### 3. Chat with AI Assistant (Below Results)
- Scroll down to the "AI Health Assistant" section
- Ask questions about your results directly on the same page
- Get explanations, dietary advice, and when to see a doctor
- No need to navigate to a separate page!

### Example Questions:
- "What does my LDL level mean?"
- "How can I improve my hemoglobin?"
- "Is my HbA1c dangerous?"
- "What foods should I avoid?"
- "Should I see a doctor immediately?"

## 📁 Project Structure

```
health-ai-assistant/
├── app.py                          # Main Streamlit application
├── .env                            # API keys configuration
├── requirements.txt                # Python dependencies
├── data/
│   ├── sample_reports/            # Sample blood reports
│   └── knowledge_base/            # Medical knowledge texts
│       ├── hemoglobin.txt
│       ├── hba1c.txt
│       ├── cholesterol.txt
│       ├── kidney.txt
│       ├── liver.txt
│       └── thyroid.txt
├── report_processing/
│   ├── extractor.py               # PDF extraction
│   ├── parser.py                  # Parameter parsing
│   └── normalizer.py              # Data normalization
├── analytics/
│   ├── severity.py                # Severity classification
│   ├── risk_engine.py             # Risk assessment
│   └── analyzer.py                # Main analyzer
├── rag/
│   ├── embeddings.py              # Embedding generation
│   ├── vector_store.py            # FAISS vector store
│   └── retriever.py               # Document retrieval
├── ai/
│   ├── prompts.py                 # LLM prompts
│   ├── summary_generator.py      # AI summary generation
│   └── chatbot.py                 # Conversational AI
└── dashboard/
    └── charts.py                  # Plotly visualizations
```

## 🔍 Supported Blood Parameters

- Hemoglobin (Hb)
- HbA1c (Glycated Hemoglobin)
- Glucose (Blood Sugar)
- Total Cholesterol
- LDL Cholesterol
- HDL Cholesterol
- Triglycerides
- RBC (Red Blood Cells)
- WBC (White Blood Cells)
- Platelets
- Creatinine
- BUN (Blood Urea Nitrogen)
- Vitamin D
- TSH (Thyroid Stimulating Hormone)
- T3, T4 (Thyroid Hormones)
- ALT, AST (Liver Enzymes)

## 📊 Risk Assessment Categories

### 1. Anemia Risk
- Detects low hemoglobin and RBC
- Severity levels based on hemoglobin values

### 2. Diabetes Risk
- HbA1c and glucose levels
- Prediabetes and diabetes detection

### 3. Cholesterol Risk
- LDL, HDL, and triglycerides
- Cardiovascular risk assessment

### 4. Kidney Function
- Creatinine and BUN levels
- CKD stage estimation

### 5. Liver Function
- ALT and AST enzyme levels
- Liver health assessment

### 6. Thyroid Function
- TSH, T3, T4 levels
- Hypo/hyperthyroidism detection

## 🔒 Privacy & Security

- All processing happens locally on your machine
- No data is sent to external servers except Groq API for AI generation
- Reports are not permanently stored
- You can clear all data anytime

## ⚠️ Disclaimer

**IMPORTANT**: This application is for educational and informational purposes only. It is NOT a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition.

## 🐛 Troubleshooting

### Issue: "No blood parameters found"
- **For PDFs**: Ensure PDF contains text (not scanned image) or enable "Use OCR"
- **For scanned PDFs**: Check the "Use OCR" checkbox
- **For images**: Ensure image is clear and text is readable
- Check if parameter names match expected formats

### Issue: OCR not working
- Install Tesseract OCR: Download from https://github.com/UB-Mannheim/tesseract/wiki
- Windows users: Install to `C:\Program Files\Tesseract-OCR\`
- Verify installation: Run `tesseract --version` in command prompt
- Restart the application after installation

### Issue: "GROQ_API_KEY not found" or "Invalid API key"
- Verify `.env` file exists in root directory
- Check API key is correctly set: `GROQ_API_KEY=gsk_your_key_here`
- API key should start with `gsk_`
- Do not use quotes around the key
- Restart the application after updating `.env`

### Issue: Module import errors
- Ensure virtual environment is activated: `venv\Scripts\activate`
- Reinstall dependencies: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.8+)

### Issue: Login not working
- Use default credentials: `admin` / `admin123`
- Check if `users.json` file exists
- Try deleting `users.json` and restart (will recreate default admin)

### Issue: Application crashes or errors
- Check `logs` folder for error details
- Ensure all directories exist: `data`, `faiss_index`, `logs`
- Try clearing session state with "Clear All Data" button
- Restart the application

### Issue: File upload fails
- Check file size (max 10MB)
- Ensure file format is supported (PDF, PNG, JPG, JPEG)
- Try a different file
- Check disk space

### Getting Help
- Check the logs in `logs/` directory
- Open an issue on GitHub with error details
- Include: OS, Python version, error message, and log file

## 📈 Future Enhancements

- [x] OCR support for scanned PDFs ✅
- [x] Image upload support ✅
- [x] Integrated AI Assistant on results page ✅
- [ ] Multi-language support
- [ ] Trend analysis (multiple reports over time)
- [ ] Doctor report generation
- [ ] Email notifications for critical findings
- [ ] Mobile app version

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## 📄 License

This project is licensed under the MIT License.

## 👥 Support

For questions or support, please open an issue on GitHub.

