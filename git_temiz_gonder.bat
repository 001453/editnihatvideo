@echo off
cd /d "%~dp0"
echo ===============================================================
echo  Gizli anahtar sorununu temizle ve gonder
echo ===============================================================
git fetch origin
echo [1/4] Gonderilemeyen tum commitler tek paket yapiliyor (dosyalar korunuyor)...
git reset --soft origin/main
echo [2/4] Gizli dosyalar takip disi birakiliyor...
git rm -r --cached --ignore-unmatch ".cursor/mcp.json" "scripts/openai_key.txt" ".env" "_ref_gold_tip" "Claude outputs" "_dash.err" "_dash.log" "videos/*/public"
git add -A
echo [3/4] Temiz commit...
git commit -m "Pipeline guncellemesi: OpenAI transkript, rank-board, scene kart havuzu, 1004/1005"
echo [4/4] Gonderiliyor...
git push
echo.
echo Bitti. Hata varsa ekran goruntusunun EN USTUNDEKI "secret"/dosya adi satirlarini da gonder.
pause
