@echo off
cd /d "%~dp0"
echo Dashboard: http://127.0.0.1:8765/
echo Altyazi:   http://127.0.0.1:8765/captions?id=0909
echo.
py -3.12 scripts\dashboard_server.py
pause
