@echo off
chcp 65001 >nul
echo ========================================
echo   TG ALARM - PM2 LOGS
echo ========================================
echo.
set /p vps_ip="Enter VPS IP: "
set /p vps_pass="Enter VPS SSH Password: "
echo.
python -c "import paramiko,sys; sys.stdout.reconfigure(encoding='utf-8'); ssh=paramiko.SSHClient(); ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()); ssh.connect('%vps_ip%',username='root',password='%vps_pass%'); i,o,e=ssh.exec_command('pm2 logs --nostream --lines 50'); print(o.read().decode('utf-8','ignore')); ssh.close()"
echo.
pause
