@echo off
cd /d "%~dp0"
echo ===============================================================
echo  CATISMA COZULUYOR - bundan sonra videolar GitHub'a gitmeyecek
echo ===============================================================
echo.
echo Bu islem videolarinizi bilgisayarinizdan SILMEZ. Sadece GitHub'a
echo (paylasilan projeye) artik gonderilmeyecekler - orada sadece
echo ortak altyapi (motor/sablon) kalacak.
echo.

echo [1/5] .gitignore guncelleniyor...
git add .gitignore

echo.
echo [2/5] shared/SHOW_STANDARD.md catismasi cozuluyor...
git add shared/SHOW_STANDARD.md

echo.
echo [3/5] videolar git takibinden cikariliyor (dosyalar bilgisayarda kalir)...
git rm -r --cached -f videos/ >nul 2>&1

echo.
echo [4/5] kalan catisma var mi kontrol ediliyor...
git diff --name-only --diff-filter=U > "%TEMP%\_kalan_catisma.txt"
for %%A in ("%TEMP%\_kalan_catisma.txt") do set BOYUT=%%~zA
if not "%BOYUT%"=="0" (
  echo.
  echo *** HALA COZULMEMIS CATISMA VAR - asagidaki listeyi ekran goruntusu alip gonder ***
  type "%TEMP%\_kalan_catisma.txt"
  pause
  exit /b 1
)

echo.
echo [5/5] birlestirme tamamlaniyor ve GitHub'a gonderiliyor...
git commit -m "Merge: videolar artik GitHub'a gonderilmiyor, sadece ortak pipeline"
if errorlevel 1 (
  echo.
  echo *** COMMIT BASARISIZ OLDU - ekran goruntusunu alip gonder ***
  pause
  exit /b 1
)

git push

echo.
echo ===============================================================
echo Bitti. Yukarida kirmizi "error" yazisi yoksa basariyla gitti.
echo Videolariniz bilgisayarinizda oldugu gibi duruyor, sadece
echo bundan sonra GitHub'a gonderilmeyecekler.
echo ===============================================================
pause
