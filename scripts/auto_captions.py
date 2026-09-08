"""Transcript JSON -> project.json captions."""
import argparse
import json
import re
from pathlib import Path

SERT_KW = ["düştü", "düşüş", "kayıp", "risk", "kriz", "çöktü", "azal", "zarar", "kaybet", "ters", "tehlike", "ucuz", "gerile"]
YUKSELIS_KW = ["yükseldi", "arttı", "artış", "kazanç", "kâr", "fırsat", "rüzgâr", "rüzgar", "çıktı", "güçlü", "avantaj", "lehine", "yüksel"]


def classify_tone(text):
    low = text.lower()
    if any(k in low for k in SERT_KW):
        return "sert"
    if any(k in low for k in YUKSELIS_KW):
        return "yukselis"
    return "yumusak"


def chunk_words(words, max_words=5, min_words=2):
    chunks, cur = [], []
    for w in words:
        cur.append(w)
        ends = bool(re.search(r"[.!?]$", w["text"]))
        if (ends and len(cur) >= min_words) or len(cur) >= max_words:
            chunks.append(cur)
            cur = []
        elif ends and len(cur) < min_words:
            continue
    if cur:
        chunks.append(cur)
    return chunks


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
        if n <= 3:
            top, bottom = "", " ".join(w["text"] for w in ch).upper()
        else:
            half = min(3, (n + 1) // 2)
            top = " ".join(w["text"] for w in ch[:half]).upper()
            bottom = " ".join(w["text"] for w in ch[half:]).upper()
        captions.append({
            "start": round(float(ch[0]["start"]), 3),
            "end": round(float(ch[-1]["end"]), 3),
            "text": text,
            "top": top,
            "bottom": bottom,
            "tone": "fixed" if args.account == "mehmet" else classify_tone(text),
            "format": "B" if n <= 2 else "A",
            "account": args.account,
            "wordStart": ch[0]["idx"],
            "wordEnd": ch[-1]["idx"],
        })
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
            "caption": {"x": 20, "y": 1208, "w": 1060, "h": 320, "fontSize": 62},
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
