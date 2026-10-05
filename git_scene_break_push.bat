@echo off
cd /d "%~dp0"
echo ===============================================================
echo  mk-scene-break ozelligi GitHub'a gonderiliyor
echo ===============================================================
echo.

git add shared\build_engine.py shared\registry\compositions\mk-scene-break.html shared\registry\compositions\mk-app-mockup.html shared\PRO_CARDS.md shared\SHOW_STANDARD.md README.md
git commit -m "mk-scene-break: gorunurluk kilitlenme hatasi duzeltildi (ileri/geri scrub), standart 4 normal + 2 pro kart kurali, zaman cakismasi yasagi"
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
