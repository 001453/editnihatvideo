# -*- coding: utf-8 -*-
"""Yeni video klasoru: shared asset + sablon + istege bagli encode."""
import argparse
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHARED = ROOT / "shared"
TEMPLATE = ROOT / "template"
VIDEOS = ROOT / "videos"
sys.path.insert(0, str(Path(__file__).resolve().parent))


def sanitize_id(raw: str) -> str:
    s = (raw or "").strip()
    s = re.sub(r"\.mp4$", "", s, flags=re.I)
    s = re.sub(r"[^\w\-]+", "", s, flags=re.U)
    if not s:
        raise SystemExit("gecersiz video id")
    return s


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("id", help="ornek: 0910")
    p.add_argument("--source", help="ham talking-head mp4 (dosya, klasor degil)")
    p.add_argument("--account", default="nihat", choices=["nihat", "mehmet"])
    p.add_argument("--force", action="store_true", help="eksik/yarim klasoru silip yeniden olustur")
    p.add_argument("--quality", choices=["draft", "final"], default="draft")
    args = p.parse_args()

    vid = sanitize_id(args.id)
    dest = VIDEOS / vid

    if args.source:
        src = Path(args.source)
        if not src.is_file():
            sys.exit(f"kaynak bir video DOSYASI olmali (klasor degil): {src}")

    if dest.exists():
        if args.force:
            shutil.rmtree(dest)
        else:
            sys.exit(f"zaten var: {dest}  (--force ile yeniden)")

    public = dest / "public"
    public.mkdir(parents=True)
    (public / "broll").mkdir()
    for name in ("fonts", "sfx", "vendor"):
        shutil.copytree(SHARED / name, public / name)
    shutil.copy2(SHARED / "follow_banner.png", public / "follow_banner.png")
    shutil.copy2(TEMPLATE / "hyperframes.json", dest / "hyperframes.json")
    shutil.copy2(TEMPLATE / "timeline.json", dest / "timeline.json")
    shutil.copy2(TEMPLATE / "cards.html", dest / "cards.html")
    shutil.copy2(TEMPLATE / "build_composition.py", dest / "build_composition.py")
    pkg = json.loads((TEMPLATE / "package.json").read_text(encoding="utf-8"))
    pkg["name"] = vid
    (dest / "package.json").write_text(json.dumps(pkg, indent=2) + "\n", encoding="utf-8")

    project = {
        "version": 1,
        "account": args.account,
        "source": args.source or "",
        "duration": 0,
        "cuts": [],
        "splits": [],
        "words": [],
        "layout": {
            "banner": {"x": 76, "y": 220, "w": 928, "h": 120},
            "caption": {"x": 20, "y": 1208, "w": 1060, "h": 320, "fontSize": 62},
        },
        "captions": [],
        "events": [],
    }
    (dest / "project.json").write_text(
        json.dumps(project, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    if args.source:
        from encode_input import encode
        encode(Path(args.source), public / "input-video.mp4", quality=args.quality)

    print(f"hazir {dest}")
    print("1. editor.html ile kes / altyazi / kaydet -> project.json")
    print("2. Agent transkripti 0907 akisi gibi paketler (kart + b-roll + punch)")
    print(f"3. python videos\\{vid}\\build_composition.py")
    print(f"4. Studio Ctrl+F5; cd videos\\{vid}; npx hyperframes@0.8.30 preview")


if __name__ == "__main__":
    main()
