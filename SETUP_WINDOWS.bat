@echo off
REM =============================================================================
REM Community Volunteer Management System - Windows Setup Script
REM =============================================================================
REM This script will automatically set up and run the system on Windows
REM No prior experience required!
REM =============================================================================

chcp 65001 >nul
title Community Volunteer Management System - Setup

echo.
echo =============================================================================
echo    Community Volunteer Management System
echo    Windows Installation and Setup Script
echo =============================================================================
echo.

REM Step 1: Check Python Installation
echo [Step 1/5] Checking Python installation...
echo.
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed on your system!
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo IMPORTANT: During installation, make sure to check the box that says:
    echo "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

echo [SUCCESS] Python is installed!
python --version
echo.

REM Step 2: Check if virtual environment exists
echo [Step 2/5] Setting up virtual environment...
echo.

if not exist "venv" (
    echo Creating virtual environment... This may take a minute.
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [SUCCESS] Virtual environment created!
) else (
    echo [INFO] Virtual environment already exists
)
echo.

REM Step 3: Activate virtual environment
echo [Step 3/5] Activating virtual environment...
echo.
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo [SUCCESS] Virtual environment activated!
echo.

REM Step 4: Install dependencies
echo [Step 4/5] Installing required packages...
echo This may take several minutes depending on your internet connection.
echo.
pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    echo Please check your internet connection and try again
    pause
    exit /b 1
)
echo.
echo [SUCCESS] All packages installed successfully!
echo.

REM Step 5: Create necessary directories
echo [Step 5/5] Creating system directories...
echo.
if not exist "uploads" (
    mkdir uploads
    echo [SUCCESS] Created 'uploads' directory
)
if not exist "instance" (
    mkdir instance
    echo [SUCCESS] Created 'instance' directory
)
echo.

REM Display system information
echo =============================================================================
echo    Setup completed successfully!
echo =============================================================================
echo.
echo System is ready to start!
echo.
echo Access URL: http://localhost:5002
echo Default admin account:
echo   - Username: admin
echo   - Password: admin123
echo.
echo The system will now start. Press Ctrl+C to stop the server.
echo.
echo =============================================================================
echo.
pause

REM Start the system
echo Starting the Community Volunteer Management System...
echo.
python run.py

REM If system stops
echo.
echo =============================================================================
echo System stopped.
echo =============================================================================
pause
