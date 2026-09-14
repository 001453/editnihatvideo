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


def chunk_words(words, max_words=6, min_words=3):
    """Bigger chunks → longer on-screen holds (speech-synced, not flashy)."""
    chunks, cur = [], []
    for w in words:
        cur.append(w)
        ends = bool(re.search(r"[.!?]$", w["text"]))
        dur = float(cur[-1]["end"]) - float(cur[0]["start"])
        if ends and len(cur) >= min_words:
            chunks.append(cur)
            cur = []
        elif len(cur) >= max_words:
            chunks.append(cur)
            cur = []
        elif ends and len(cur) < min_words:
            continue
        elif dur >= 2.4 and len(cur) >= min_words:
            chunks.append(cur)
            cur = []
    if cur:
        if chunks and len(cur) < min_words:
            chunks[-1].extend(cur)
        else:
            chunks.append(cur)
    return chunks


def split_top_bottom(ch):
    """Always 2 lines — minimize longest line so punto stays near standard."""
    n = len(ch)
    if n == 1:
        return "", caption_display(ch[0]["text"])
    if n == 2:
        return (
            caption_display(ch[0]["text"]),
            caption_display(ch[1]["text"]),
        )
    best_i, best_score = 1, None
    for i in range(1, n):
        a = " ".join(w["text"] for w in ch[:i])
        b = " ".join(w["text"] for w in ch[i:])
        score = max(len(a), len(b)) * 10 + abs(len(a) - len(b))
        if best_score is None or score < best_score:
            best_score, best_i = score, i
    top = caption_display(" ".join(w["text"] for w in ch[:best_i]))
    bottom = caption_display(" ".join(w["text"] for w in ch[best_i:]))
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
    # Min hold ~2s so captions don't flash; stay speech-synced without overlap
    MIN_HOLD, GAP = 2.05, 0.04
    for i, c in enumerate(captions):
        target = c["start"] + MIN_HOLD
        limit = (captions[i + 1]["start"] - GAP) if i + 1 < len(captions) else (float(words[-1]["end"]) + 0.4)
        c["end"] = round(min(max(c["end"], target), max(c["start"] + 0.6, limit)), 3)
    duration = round(float(words[-1]["end"]) + 0.4, 3) if words else 0
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
            "caption": {"x": 40, "y": 1208, "w": 1000, "h": 340, "fontSize": 58},
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
