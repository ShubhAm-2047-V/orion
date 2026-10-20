@echo off
title Jarvis Assistant
echo ===================================================
echo             JARVIS AI SYSTEM INITIALIZATION
echo ===================================================
echo.

:: 1. Start Control Center Dashboard on port 8000
netstat -ano | findstr :8000 >nul
if %errorlevel% neq 0 (
    echo [SYSTEM]: Starting JARVIS Control Center Dashboard on port 8000...
    start /b python "%~dp0dashboard_server.py"
) else (
    echo [SYSTEM]: Control Center Dashboard is already running on port 8000.
)

:: 2. Start Orion OS WhatsApp Bot & Remote Executive Engine
netstat -ano | findstr :3030 >nul
if %errorlevel% neq 0 (
    echo [SYSTEM]: Starting Orion OS WhatsApp Bot Engine...
    start "Shubdeep Labs - WhatsApp AI Bot" "%~dp0start_whatsapp_bot.bat"
) else (
    echo [SYSTEM]: WhatsApp Bot Engine is already running on port 3030.
)

:: 3. Start Jarvis AI OS interface
echo [SYSTEM]: Initializing Jarvis AI OS interface...
python "%~dp0main.py"
if %errorlevel% neq 0 (
    echo.
    echo [ERROR]: Failed to start Jarvis. Please ensure Python is installed and configured in PATH.
    pause
)

