# -*- coding: utf-8 -*-
"""ZSky b-roll prep: kisa (~5sn) ZSky uretimini show-locked 8sn 9:16 muted
b-roll'e cevirir.

ZSky ucretsiz video ciktisi ~5sn. Sabit 8sn kuralina (show-flow.json ->
broll.dur, durLocked:true) uymak icin ping-pong (ileri + ters, sonra 8sn'e
kirp) kullanilir: sert bir stream-loop atlamasi ("bas -> kare 0" sicramasi)
yerine, hareketin yon degistirdigi yumusak bir donus noktasi verir. Kaynak
zaten >=8sn ise davranis duz bir trim'den farksizdir (guvenli).

Cikti ayni encode/crop/PIP kurallarina uyar (bkz. scripts/encode_input.py
--broll): 1080x1920 crop, sessiz, libx264.

Kullanim:
  py -3.12 scripts\\prep_zsky_broll.py raw\\zsky_kurumsal.mp4 videos\\0927\\public\\broll\\kurumsal-yatirimci.mp4
"""
import argparse
import subprocess
from pathlib import Path

TARGET_DUR = 8.0


def prep(src: Path, dst: Path, dur: float = TARGET_DUR) -> None:
    src = Path(src)
    dst = Path(dst)
    if not src.is_file():
        raise FileNotFoundError(f"video dosyasi degil (klasor olamaz): {src}")
    dst.parent.mkdir(parents=True, exist_ok=True)

    # forward + reverse (ping-pong) -> concat -> hedef sureye kirp.
    # Kaynak zaten >=dur ise reverse parcasina hic ulasilmadan kirpilir
    # (duz trim ile ayni sonuc) -- guvenli fallback.
    filt = (
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,fps=30,setsar=1[base];"
        "[base]split[fwd][torev];"
        "[torev]reverse[rev];"
        f"[fwd][rev]concat=n=2:v=1:a=0,trim=duration={dur},setpts=PTS-STARTPTS[out]"
    )
    cmd = [
        "ffmpeg", "-y", "-i", str(src),
        "-filter_complex", filt,
        "-map", "[out]",
        "-an",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-g", "15", "-bf", "0", "-tune", "fastdecode", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(dst),
    ]
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("src", help="ZSky ham klip (kisa, orn. ~5sn)")
    p.add_argument("dst", help="videos/<id>/public/broll/<slot>.mp4 hedefi")
    p.add_argument("--dur", type=float, default=TARGET_DUR, help="hedef sure (varsayilan 8.0 - show lock)")
    args = p.parse_args()
    prep(Path(args.src), Path(args.dst), dur=args.dur)


if __name__ == "__main__":
    main()
