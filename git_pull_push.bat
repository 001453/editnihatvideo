@echo off
cd /d "%~dp0"
echo ===============================================================
echo  GitHub'dan gelen degisiklikleri al, sonra tekrar gonder
echo ===============================================================
echo.

echo [1/2] GitHub'daki guncellemeler indiriliyor ve birlestiriliyor...
git pull origin main --no-rebase --no-edit
if errorlevel 1 (
  echo.
  echo *** PULL BASARISIZ OLDU - yukarida ne yazdigini ekran goruntusu alip gonder ***
  pause
  exit /b 1
)

echo.
echo [2/2] GitHub'a tekrar gonderiliyor...
git push

echo.
echo ===============================================================
echo Bitti. Yukarida kirmizi "error" veya "CONFLICT" yazisi yoksa
echo basariyla gitti demektir. "CONFLICT" gorursen ekran goruntusu
echo alip bana gonder, elle duzeltmemiz gerekecek.
echo ===============================================================
pause
