@echo off
echo ============================================
echo AI Health Diagnostics Assistant - Startup
echo ============================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo Please run install.bat first
    pause
    exit /b 1
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

REM Check Python version
echo [INFO] Checking Python version...
python --version

REM Check if required packages are installed
echo [INFO] Checking dependencies...
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo [ERROR] Streamlit not installed!
    echo Please run: pip install -r requirements.txt
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo [WARNING] .env file not found!
    echo Creating .env file...
    echo GROQ_API_KEY=your_groq_api_key_here > .env
    echo [INFO] Please edit .env file and add your Groq API key
    echo Get your key from: https://console.groq.com/keys
    pause
)

REM Create necessary directories
if not exist "logs" mkdir logs
if not exist "data\knowledge_base" mkdir data\knowledge_base
if not exist "faiss_index" mkdir faiss_index

REM Clean up temp files
echo [INFO] Cleaning up temporary files...
del /q temp_* 2>nul

REM Run system tests
echo.
echo [INFO] Running system tests...
python test_system.py
if errorlevel 1 (
    echo.
    echo [ERROR] System tests failed!
    echo Please fix the errors above before continuing.
    pause
    exit /b 1
)

REM Start the application
echo.
echo ============================================
echo Starting AI Health Diagnostics Assistant...
echo ============================================
echo.
echo The application will open in your browser at:
echo http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo.

streamlit run app.py

pause
