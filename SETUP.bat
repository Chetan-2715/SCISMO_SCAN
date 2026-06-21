@echo off
title SCISMO SCAN - First Time Setup
color 0A
echo.
echo  ============================================================
echo       SCISMO SCAN - Structural Crack Assessment System
echo              FIRST TIME SETUP (Run this ONCE)
echo  ============================================================
echo.

:: ---------------------------------------------------------------
:: Step 1: Check if Python is installed
:: ---------------------------------------------------------------
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo.
    echo  ERROR: Python is NOT installed on this system!
    echo.
    echo  Please install Python first:
    echo    1. Go to https://www.python.org/downloads/
    echo    2. Download Python 3.10 or later
    echo    3. IMPORTANT: Check "Add Python to PATH" during installation!
    echo    4. After installing, run this SETUP.bat again.
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do echo        Found: %%i
echo.

:: ---------------------------------------------------------------
:: Step 2: Check if Node.js is installed
:: ---------------------------------------------------------------
echo [2/5] Checking Node.js installation...
node --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo.
    echo  ERROR: Node.js is NOT installed on this system!
    echo.
    echo  Please install Node.js first:
    echo    1. Go to https://nodejs.org/
    echo    2. Download the LTS version
    echo    3. Install with default settings (Next, Next, Finish)
    echo    4. After installing, run this SETUP.bat again.
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('node --version') do echo        Found: Node.js %%i
echo.

:: ---------------------------------------------------------------
:: Step 3: Create Python Virtual Environment
:: ---------------------------------------------------------------
echo [3/5] Creating Python virtual environment...
if exist "venv" (
    echo        Virtual environment already exists. Skipping creation.
) else (
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        color 0C
        echo  ERROR: Failed to create virtual environment!
        pause
        exit /b 1
    )
    echo        Virtual environment created successfully.
)
echo.

:: ---------------------------------------------------------------
:: Step 4: Install Python dependencies
:: ---------------------------------------------------------------
echo [4/5] Installing Python dependencies (this may take 5-10 minutes)...
echo        Installing PyTorch (CPU version for compatibility)...
call venv\Scripts\pip.exe install torch torchvision --index-url https://download.pytorch.org/whl/cpu --quiet
echo        Installing remaining dependencies...
call venv\Scripts\pip.exe install -r requirements.txt --quiet
if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo  ERROR: Failed to install Python dependencies!
    pause
    exit /b 1
)
echo        All Python dependencies installed.
echo.

:: ---------------------------------------------------------------
:: Step 5: Install Frontend dependencies
:: ---------------------------------------------------------------
echo [5/5] Installing frontend dependencies...
cd frontend
call npm install --silent
if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo  ERROR: Failed to install frontend dependencies!
    cd ..
    pause
    exit /b 1
)
cd ..
echo        Frontend dependencies installed.
echo.

:: ---------------------------------------------------------------
:: Done!
:: ---------------------------------------------------------------
color 0A
echo.
echo  ============================================================
echo            SETUP COMPLETE! Everything is ready.
echo  ============================================================
echo.
echo  To run the application, double-click START.bat
echo.

:: Check if the YOLO model exists
if exist "backend\best_structural_model.pt" (
    echo  [OK] YOLO model found: backend\best_structural_model.pt
) else (
    color 0E
    echo  [WARNING] YOLO model NOT found at backend\best_structural_model.pt
    echo            The app will work but with reduced accuracy.
    echo            To train your own model, run:
    echo              venv\Scripts\python.exe backend\train_yolo.py
)
echo.
pause
