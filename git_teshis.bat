@echo off
cd /d "%~dp0"
git push > _git_log.txt 2>&1
git ls-files | findstr /i "mcp.json key .env" >> _git_log.txt 2>&1
echo Bitti. Bu pencereyi kapat, bana "tamam" yaz.
pause
