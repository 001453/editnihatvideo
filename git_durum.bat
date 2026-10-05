@echo off
cd /d "%~dp0"
echo ===============================================================
echo  DURUM RAPORU
echo ===============================================================
echo.
echo --- git status ---
git status
echo.
echo --- catisan (conflict) dosyalar icindeki isaretler ---
git diff --name-only --diff-filter=U
echo.
echo ===============================================================
echo Bu ekrandaki HER SEYI kopyalayip bana gonder.
echo ===============================================================
pause
