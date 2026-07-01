# PowerShell Installation Script
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "AI Health Diagnostics Assistant - Installation" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Step 1: Upgrading pip..." -ForegroundColor Yellow
& "venv\Scripts\python.exe" -m pip install --upgrade pip

Write-Host ""
Write-Host "Step 2: Installing dependencies..." -ForegroundColor Yellow
& "venv\Scripts\pip.exe" install streamlit
& "venv\Scripts\pip.exe" install langchain
& "venv\Scripts\pip.exe" install langchain-groq
& "venv\Scripts\pip.exe" install python-dotenv
& "venv\Scripts\pip.exe" install pdfplumber
& "venv\Scripts\pip.exe" install faiss-cpu
& "venv\Scripts\pip.exe" install sentence-transformers
& "venv\Scripts\pip.exe" install plotly
& "venv\Scripts\pip.exe" install pandas
& "venv\Scripts\pip.exe" install numpy
& "venv\Scripts\pip.exe" install Pillow

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Edit .env file and add your Groq API key"
Write-Host "2. Get API key from: https://console.groq.com/keys"
Write-Host "3. Run: .\run.ps1"
Write-Host ""
