@echo off
chcp 65001 >nul
echo ========================================
echo   TG ALARM - DEPLOY TO VPS
echo ========================================
echo.
cd /d "%~dp0\.."
python deploy_remote.py
echo.
pause
