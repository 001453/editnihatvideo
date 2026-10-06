@echo off
cd /d "%~dp0"
git rebase --abort 2>nul
echo [1/3] Birlestiriliyor (senin dosyalarin oncelikli)...
git fetch origin
git merge -X ours origin/main -m "Merge: son pro kart/sahne guncellemeleri"
if errorlevel 1 (
  echo.
  echo HATA. Ekran goruntusu al, bana gonder.
  git merge --abort
  pause
  exit /b 1
)
echo [2/3] GitHub a gonderiliyor...
git push origin main
echo [3/3] Son durum:
git status -sb
echo.
echo Bitti. Kirmizi error yoksa basarili.
pause
