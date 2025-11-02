#!/bin/bash
# Cross-platform Python dev script
# Uses venv Python if available, otherwise falls back to python3/python

# Try to find Python in common locations
if [ -f "./venv/bin/python" ]; then
    # macOS/Linux venv
    PYTHON="./venv/bin/python"
elif [ -f "./venv/Scripts/python.exe" ]; then
    # Windows venv
    PYTHON="./venv/Scripts/python.exe"
elif command -v python3 &> /dev/null; then
    # System python3 (macOS/Linux)
    PYTHON="python3"
elif command -v python &> /dev/null; then
    # System python (Windows or if python3 alias exists)
    PYTHON="python"
else
    echo "Error: Python not found. Please install Python 3.12+ or activate your virtual environment."
    exit 1
fi

# Run uvicorn with the found Python
PYTHONPATH=. $PYTHON -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000

