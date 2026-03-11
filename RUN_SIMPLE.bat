@echo off
chcp 65001 >nul
title Community Volunteer Management System

echo ========================================
echo Community Volunteer Management System
echo ========================================
echo.

REM Try to find Python 3.13 in common locations
set "PYTHON_EXE="

echo Searching for Python 3.13...
echo.

REM Check common Python 3.13 installation paths
if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" (
    set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
    echo ✓ Found Python at: %LOCALAPPDATA%\Programs\Python\Python313\
)

if "%PYTHON_EXE%"=="" if exist "C:\Program Files\Python313\python.exe" (
    set "PYTHON_EXE=C:\Program Files\Python313\python.exe"
    echo ✓ Found Python at: C:\Program Files\Python313\
)

if "%PYTHON_EXE%"=="" if exist "C:\Python313\python.exe" (
    set "PYTHON_EXE=C:\Python313\python.exe"
    echo ✓ Found Python at: C:\Python313\
)

if "%PYTHON_EXE%"=="" if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python313\python.exe" (
    set "PYTHON_EXE=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python313\python.exe"
    echo ✓ Found Python at: C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python313\
)

REM If still not found, try py launcher
if "%PYTHON_EXE%"=="" (
    py -3.13 --version >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✓ Found Python using py launcher
        set "USE_PY_LAUNCHER=1"
    )
)

REM If still not found, try python command (might work if PATH is set)
if "%PYTHON_EXE%"=="" if "%USE_PY_LAUNCHER%"=="" (
    python --version >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✓ Found Python in PATH
        set "USE_PYTHON_COMMAND=1"
    )
)

REM If no Python found at all
if "%PYTHON_EXE%"=="" if "%USE_PY_LAUNCHER%"=="" if "%USE_PYTHON_COMMAND%"=="" (
    echo ========================================
    echo ERROR: Cannot find Python 3.13
    echo ========================================
    echo.
    echo Please do one of the following:
    echo.
    echo Option 1: Find your Python installation
    echo   1. Press Windows key and search for "IDLE"
    echo   2. Right-click IDLE and select "Open file location"
    echo   3. Note the folder path
    echo   4. Edit this script and add the path at line 15
    echo.
    echo Option 2: Add Python to PATH
    echo   1. Search for "Environment Variables" in Windows
    echo   2. Click "Environment Variables"
    echo   3. Under "System variables", find "Path"
    echo   4. Add your Python installation folder
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Starting Installation
echo ========================================
echo.

REM Create virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    if defined USE_PY_LAUNCHER (
        py -3.13 -m venv venv
    ) else if defined USE_PYTHON_COMMAND (
        python -m venv venv
    ) else (
        "%PYTHON_EXE%" -m venv venv
    )

    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo ✓ Virtual environment created
) else (
    echo ✓ Virtual environment already exists
)

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo Creating necessary directories...
if not exist "uploads" mkdir uploads
if not exist "instance" mkdir instance

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Access the system at: http://localhost:5002
echo.
echo Default admin account:
echo   Username: admin
echo   Password: admin123
echo.
echo Press any key to start the system...
pause >nul

echo.
echo Starting server...
python run.py

pause
