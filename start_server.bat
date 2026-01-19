@echo off
echo Starting Financial Analyst Agent API Server...
echo.
echo Configuration:
echo - Gemini API Key: Configured
echo - Model: gemini-2.5-flash
echo - Qdrant: Connected to Cloud
echo.
call backend\venv\Scripts\activate.bat
python -m backend.app.main
pause
