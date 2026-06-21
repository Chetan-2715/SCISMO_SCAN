@echo off
title SCISMO SCAN - Stopping Servers
color 0C
echo.
echo  Stopping all SCISMO SCAN servers...
echo.

:: Kill Python backend server
taskkill /FI "WINDOWTITLE eq SCISMO Backend*" /F >nul 2>&1
taskkill /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq *server*" /F >nul 2>&1

:: Kill Node frontend server  
taskkill /FI "WINDOWTITLE eq SCISMO Frontend*" /F >nul 2>&1

echo  All servers stopped.
echo.
pause
