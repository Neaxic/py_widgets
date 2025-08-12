@echo off
REM Desktop Widget Startup Script
REM Double-click this file to start all your widgets

echo Starting Desktop Widgets...
cd /d "%~dp0"
python startup.py

REM Keep window open if there's an error
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo An error occurred. Press any key to exit...
    pause >nul
)
