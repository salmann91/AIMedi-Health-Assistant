@echo off
echo ============================================================
echo AI Health Diagnostics Assistant - Installation Script
echo ============================================================
echo.

echo Step 1: Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment
    echo Please ensure Python 3.8+ is installed
    pause
    exit /b 1
)
echo Virtual environment created successfully!
echo.

echo Step 2: Activating virtual environment...
call venv\Scripts\activate.bat
echo.

echo Step 3: Upgrading pip...
python -m pip install --upgrade pip
echo.

echo Step 4: Installing dependencies...
pip install streamlit==1.31.0
pip install langchain==0.1.10
pip install langchain-groq==0.0.1
pip install python-dotenv==1.0.1
pip install pdfplumber==0.10.3
pip install faiss-cpu==1.7.4
pip install sentence-transformers==2.3.1
pip install plotly==5.18.0
pip install pandas==2.2.0
pip install numpy==1.26.3
pip install Pillow==10.2.0

if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo.

echo ============================================================
echo Installation Complete!
echo ============================================================
echo.
echo Next Steps:
echo 1. Edit .env file and add your Groq API key
echo 2. Get API key from: https://console.groq.com/keys
echo 3. Run: venv\Scripts\activate
echo 4. Run: streamlit run app.py
echo.
echo ============================================================
pause
