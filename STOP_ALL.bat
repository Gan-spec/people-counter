@echo off
title People Counter - Shutdown
color 0C

echo ========================================
echo   PEOPLE COUNTER - STOPPING ALL
echo ========================================
echo.

echo Closing all services...
echo.

taskkill /FI "WindowTitle eq People Counter*" /F >nul 2>&1
taskkill /FI "WindowTitle eq Web Server*" /F >nul 2>&1
taskkill /FI "WindowTitle eq ngrok*" /F >nul 2>&1

echo.
echo ========================================
echo   ALL SERVICES STOPPED!
echo ========================================
echo.
echo Press any key to close...
pause >nul
