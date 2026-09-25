"""Transcript JSON -> project.json captions."""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tr_text import caption_display

SERT_KW = ["düştü", "düşüş", "kayıp", "risk", "kriz", "çöktü", "azal", "zarar", "kaybet", "ters", "tehlike", "ucuz", "gerile"]
YUKSELIS_KW = ["yükseldi", "arttı", "artış", "kazanç", "kâr", "fırsat", "rüzgâr", "rüzgar", "çıktı", "güçlü", "avantaj", "lehine", "yüksel"]


def classify_tone(text):
    low = text.lower()
    if any(k in low for k in SERT_KW):
        return "sert"
    if any(k in low for k in YUKSELIS_KW):
        return "yukselis"
    return "yumusak"


def chunk_words(words, min_chars=10, max_words=5):
    """KİLİT (2026-09, '10 harf' kuralı): blok KELİME sayısına göre değil KARAKTER
    sayısına göre kapanır — en az MIN_CHARS harf birikince (cümle sonu beklemeden)
    blok kapanır, MAX_WORDS'e ulaşınca da (harf yetmese bile) kapanır. Önceki
    'min_words=10,max_words=16' sürümü cümle tamamlanana kadar bekliyordu — bu da
    16 kelimeye varan dev altyazı blokları üretip caption kutusuna sığdırmak için
    otomatik küçültmeyi (cap_line_scale + fitCapCutBlock) tetikliyor, altyazı
    minicik/sıkışık görünüyordu (0923'te gözlemlendi). Bu sürüm 0922'nin doğru
    davranışını (ort. ~2 kelime/blok, max 5) yeniden üretir — kısa, büyük, okunaklı
    altyazı patlamaları."""
    chunks, cur, cur_chars = [], [], 0
    for w in words:
        cur.append(w)
        cur_chars += len(w["text"]) + 1
        if len(cur) >= max_words:
            chunks.append(cur)
            cur, cur_chars = [], 0
        elif cur_chars >= min_chars:
            chunks.append(cur)
            cur, cur_chars = [], 0
    if cur:
        # Kalan kuyruk tek kelimelik gibi çok kısaysa bir önceki gruba ekle
        if chunks and len(cur) < 2:
            chunks[-1].extend(cur)
        else:
            chunks.append(cur)
    return chunks


def split_top_bottom(ch):
    """Kelimeleri iki satıra dengeli böl (üst + alt). build_engine.py zaten
    balance_caption_lines() ile en iyi bölme noktasını yeniden hesaplıyor —
    burada sadece makul bir başlangıç noktası veriyoruz."""
    n = len(ch)
    if n == 1:
        return "", caption_display(ch[0]["text"])
    if n == 2:
        return (
            caption_display(ch[0]["text"]),
            caption_display(ch[1]["text"]),
        )
    mid = max(1, n // 2)
    top = caption_display(" ".join(w["text"] for w in ch[:mid]))
    bottom = caption_display(" ".join(w["text"] for w in ch[mid:]))
    return top, bottom


def main():
    p = argparse.ArgumentParser()
    p.add_argument("transcript")
    p.add_argument("--out", required=True)
    p.add_argument("--source", default="")
    p.add_argument("--account", default="nihat", choices=["nihat", "mehmet"])
    args = p.parse_args()

    data = json.loads(Path(args.transcript).read_text(encoding="utf-8"))
    words = [w for w in data["words"] if w.get("type") != "spacing" and str(w.get("text", "")).strip()]
    for i, w in enumerate(words):
        w["idx"] = i
    chunks = chunk_words(words)
    captions = []
    for ch in chunks:
        text = " ".join(w["text"] for w in ch)
        n = len(ch)
        top, bottom = split_top_bottom(ch)
        captions.append({
            "start": round(float(ch[0]["start"]), 3),
            "end": round(float(ch[-1]["end"]), 3),
            "text": text,
            "top": top,
            "bottom": bottom,
            "tone": "fixed" if args.account == "mehmet" else classify_tone(text),
            "format": "A" if top else "B",
            "account": args.account,
            "wordStart": ch[0]["idx"],
            "wordEnd": ch[-1]["idx"],
        })
    # Kısa kuyruk kartı için minimum tutuş; konuşma süresine bağlı kal
    MIN_HOLD, GAP = 0.85, 0.03
    for i, c in enumerate(captions):
        target = c["start"] + MIN_HOLD
        limit = (captions[i + 1]["start"] - GAP) if i + 1 < len(captions) else (float(words[-1]["end"]) + 0.35)
        c["end"] = round(min(max(c["end"], target), max(c["start"] + 0.45, limit)), 3)
    duration = round(float(words[-1]["end"]) + 0.4, 3) if words else 0
    # Punto büyütüldü (75 -> 90); uzun satırlar Studio'daki oto-sığdırma ile taşmadan küçülür
    project = {
        "version": 1,
        "account": args.account,
        "source": args.source,
        "duration": duration,
        "cuts": [],
        "splits": [],
        "words": [{"start": w["start"], "end": w["end"], "text": w["text"]} for w in words],
        "layout": {
            "banner": {"x": 76, "y": 220, "w": 928, "h": 120},
            "caption": {"x": 40, "y": 1180, "w": 1000, "h": 380, "fontSize": 105},
        },
        "captions": captions,
        "events": [],
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(project, ensure_ascii=False, indent=2), encoding="utf-8")
    print("yazildi", out, "kelime", len(words), "altyazi", len(captions), "sure", duration)


if __name__ == "__main__":
    main()
