@echo off
REM Windows batch script for Python dev server
REM Uses venv Python if available, otherwise falls back to python

if exist "venv\Scripts\python.exe" (
    set PYTHON=venv\Scripts\python.exe
) else if exist "venv\bin\python" (
    set PYTHON=venv\bin\python
) else (
    where python >nul 2>&1
    if %errorlevel% == 0 (
        set PYTHON=python
    ) else (
        echo Error: Python not found. Please install Python 3.12+ or activate your virtual environment.
        exit /b 1
    )
)

set PYTHONPATH=.
%PYTHON% -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000

