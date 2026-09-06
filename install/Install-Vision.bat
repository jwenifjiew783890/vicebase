@echo off
REM Double-click entry point. Runs the PowerShell installer without
REM requiring the user to change their execution policy permanently.
echo Starting the Vision installer...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0Install-Vision.ps1" %*
if errorlevel 1 pause
