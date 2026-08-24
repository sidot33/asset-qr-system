#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fixed Asset QR System Launcher
"""

import subprocess
import sys
import os
import time
import webbrowser
import threading

# Config
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(PROJECT_DIR, "backend")
REQUIREMENTS = os.path.join(BACKEND_DIR, "requirements.txt")
URL = "http://localhost:8000"

VENV_DIR = os.path.join(PROJECT_DIR, "venv")
if os.name == 'nt':
    VENV_PYTHON = os.path.join(VENV_DIR, "Scripts", "python.exe")
else:
    VENV_PYTHON = os.path.join(VENV_DIR, "bin", "python")

PYTHON = VENV_PYTHON if os.path.exists(VENV_PYTHON) else sys.executable

PIPI_MIRROR = "https://pypi.tuna.tsinghua.edu.cn/simple"
SKIP_DEPS = os.environ.get("SKIP_DEPS", "0") == "1"

CORE_PACKAGES = [
    "fastapi", "uvicorn", "sqlalchemy", "pydantic",
    "openpyxl", "cryptography"
]


def print_step(step):
    print(f"\n{'='*50}")
    print(f"  {step}")
    print(f"{'='*50}")


def check_python():
    print_step("Check Python Environment")
    if os.path.exists(VENV_PYTHON):
        print(f"Using venv Python: {VENV_PYTHON}")
    else:
        print(f"Using system Python: {sys.executable}")
        print("\nTip: Run setup.bat first to create a virtual environment.")
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("ERROR: Python 3.9+ required")
        sys.exit(1)
    print("Python OK")


def check_package_installed(pkg_name):
    try:
        result = subprocess.run(
            [PYTHON, "-c", f"import {pkg_name}"],
            capture_output=True, timeout=5
        )
        return result.returncode == 0
    except Exception:
        return False


def install_dependencies():
    print_step("Check Dependencies")
    if not os.path.exists(REQUIREMENTS):
        print(f"ERROR: {REQUIREMENTS} not found")
        sys.exit(1)

    if SKIP_DEPS:
        print("SKIP_DEPS=1, skipping dependency check")
        return

    missing = [p for p in CORE_PACKAGES if not check_package_installed(p)]
    if not missing:
        print("All dependencies are installed.")
        return

    print(f"Missing: {', '.join(missing)}")
    print(f"Mirror: {PIPI_MIRROR}")
    print("Installing, please wait...")

    result = subprocess.run(
        [PYTHON, "-m", "pip", "install", "-r", REQUIREMENTS,
         "-i", PIPI_MIRROR, "--timeout", "60", "--retries", "3"],
        cwd=BACKEND_DIR,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, encoding="utf-8", errors="ignore"
    )
    for line in result.stdout.splitlines():
        line = line.strip()
        if "Successfully" in line or "satisfied" in line or "error" in line.lower():
            print("  " + line)

    if result.returncode != 0:
        print("WARNING: Dependency installation may have failed.")
    else:
        print("Dependencies installed.")


def open_browser_delayed():
    time.sleep(4)
    print(f"\nOpening browser: {URL}")
    webbrowser.open(URL)


def main():
    print("""
    ==========================================
         Fixed Asset QR System Launcher
    ==========================================
    """)

    check_python()
    install_dependencies()

    print_step("Start Server")
    print(f"Working directory: {BACKEND_DIR}")
    print(f"URL: {URL}")
    print("\nStarting uvicorn...\n")

    # Open browser in background thread
    threading.Thread(target=open_browser_delayed, daemon=True).start()

    print("Server is running. Press Ctrl+C to stop.\n")

    # Run uvicorn directly in this process so errors are visible
    try:
        import uvicorn
        uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
    except ImportError as e:
        print(f"\nERROR: Failed to import uvicorn - {e}")
        print("Please run setup.bat to install dependencies.")
        input("\nPress Enter to exit...")
    except Exception as e:
        print(f"\nERROR: {e}")
        input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
