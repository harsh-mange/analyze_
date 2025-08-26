@echo off
echo 📈 Stock Analyzer & Predictor - Demo Mode
echo ================================================
echo.
echo 🚀 Starting demo application...
echo 📊 This will open a web browser with the demo
echo ⏳ Please wait...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Check if requirements are installed
echo 🔍 Checking dependencies...
python -c "import streamlit, pandas, plotly, numpy" >nul 2>&1
if errorlevel 1 (
    echo ❌ Missing dependencies
    echo Installing requirements...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Failed to install requirements
        pause
        exit /b 1
    )
)

echo ✅ Dependencies check passed
echo.
echo 🎯 Starting demo application...
echo 💡 The application will open in your default web browser
echo 🔄 To stop the demo, close this window or press Ctrl+C
echo ------------------------------------------------

REM Start the demo
python start_demo.py

echo.
echo Demo stopped.
pause 