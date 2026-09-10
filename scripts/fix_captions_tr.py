# -*- coding: utf-8 -*-
"""Normalize existing project.json captions with Turkish display rules."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tr_text import caption_display

path = Path(sys.argv[1])
p = json.loads(path.read_text(encoding="utf-8"))
n = 0
for c in p.get("captions") or []:
    top = caption_display(c.get("top") or "")
    bot = caption_display(c.get("bottom") or c.get("text") or "")
    if top != (c.get("top") or "") or bot != (c.get("bottom") or ""):
        n += 1
    c["top"] = top
    c["bottom"] = bot
    c["text"] = f"{top} {bot}".strip()
path.write_text(json.dumps(p, ensure_ascii=False, indent=2), encoding="utf-8")
print("ok", path, "degisen", n, "toplam", len(p.get("captions") or []))
