@echo off
cd /d "%~dp0"
echo ===============================================================
echo  GitHub'a GUVENLI gonderim
echo  - Gizli anahtar (.cursor/mcp.json) commit'ten cikariliyor
echo  - Video ciktilari (videos/*/public) artik gonderilmeyecek
echo  - Sadece proje/kod/kart kaynaklari gidecek
echo ===============================================================
echo.

echo [1/5] Son (gonderilemeyen) commit geri aliniyor, dosyalar korunuyor...
git reset --soft HEAD~1

echo.
echo [2/5] Gizli anahtar ve video ciktilari takip disi birakiliyor...
git rm -r --cached --ignore-unmatch ".cursor/mcp.json" "_ref_gold_tip" "Claude outputs" "_dash.err" "_dash.log" "videos/*/public"

echo.
echo [3/5] Degisiklikler yeniden hazirlaniyor...
git add -A

echo.
echo [4/5] Yeni, temiz commit olusturuluyor...
git commit -m "Pipeline guncellemesi (yakin/punch konumu, kart rozeti/gecis ornegi) - video ciktilari ve gizli anahtar haric"

echo.
echo [5/5] GitHub'a gonderiliyor...
git push

echo.
echo ===============================================================
echo Bitti. Yukarida kirmizi "error" yazisi yoksa basariyla gitti demektir.
echo Bir hata gorursen ekran goruntusu al, bana gonder.
echo ===============================================================
pause
