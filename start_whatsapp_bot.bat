@echo off
title Shubdeep Labs - WhatsApp AI Bot
cd /d "%~dp0Whatsapp Chatbot\Whatsapp Chatbot"
:loop
echo ===================================================
echo [SYSTEM]: Starting Shubdeep Labs WhatsApp Bot Engine...
echo ===================================================
node index.js
echo.
echo [WARNING]: WhatsApp Bot stopped. Restarting in 3 seconds... (Press Ctrl+C to stop)
timeout /t 3 /nobreak >nul
goto loop
