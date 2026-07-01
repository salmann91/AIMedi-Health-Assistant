@echo off
echo ============================================================
echo AI Health Diagnostics Assistant
echo ============================================================
echo.

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Starting Streamlit application...
echo.
echo Application will open in your browser at http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo.

streamlit run app.py

pause
