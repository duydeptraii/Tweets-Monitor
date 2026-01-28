@echo off
title X Tweet Monitor
echo Starting X Tweet Monitor...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

REM Check if dependencies are installed
python -c "import rich" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    echo.
)

REM Run the monitor
python tweet_monitor.py %*

pause
