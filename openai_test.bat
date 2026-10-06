@echo off
cd /d "%~dp0"
py -3.12 scripts\openai_transcribe.py videos\1006\public\input-video.mp4 _test_openai.json > _openai_test.txt 2>&1
type _openai_test.txt
echo.
echo Bitti. Bana "tamam" yaz.
pause
