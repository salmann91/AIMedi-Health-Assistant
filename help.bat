@echo off
cls
echo ================================================================
echo    AI Health Diagnostics Assistant v2.0
echo ================================================================
echo.
echo QUICK START:
echo   1. Run: start.bat
echo   2. Login: admin / admin123
echo   3. Upload blood report (PDF or image)
echo   4. View analysis and chat with AI
echo.
echo ================================================================
echo AVAILABLE COMMANDS:
echo ================================================================
echo.
echo   start.bat          - Start the application
echo   python test_system.py - Run system tests
echo   help.bat           - Show this help
echo.
echo ================================================================
echo FILE STRUCTURE:
echo ================================================================
echo.
echo   app.py             - Main application
echo   auth.py            - Login system
echo   config.py          - Configuration
echo   utils.py           - Utility functions
echo   test_system.py     - System tests
echo   .env               - API key (configure this!)
echo.
echo   data/              - Medical knowledge base
echo   logs/              - Application logs
echo   faiss_index/       - Vector database
echo.
echo ================================================================
echo DOCUMENTATION:
echo ================================================================
echo.
echo   README.md          - Full documentation
echo   INSTALLATION.md    - Setup guide
echo   FIXES.md           - Changelog and improvements
echo.
echo ================================================================
echo TROUBLESHOOTING:
echo ================================================================
echo.
echo Problem: "GROQ_API_KEY not found"
echo Solution: Edit .env file and add your API key
echo          Get key from: https://console.groq.com/keys
echo.
echo Problem: "Module not found"
echo Solution: pip install -r requirements.txt
echo.
echo Problem: "Login fails"
echo Solution: Use admin/admin123 or delete users.json
echo.
echo Problem: OCR not working
echo Solution: Install Tesseract OCR
echo          https://github.com/UB-Mannheim/tesseract/wiki
echo.
echo ================================================================
echo FEATURES:
echo ================================================================
echo.
echo   [x] Secure login system
echo   [x] PDF and image upload
echo   [x] OCR for scanned documents
echo   [x] Blood parameter extraction
echo   [x] AI-powered risk assessment
echo   [x] Health recommendations
echo   [x] Interactive chat assistant
echo   [x] Visual dashboards
echo   [x] Download reports
echo   [x] Error logging
echo.
echo ================================================================
echo SUPPORT:
echo ================================================================
echo.
echo   Check logs:     type logs\app_*.log
echo   Run tests:      python test_system.py
echo   Read docs:      type README.md
echo   View changes:   type FIXES.md
echo.
echo ================================================================
echo SECURITY:
echo ================================================================
echo.
echo   - Change default admin password after first login
echo   - Keep .env file secret (contains API key)
echo   - Review logs regularly
echo   - Update dependencies monthly
echo.
echo ================================================================
echo.
echo Press any key to exit...
pause >nul
