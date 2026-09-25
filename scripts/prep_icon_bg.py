# -*- coding: utf-8 -*-
"""Nano Banana ikon prep: duz yesil (#00FF00) zemin uzerinde uretilmis PNG'yi
seffaf PNG'ye cevirir (chroma-key + kenar yumusatma).

Nano Banana (Gemini 2.5 Flash Image) native alpha/seffaf PNG uretemiyor (RGB
only). Bunun yerine prompt'ta obje duz yesil zemin uzerinde uretiliyor, bu
script basit bir renk-anahtari (chroma key) ile yesili siler -- ek model/
indirme gerektirmez (rembg vb. yok), sadece Pillow.

Kullanim:
  py -3.12 scripts\\prep_icon_bg.py raw\\nanobanana_vault.png shared\\registry\\assets\\icon-vault.png
"""
import argparse
from pathlib import Path

from PIL import Image, ImageFilter

# Yesil zeminin hedef tonu (#00FF00). Prompt bu tonu istiyor; tolerans
# gercek uretimdeki hafif ton/isik sapmalarini karsilar.
KEY_R, KEY_G, KEY_B = 0, 255, 0


def _green_distance(r: int, g: int, b: int) -> float:
    """0..1 arasi: 0 = tam yesil zemin, 1 = yesilden cok uzak (obje)."""
    # Chroma-key formulu: yesil kanalin kirmizi+mavi ortalamasindan ne kadar
    # baskin oldugu -- klasik green-screen mantigi, altin/amber objeler
    # (kirmizi/sari agirlikli) icin guvenli (yesile yakin degiller).
    dominance = g - (r + b) / 2.0
    return dominance


def prep(src: Path, dst: Path, low: float = 25.0, high: float = 70.0, feather: float = 1.4) -> None:
    src = Path(src)
    dst = Path(dst)
    if not src.is_file():
        raise FileNotFoundError(f"gorsel dosyasi degil (klasor olamaz): {src}")
    dst.parent.mkdir(parents=True, exist_ok=True)

    img = Image.open(src).convert("RGBA")
    px = img.load()
    w, h = img.size
    alpha = Image.new("L", (w, h), 255)
    apx = alpha.load()

    for y in range(h):
        for x in range(w):
            r, g, b, _a = px[x, y]
            dominance = _green_distance(r, g, b)
            if dominance <= low:
                apx[x, y] = 255  # kesin obje
            elif dominance >= high:
                apx[x, y] = 0  # kesin zemin
            else:
                # low..high arasi yumusak gecis (kenar/aliasing)
                t = (dominance - low) / (high - low)
                apx[x, y] = int(255 * (1.0 - t))

    # Kenarlardaki sert/gurultulu alpha'yi hafif yumusat (feather)
    alpha = alpha.filter(ImageFilter.GaussianBlur(radius=feather))
    img.putalpha(alpha)
    img.save(dst, "PNG")
    print(f"+ yazildi: {dst} ({w}x{h}, seffaf zemin)")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("src", help="Nano Banana ham PNG (duz yesil #00FF00 zeminli)")
    p.add_argument("dst", help="shared/registry/assets/icon-<isim>.png hedefi")
    p.add_argument("--low", type=float, default=25.0, help="bu esigin alti = kesin obje (varsayilan 25)")
    p.add_argument("--high", type=float, default=70.0, help="bu esigin ustu = kesin zemin (varsayilan 70)")
    p.add_argument("--feather", type=float, default=1.4, help="kenar yumusatma blur yaricapi (varsayilan 1.4px)")
    args = p.parse_args()
    prep(Path(args.src), Path(args.dst), low=args.low, high=args.high, feather=args.feather)


if __name__ == "__main__":
    main()
