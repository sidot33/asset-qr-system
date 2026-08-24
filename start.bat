@echo off
chcp 65001 >nul
cd /d "%~dp0"

set PYTHONHOME=
set PYTHONPATH=

if not exist "venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found.
    echo Please run setup.bat first to initialize the environment.
    pause
    exit /b 1
)

echo ==========================================
echo    Fixed Asset QR System - Starting
echo ==========================================
echo.

venv\Scripts\python.exe launch.py
pause
