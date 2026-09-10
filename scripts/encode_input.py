# -*- coding: utf-8 -*-
"""Seek-friendly H.264 encode. Talking-head: same resolution, fast draft.
B-roll: muted 9:16 crop. Final export quality stays HyperFrames render (not here).
"""
import argparse
import subprocess
from pathlib import Path


def encode(src: Path, dst: Path, broll: bool = False, quality: str = "draft") -> None:
    src = Path(src)
    dst = Path(dst)
    if not src.is_file():
        raise FileNotFoundError(f"video dosyasi degil (klasor olamaz): {src}")
    dst.parent.mkdir(parents=True, exist_ok=True)

    # draft = hizli, ayni cozunurluk. final = daha yavas/daha iyi (son render oncesi)
    if quality == "final":
        preset, crf = "slow", "18"
    else:
        preset, crf = "veryfast", "20"

    same = src.resolve() == dst.resolve()
    out = dst.with_suffix(dst.suffix + ".tmp.mp4") if same else dst

    cmd = ["ffmpeg", "-y", "-i", str(src)]
    if broll:
        # Always 8s · muted 9:16 crop (show lock — user prepares from start sentence)
        cmd += [
            "-t", "8",
            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
            "-an",
        ]
    else:
        # NO scale — cozunurlugu bozma; sadece seek-friendly re-encode
        cmd += ["-c:a", "aac", "-ar", "48000", "-ac", "2"]
    cmd += [
        "-c:v", "libx264", "-preset", preset, "-crf", crf,
        "-g", "15", "-bf", "0", "-tune", "fastdecode", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(out),
    ]
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True)
    if same:
        out.replace(dst)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("src")
    p.add_argument("dst")
    p.add_argument("--broll", action="store_true", help="muted 9:16 crop / 8s, no audio")
    p.add_argument("--quality", choices=["draft", "final"], default="draft")
    args = p.parse_args()
    encode(Path(args.src), Path(args.dst), broll=args.broll, quality=args.quality)


if __name__ == "__main__":
    main()
