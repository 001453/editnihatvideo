@echo off
cd /d "%~dp0"
echo ===============================================================
echo  README.md GitHub'a gonderiliyor
echo ===============================================================
echo.

git add README.md
git commit -m "README: A'dan Z'ye video yapim adimlari guncellendi"
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
echo ===============================================================
pause
