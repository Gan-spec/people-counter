@echo off
title People Counter - Startup
color 0A

echo ========================================
echo   PEOPLE COUNTER - STARTING ALL
echo ========================================
echo.

echo [1/3] Starting people counter (AI detection)...
start "People Counter" cmd /k "cd laptop_server && python people_counter.py"
timeout /t 5 /nobreak >nul

echo [2/3] Starting web server...
start "Web Server" cmd /k "cd laptop_server && python app.py"
timeout /t 5 /nobreak >nul

echo [3/3] Starting ngrok (public URL)...
start "ngrok" cmd /k "cd ngrok-v3-stable-windows-amd64 && ngrok http 5000"

echo.
echo ========================================
echo   ALL SERVICES STARTED!
echo ========================================
echo.
echo Check the "ngrok" window for your public URL
echo It will look like: https://abc123.ngrok.io
echo.
echo Share that URL with anyone to access your app!
echo.
echo Press any key to close this window...
pause >nul
