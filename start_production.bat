@echo off
echo ========================================
echo   Stock Analyzer - Production Mode
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Check if required files exist
if not exist "app.py" (
    echo ERROR: app.py not found
    echo Please run this script from the project directory
    pause
    exit /b 1
)

if not exist "config.py" (
    echo ERROR: config.py not found
    echo Please run this script from the project directory
    pause
    exit /b 1
)

echo Starting Stock Analyzer in PRODUCTION mode...
echo.
echo Server will be available at: http://localhost:8501
echo Press Ctrl+C to stop the application
echo.

REM Start the production app
python start_production.py

pause
