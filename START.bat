@echo off
title SCISMO SCAN - Running...
color 0B
echo.
echo  ============================================================
echo       SCISMO SCAN - Structural Crack Assessment System
echo  ============================================================
echo.

:: Check if setup was done
if not exist "venv\Scripts\python.exe" (
    color 0C
    echo  ERROR: Setup not completed! Please run SETUP.bat first.
    echo.
    pause
    exit /b 1
)

if not exist "frontend\node_modules" (
    color 0C
    echo  ERROR: Frontend not set up! Please run SETUP.bat first.
    echo.
    pause
    exit /b 1
)

:: ---------------------------------------------------------------
:: Start Backend Server
:: ---------------------------------------------------------------
echo  [1/2] Starting Backend Server (FastAPI on port 8000)...
start "SCISMO Backend" /min cmd /c "cd /d "%~dp0" && venv\Scripts\python.exe backend\server.py"
echo        Backend starting at: http://127.0.0.1:8000
echo.

:: Wait for backend to boot up
timeout /t 3 /nobreak >nul

:: ---------------------------------------------------------------
:: Start Frontend Dev Server
:: ---------------------------------------------------------------
echo  [2/2] Starting Frontend Server (Vite on port 5173)...
start "SCISMO Frontend" /min cmd /c "cd /d "%~dp0frontend" && npm run dev"
echo        Frontend starting at: http://localhost:5173
echo.

:: Wait for frontend to boot up
timeout /t 5 /nobreak >nul

:: ---------------------------------------------------------------
:: Open browser
:: ---------------------------------------------------------------
echo  Opening browser...
start http://localhost:5173
echo.
echo  ============================================================
echo       Application is running!
echo.
echo       Frontend : http://localhost:5173
echo       Backend  : http://127.0.0.1:8000
echo       API Docs : http://127.0.0.1:8000/docs
echo.
echo       To STOP the app, close this window and the two
echo       minimized command windows (Backend and Frontend).
echo  ============================================================
echo.
pause
