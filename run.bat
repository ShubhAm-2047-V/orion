@echo off
title Jarvis Assistant
echo [SYSTEM]: Initializing Jarvis interface...
python "%~dp0main.py"
if %errorlevel% neq 0 (
    echo.
    echo [ERROR]: Failed to start Jarvis. Please ensure Python is installed and configured in PATH.
    pause
)
