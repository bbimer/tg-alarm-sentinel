@echo off
chcp 65001 >nul
echo ========================================
echo   TG ALARM - SERVER STATUS
echo ========================================
echo.
set /p vps_ip="Enter VPS IP (or press Enter if saved in env): "
set /p vps_pass="Enter VPS SSH Password: "
echo.
python -c "import paramiko,sys; sys.stdout.reconfigure(encoding='utf-8'); ssh=paramiko.SSHClient(); ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()); ssh.connect('%vps_ip%',username='root',password='%vps_pass%'); cmds=['pm2 status','free -h','uptime']; [print(ssh.exec_command(c)[1].read().decode('utf-8','ignore')) for c in cmds]; ssh.close()"
echo.
pause
