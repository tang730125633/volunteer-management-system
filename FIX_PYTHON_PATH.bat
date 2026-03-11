@echo off
chcp 65001 >nul
title Python Path Diagnostic Tool

echo ========================================
echo Python Installation Diagnostic
echo ========================================
echo.

echo Checking common Python installation paths...
echo.

REM Check if Python is in PATH
echo [Test 1] Checking if Python is in PATH...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ SUCCESS: Python found in PATH
    python --version
    echo.
    echo Python location:
    where python
    echo.
    goto :found
)

echo ✗ Python NOT found in PATH
echo.

REM Try common installation locations for Python 3.13
echo [Test 2] Searching common installation locations...
echo.

set "PYTHON_FOUND="

REM Check AppData Local
if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" (
    set "PYTHON_PATH=%LOCALAPPDATA%\Programs\Python\Python313"
    set "PYTHON_FOUND=1"
    goto :fix_path
)

REM Check Program Files
if exist "C:\Program Files\Python313\python.exe" (
    set "PYTHON_PATH=C:\Program Files\Python313"
    set "PYTHON_FOUND=1"
    goto :fix_path
)

REM Check Program Files (x86)
if exist "C:\Program Files (x86)\Python313\python.exe" (
    set "PYTHON_PATH=C:\Program Files (x86)\Python313"
    set "PYTHON_FOUND=1"
    goto :fix_path
)

REM Check C:\Python313
if exist "C:\Python313\python.exe" (
    set "PYTHON_PATH=C:\Python313"
    set "PYTHON_FOUND=1"
    goto :fix_path
)

echo ✗ Python 3.13 not found in common locations
echo.
echo Please locate your Python installation manually:
echo 1. Open Start Menu
echo 2. Search for "IDLE"
echo 3. Right-click on IDLE → Open file location
echo 4. Note the folder path and run SETUP_WITH_PATH.bat
echo.
pause
exit /b 1

:fix_path
echo ✓ Found Python 3.13 at: %PYTHON_PATH%
echo.
echo Testing Python...
"%PYTHON_PATH%\python.exe" --version
echo.

echo ========================================
echo Solution: Use Python with full path
echo ========================================
echo.
echo I will create a new setup script that uses the full Python path.
echo This script will work without modifying your system PATH.
echo.
pause

REM Create a new setup script with full Python path
(
echo @echo off
echo chcp 65001 ^>nul
echo title Community Volunteer Management System - Setup
echo.
echo ========================================
echo Community Volunteer Management System
echo ========================================
echo.
echo Using Python from: %PYTHON_PATH%
echo.
echo.
echo [Step 1/5] Checking Python...
echo.
echo "%PYTHON_PATH%\python.exe" --version
echo.
echo.
echo [Step 2/5] Creating virtual environment...
if not exist "venv" ^(
echo     "%PYTHON_PATH%\python.exe" -m venv venv
echo     if %%errorlevel%% neq 0 ^(
echo         echo [ERROR] Failed to create virtual environment
echo         pause
echo         exit /b 1
echo     ^)
echo     echo ✓ Virtual environment created
echo ^) else ^(
echo     echo ✓ Virtual environment exists
echo ^)
echo.
echo.
echo [Step 3/5] Activating virtual environment...
echo call venv\Scripts\activate.bat
echo.
echo.
echo [Step 4/5] Installing dependencies...
echo pip install --upgrade pip
echo pip install -r requirements.txt
echo.
echo.
echo [Step 5/5] Creating directories...
echo if not exist "uploads" mkdir uploads
echo if not exist "instance" mkdir instance
echo.
echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Access URL: http://localhost:5002
echo Admin: admin / admin123
echo.
echo Press any key to start the system...
echo pause ^>nul
echo.
echo python run.py
echo.
echo pause
) > SETUP_WITH_PYTHON313.bat

echo.
echo ✓ Created new setup script: SETUP_WITH_PYTHON313.bat
echo.
echo ========================================
echo Next Step:
echo ========================================
echo.
echo Double-click on: SETUP_WITH_PYTHON313.bat
echo.
pause
exit /b 0

:found
echo ========================================
echo Python is properly configured!
echo ========================================
echo.
echo You can use the original SETUP_WINDOWS.bat script.
echo.
pause
