# -*- coding: utf-8 -*-
"""Yeni video: klasor + encode + whisper + altyazi. Dashboard / CLI."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent
VIDEOS = ROOT / "videos"
FREECUT_PY = Path(r"C:\Users\nihat\.claude\skills\freecut\.venv\Scripts\python.exe")
FREECUT_TX = Path(r"C:\Users\nihat\.claude\skills\freecut\helpers\transcribe.py")


def sanitize_id(raw: str) -> str:
    s = (raw or "").strip()
    s = re.sub(r"\.mp4$", "", s, flags=re.I)
    s = re.sub(r"[^\w\-]+", "", s, flags=re.U)
    if not s:
        raise SystemExit("gecersiz video id (orn: 0910)")
    return s


def run(cmd, cwd=None):
    print("+", " ".join(str(c) for c in cmd), flush=True)
    r = subprocess.run(cmd, cwd=cwd or ROOT)
    if r.returncode != 0:
        raise SystemExit(r.returncode)


def ensure_folder(vid: str, source: Path, account: str, force: bool, quality: str) -> Path:
    dest = VIDEOS / vid
    pub = dest / "public" / "input-video.mp4"
    incomplete = dest.exists() and not pub.exists()
    if not dest.exists() or force or incomplete:
        cmd = [
            sys.executable, str(SCRIPTS / "new_video.py"), vid,
            "--source", str(source),
            "--account", account,
            "--quality", quality,
        ]
        if dest.exists():
            cmd.append("--force")
        run(cmd)
    else:
        if source.exists() and source.stat().st_mtime > pub.stat().st_mtime:
            sys.path.insert(0, str(SCRIPTS))
            from encode_input import encode
            encode(source, pub, quality=quality)
        proj_path = dest / "project.json"
        proj = json.loads(proj_path.read_text(encoding="utf-8"))
        proj["account"] = account
        proj["source"] = str(source)
        proj_path.write_text(json.dumps(proj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return dest


def transcribe(dest: Path) -> Path:
    video = dest / "public" / "input-video.mp4"
    out = dest / "transcripts" / "input-video.json"
    out.parent.mkdir(exist_ok=True)
    if out.exists() and out.stat().st_size > 100:
        print(f"transcript var, atlanıyor: {out}", flush=True)
        return out
    if FREECUT_TX.exists() and FREECUT_PY.exists():
        run([
            str(FREECUT_PY),
            str(FREECUT_TX),
            str(video),
            "--edit-dir",
            str(dest),
            "--language",
            "tr",
        ])
    else:
        run(
            ["npx", "--yes", "hyperframes@0.8.30", "transcribe", str(video)],
            cwd=dest,
        )
    if not out.exists():
        alt = dest / "public" / "edit" / "transcripts" / "input-video.json"
        if alt.exists():
            out.parent.mkdir(exist_ok=True)
            shutil.copy2(alt, out)
    if not out.exists():
        raise SystemExit(f"transcript yok: {out}")
    return out


def captions(dest: Path, transcript: Path, account: str, source: str) -> None:
    run([
        sys.executable,
        str(SCRIPTS / "auto_captions.py"),
        str(transcript),
        "--out", str(dest / "project.json"),
        "--account", account,
        "--source", source,
    ])


def write_package_flag(dest: Path, account: str) -> None:
    flag = {
        "status": "ready_for_package",
        "id": dest.name,
        "account": account,
        "bible": "0907",
        "prompt": (
            f"videos/{dest.name} hazir. project.json + transcript var. "
            f"0907 akisiyla paketle: kartlar, b-roll, punch, IG, build. "
            f"Ctrl+F5 soyle. Kod bilmiyorum; soru sorma, dogrudan uygula."
        ),
    }
    (dest / "PACKAGE_ME.json").write_text(
        json.dumps(flag, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (dest / "PACKAGE_ME.txt").write_text(flag["prompt"] + "\n", encoding="utf-8")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("id")
    p.add_argument("--source", required=True)
    p.add_argument("--account", default="nihat", choices=["nihat", "mehmet"])
    p.add_argument("--skip-transcribe", action="store_true")
    p.add_argument("--force", action="store_true")
    p.add_argument("--quality", choices=["draft", "final"], default="draft")
    args = p.parse_args()
    vid = sanitize_id(args.id)
    source = Path(args.source)
    if not source.is_file():
        raise SystemExit(f"kaynak bir video DOSYASI olmali (klasor degil): {source}")

    dest = ensure_folder(vid, source, args.account, args.force, args.quality)
    if not args.skip_transcribe:
        tx = transcribe(dest)
        captions(dest, tx, args.account, str(source))
    write_package_flag(dest, args.account)
    print(f"OK {dest}")
    print(f"PROMPT: {(dest / 'PACKAGE_ME.txt').read_text(encoding='utf-8').strip()}")


if __name__ == "__main__":
    main()
