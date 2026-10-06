"""OpenAI ile Turkce transkript (kelime zamanli). Anahtar: OPENAI_API_KEY ortam degiskeni
veya scripts/openai_key.txt dosyasi. Cikti: {"words":[{type,text,start,end,speaker_id}]}"""
from __future__ import annotations
import json, os, subprocess, sys, uuid, urllib.request, urllib.error, tempfile
from pathlib import Path

PROMPT = ("Türkçe finans videosu. Terimler: altın, gram altın, ons, Fed, faiz, enflasyon, "
          "Borsa İstanbul, BIST, temettü, hisse, TOASO, ISMEN, ENJSA, AYGAZ, CLEBI, FROTO, "
          "ANSGR, ENKAI, DOAS, PAGYO, dolar, euro, tahvil, petrol, destek, direnç. "
          "Sayılar: 6.500 TL, %5,34, 29.000. Yatırım tavsiyesi değildir.")

def key() -> str:
    k = os.environ.get("OPENAI_API_KEY", "").strip()
    if not k:
        f = Path(__file__).with_name("openai_key.txt")
        if f.exists():
            k = f.read_text(encoding="utf-8").strip()
    return k

def transcribe(video: Path, out: Path) -> bool:
    k = key()
    kf = Path(__file__).with_name("openai_key.txt")
    if not k:
        print(f"OpenAI: anahtar YOK (aranan dosya: {kf}) -> atlandi", flush=True)
        return False
    print(f"OpenAI: anahtar bulundu ({len(k)} karakter) -> transkript basliyor", flush=True)
    tmp = Path(tempfile.gettempdir()) / f"oa_{uuid.uuid4().hex}.mp3"
    try:
        subprocess.run(["ffmpeg", "-y", "-i", str(video), "-vn", "-ac", "1", "-ar", "16000",
                        "-b:a", "48k", str(tmp)], check=True, capture_output=True)
    except Exception as e:
        print(f"OpenAI: ses cikarilamadi (ffmpeg): {e}", flush=True)
        return False
    data = tmp.read_bytes()
    b = uuid.uuid4().hex
    parts = []
    def f(n, v): parts.append(f'--{b}\r\nContent-Disposition: form-data; name="{n}"\r\n\r\n{v}\r\n'.encode())
    f("model", "whisper-1"); f("language", "tr"); f("response_format", "verbose_json")
    f("timestamp_granularities[]", "word"); f("temperature", "0"); f("prompt", PROMPT)
    parts.append((f'--{b}\r\nContent-Disposition: form-data; name="file"; filename="a.mp3"\r\n'
                  'Content-Type: audio/mpeg\r\n\r\n').encode() + data + b"\r\n")
    parts.append(f"--{b}--\r\n".encode())
    req = urllib.request.Request("https://api.openai.com/v1/audio/transcriptions",
        data=b"".join(parts), headers={"Authorization": f"Bearer {k}",
        "Content-Type": f"multipart/form-data; boundary={b}"})
    try:
        res = json.load(urllib.request.urlopen(req, timeout=600))
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode("utf-8", "ignore")[:400]
        except Exception:
            body = ""
        print(f"OpenAI hata {e.code}: {body}", flush=True); return False
    except Exception as e:
        print(f"OpenAI hata: {e}", flush=True); return False
    finally:
        tmp.unlink(missing_ok=True)
    words = [{"type": "word", "text": w["word"].strip(), "start": round(w["start"], 2),
              "end": round(w["end"], 2), "speaker_id": "speaker_0"} for w in res.get("words", [])]
    if not words:
        return False
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"words": words}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"OpenAI transkript: {len(words)} kelime", flush=True)
    return True

if __name__ == "__main__":
    sys.exit(0 if transcribe(Path(sys.argv[1]), Path(sys.argv[2])) else 1)
