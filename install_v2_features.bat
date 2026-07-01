@echo off
echo ============================================================
echo Installing V2.0 Features (Patient Info + Multi-format Downloads)
echo ============================================================
echo.

call venv\Scripts\activate.bat

echo Installing ReportLab for PDF generation...
pip install reportlab

echo.
echo ============================================================
echo Installation Complete!
echo ============================================================
echo.
echo NEW FEATURES AVAILABLE:
echo - Real-time patient information extraction
echo - PDF report downloads
echo - CSV spreadsheet exports
echo - JSON data exports
echo - Enhanced UI with download page
echo.
echo TO RUN:
echo   streamlit run app_final.py
echo.
echo SEE: NEW_FEATURES_V2.md for full documentation
echo ============================================================
pause
