@echo off
chcp 65001 >nul
cd /d "%~dp0"

set PYTHONHOME=
set PYTHONPATH=

echo ==========================================
echo    Fixed Asset QR System - Setup
echo ==========================================
echo.

set PY_CMD=py -3
%PY_CMD% --version >nul 2>&1
if %errorlevel% neq 0 (
    set PY_CMD=python
    %PY_CMD% --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo ERROR: Python not found.
        echo Please install Python 3.11 or 3.12 (64-bit) from:
        echo   https://www.python.org/downloads/
        echo Make sure to check "Add Python to PATH" during install.
        pause
        exit /b 1
    )
)

echo Python detected:
%PY_CMD% --version
echo.

echo [1/3] Creating virtual environment...
%PY_CMD% -m venv venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create venv.
    pause
    exit /b 1
)

echo [2/3] Upgrading pip...
venv\Scripts\python.exe -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple

echo [3/3] Installing dependencies (binary only)...
echo.

REM Install packages from requirements.txt (all have pre-built wheels)
venv\Scripts\python.exe -m pip install -r backend\requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --only-binary :all: --timeout 60
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to install base packages.
    echo Please install Python 3.11 or 3.12 (64-bit).
    pause
    exit /b 1
)

REM Install SQLAlchemy without greenlet dependency (greenlet has no wheel for Python 3.14)
echo.
echo Installing SQLAlchemy (without greenlet dependency)...
venv\Scripts\python.exe -m pip install sqlalchemy==1.4.51 --no-deps -i https://pypi.tuna.tsinghua.edu.cn/simple --only-binary :all: --timeout 60
if %errorlevel% neq 0 (
    echo WARNING: SQLAlchemy installation failed. Trying alternative...
    venv\Scripts\python.exe -m pip install sqlalchemy==1.4.51 --no-deps -i https://pypi.tuna.tsinghua.edu.cn/simple --timeout 60
)

echo.
echo Setup complete! You can now run start.bat
echo.
pause
