@echo off
title Bangkok Mobility & Transit Interactive Dashboard (Production)
echo ================================================================
echo    Bangkok Smart Mobility & Transit Analytics Dashboard
echo ================================================================
echo.
echo Launching Production Web Application...
echo Local Server URL: http://localhost:5555/
echo.
start "" "http://localhost:5555/"
timeout /t 3 >nul
exit
