"""Transkripte gore pro kart ONERI plani uretir (otomatik uygulamaz).
Kullanim: python scripts/plan_cards.py 1008  ->  videos/1008/CARD_PLAN.json + ekrana ozet.
Mantik: sayi/yuzde/seviye iceren cumleler bulunur; kart tipi ve zamani cumleye gore secilir;
normal kartlar, sahneler ve birbirleriyle (>=1.5 sn bosluk) cakismaz. Etiket/metinleri paketleme
sirasinda cumleden elle/Claude ile netlestir (copy alanlari taslaktir)."""
from __future__ import annotations
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NUM = re.compile(r"\d[\d.,]*")
PCT = re.compile(r"%\s*\d|\d\s*%|yüzde", re.I)
PAIR = re.compile(r"beklen|açıkla|önceki|şimdi|dan\s+\d|\bgeriledi|\byükseldi|arttı|düştü", re.I)
LEVEL = re.compile(r"seviye|destek|direnç|bölge", re.I)


def load_words(vid):
    d = json.loads((ROOT / "videos" / vid / "transcripts" / "input-video.json").read_text(encoding="utf-8"))
    return [w for w in d.get("words", []) if w.get("type", "word") == "word"]


def sentences(words):
    out, cur = [], []
    for w in words:
        cur.append(w)
        t = w["text"]
        if t.endswith((".", "?", "!")) or (len(cur) >= 18):
            out.append(cur); cur = []
    if cur:
        out.append(cur)
    return out


def busy_windows(vid, tl):
    wins = []
    cp = ROOT / "videos" / vid / "cards.html"
    if cp.exists():
        for m in re.finditer(r'class="card-host[^"]*"[^>]*data-start="([\d.]+)"[^>]*data-duration="([\d.]+)"', cp.read_text(encoding="utf-8")):
            wins.append((float(m.group(1)), float(m.group(1)) + min(float(m.group(2)), 4.5)))
    for p in tl.get("proCards") or []:
        wins.append((float(p.get("start", 0)), float(p.get("start", 0)) + float(p.get("dur", 7))))
    for b in tl.get("broll") or []:
        wins.append((float(b["start"]), float(b["start"]) + float(b.get("dur", 8))))
    return wins


def free(s, e, wins, gap=1.5):
    return all(e + gap <= a or s >= b + gap for a, b in wins)


def main(vid):
    tpath = ROOT / "videos" / vid / "timeline.json"
    tl = json.loads(tpath.read_text(encoding="utf-8")) if tpath.exists() else {}
    words = load_words(vid)
    total = words[-1]["end"] if words else 0
    wins = busy_windows(vid, tl)
    rot = json.loads((ROOT / "shared" / "pro_rotation.json").read_text(encoding="utf-8"))["presets"]
    try:
        n = int(re.search(r"(\d+)\s*$", vid).group(1))
    except Exception:
        n = 0
    r = rot[n % len(rot)]
    plan = []
    # 1) acilis kancasi
    first = " ".join(w["text"] for w in sentences(words)[0]) if words else ""
    plan.append({"id": "hook", "block": "mk-hook", "start": 0.1, "dur": 3.0,
                 "copy": {"accent": r["accent"], "kicker": "KONU", "title": first.upper()[:46], "sub": ""}, "why": "açılış"})
    wins.append((0.0, 3.2))
    used = 0
    for s in sentences(words):
        txt = " ".join(w["text"] for w in s)
        nums = NUM.findall(txt)
        if not nums or used >= 5:
            continue
        t0 = max(0.5, s[0]["start"] - 0.2)
        if t0 + 5.5 > total - 1:
            continue
        if len(nums) >= 3 and LEVEL.search(txt):
            blk, cp = "mk-flap-board", {"label": "SEVİYELER", "rows": [{"label": f"Seviye {i+1}", "value": re.sub(r"\D", "", x)} for i, x in enumerate(nums[:3])], "unit": "TL"}
        elif len(nums) == 2 and PAIR.search(txt):
            blk, cp = "mk-compare", {"title": "KARŞILAŞTIRMA", "leftLabel": "Önce", "leftValue": nums[0], "rightLabel": "Şimdi", "rightValue": nums[1], "delta": "", "posY": 330}
        elif PCT.search(txt):
            v = int(re.sub(r"\D", "", nums[0]) or 0)
            blk, cp = "mk-ring-stat", {"label": "ORAN", "value": min(v, 100), "suffix": "%", "caption": txt[:48]}
        elif LEVEL.search(txt):
            blk, cp = "mk-strip", {"tag": "SEVİYE", "entries": [{"label": "Seviye", "value": x} for x in nums[:2]]}
        else:
            continue
        if not free(t0, t0 + 5.5, wins):
            continue
        cp["accent"] = r["accent"]
        plan.append({"id": f"{blk[3:]}-{int(t0)}", "block": blk, "start": round(t0, 1), "dur": 5.5, "copy": cp, "why": txt[:90]})
        wins.append((t0, t0 + 5.5)); used += 1
    out = ROOT / "videos" / vid / "CARD_PLAN.json"
    out.write_text(json.dumps({"video": vid, "oneriler": plan}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(plan)} kart önerisi -> {out}")
    for p in plan:
        print(f"  {p['start']:6.1f}s  {p['block']:<15} {p['why']}")


if __name__ == "__main__":
    main(sys.argv[1])
