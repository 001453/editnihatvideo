@echo off
cd /d "%~dp0"
echo ===============================================================
echo  Son guncellemeleri GitHub'a gonder
echo ===============================================================
git add -A
git commit -m "Pipeline guncellemesi: OpenAI transkript, rank-board, scene kart havuzu, 1004/1005"
git pull origin main --no-rebase --no-edit
if errorlevel 1 (
  echo *** PULL BASARISIZ - ekran goruntusu alip gonder ***
  pause
  exit /b 1
)
git push
echo.
echo Bitti. Kirmizi "error" veya "CONFLICT" yoksa basariyla gitti.
pause
