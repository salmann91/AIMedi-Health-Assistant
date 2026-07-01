@echo off
echo ============================================================
echo OCR Features Installation
echo ============================================================
echo.

echo Installing OCR-related Python packages...
echo.

call venv\Scripts\activate.bat

pip install pytesseract
pip install pdf2image
pip install opencv-python

echo.
echo ============================================================
echo Python packages installed!
echo ============================================================
echo.

echo NEXT STEPS:
echo.
echo 1. Install Tesseract OCR:
echo    Download from: https://github.com/UB-Mannheim/tesseract/wiki
echo    Run the installer and add to PATH
echo.
echo 2. Install Poppler:
echo    Download from: https://github.com/oschwartz10612/poppler-windows/releases
echo    Extract and add bin folder to PATH
echo.
echo 3. See OCR_SETUP.md for detailed instructions
echo.
echo ============================================================
pause
