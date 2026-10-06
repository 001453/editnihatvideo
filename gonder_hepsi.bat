@echo off
cd /d "%~dp0"
echo [1/3] Dosyalar ekleniyor...
git add -A scripts shared gonder_hepsi.bat git_birlestir_gonder.bat
git commit -m "Pro kartlar: yeni bloklar, hook, planlayici, OpenAI duzeltmesi"
echo [2/3] Birlestiriliyor...
git fetch origin
git merge -X ours origin/main -m "birlestir"
echo [3/3] GitHub a gonderiliyor...
git push origin main
git status -sb
echo Bitti.
pause
