@echo off
chcp 65001 >nul
title Community Volunteer Management System - Fix & Run

echo =============================================================================
echo    Community Volunteer Management System
echo    Fix Virtual Environment and Run
echo =============================================================================
echo.

REM Step 1: Check Python
echo [Step 1/6] Checking Python installation...
echo.
python --version
if %errorlevel% neq 0 (
    echo [ERROR] Python not found in PATH
    pause
    exit /b 1
)
echo [SUCCESS] Python is ready!
echo.

REM Step 2: Remove corrupted virtual environment
echo [Step 2/6] Cleaning up old virtual environment...
echo.
if exist "venv" (
    echo Removing corrupted virtual environment...
    rmdir /s /q venv
    if exist "venv" (
        echo [WARNING] Could not remove venv folder completely
        echo Please manually delete the 'venv' folder and run this script again
        pause
        exit /b 1
    )
    echo [SUCCESS] Old virtual environment removed
) else (
    echo [INFO] No existing virtual environment found
)
echo.

REM Step 3: Create fresh virtual environment
echo [Step 3/6] Creating fresh virtual environment...
echo This may take 1-2 minutes...
echo.
python -m venv venv
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create virtual environment
    echo.
    echo Troubleshooting:
    echo 1. Make sure you have write permissions in this folder
    echo 2. Check if antivirus is blocking the operation
    echo 3. Try running this script as Administrator
    pause
    exit /b 1
)
echo [SUCCESS] Virtual environment created!
echo.

REM Step 4: Verify activation script exists
echo [Step 4/6] Verifying virtual environment...
echo.
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment is incomplete
    echo The activation script was not created properly
    pause
    exit /b 1
)
echo [SUCCESS] Virtual environment is complete!
echo.

REM Step 5: Activate virtual environment
echo [Step 5/6] Activating virtual environment...
echo.
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo [SUCCESS] Virtual environment activated!
echo.

REM Step 6: Install dependencies
echo [Step 6/6] Installing dependencies...
echo This may take 5-10 minutes on first run...
echo.
python -m pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    echo Check your internet connection and try again
    pause
    exit /b 1
)
echo [SUCCESS] All dependencies installed!
echo.

REM Create necessary directories
echo Creating necessary directories...
if not exist "uploads" mkdir uploads
if not exist "instance" mkdir instance
echo.

REM Display success message
echo =============================================================================
echo    Setup Complete!
echo =============================================================================
echo.
echo The system is ready to start!
echo.
echo Access URL:  http://localhost:5002
echo.
echo Default Admin Account:
echo   Username: admin
echo   Password: admin123
echo.
echo Press any key to start the server...
echo (Press Ctrl+C to stop the server when running)
echo =============================================================================
pause >nul

REM Start the application
echo.
echo Starting Community Volunteer Management System...
echo.
python run.py

REM If server stops
echo.
echo Server stopped.
pause
