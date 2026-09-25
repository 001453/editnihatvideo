# -*- coding: utf-8 -*-
"""Nano Banana (Gemini 2.5 Flash Image) ile show-locked ikon (coin/vault/goldbar/chart)
uretir -- Cursor/MCP GEREKMEZ. Key'i dogrudan `.cursor/mcp.json`'dan okur (kullanicinin
zaten kaydettigi dosya) ve Google'in REST API'sine bu script kendisi baglanir. Uretilen
ham gorseli (duz yesil #00FF00 zeminli) `prep_icon_bg.py` ile ayni chroma-key mantigiyla
seffaflastirip show-locked assets klasorune kaydeder.

Cursor MCP, Cursor Pro plan gerektiriyor (Hobby/free planda MCP calismiyor) -- bu script
o katmani tamamen atlar, tek gereken .cursor/mcp.json icindeki GEMINI_API_KEY.

Kullanim:
  py -3.12 scripts\\generate_icon_nanobanana.py vault "3D realistic glossy gold bank vault door, dramatic studio lighting, centered, floating in empty space, solid pure green background (#00FF00), no text, no watermark, product render style"

Cikti (varsayilan): shared/registry/assets/icon-<name>.png
"""
import argparse
import base64
import json
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
MCP_CONFIG = ROOT / ".cursor" / "mcp.json"
ASSETS_DIR = ROOT / "shared" / "registry" / "assets"
MODEL = "gemini-2.5-flash-image"
ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"


def _load_key() -> str:
    if not MCP_CONFIG.is_file():
        raise SystemExit(f"{MCP_CONFIG} bulunamadi.")
    cfg = json.loads(MCP_CONFIG.read_text(encoding="utf-8"))
    try:
        key = cfg["mcpServers"]["nanobanana"]["env"]["GEMINI_API_KEY"]
    except KeyError:
        raise SystemExit(f"{MCP_CONFIG} icinde mcpServers.nanobanana.env.GEMINI_API_KEY yok.")
    if not key or key.startswith("PASTE_"):
        raise SystemExit(f"GEMINI_API_KEY bos/placeholder -- {MCP_CONFIG} dosyasini kontrol et.")
    return key


def generate_raw(prompt: str, key: str) -> bytes:
    body = {"contents": [{"parts": [{"text": prompt}]}]}
    resp = requests.post(ENDPOINT, params={"key": key}, json=body, timeout=120)
    if not resp.ok:
        raise RuntimeError(f"Gemini API hata verdi ({resp.status_code}): {resp.text[:800]}")
    data = resp.json()
    try:
        parts = data["candidates"][0]["content"]["parts"]
    except (KeyError, IndexError):
        raise RuntimeError(f"Beklenmeyen yanit: {json.dumps(data)[:800]}")
    for part in parts:
        inline = part.get("inlineData") or part.get("inline_data")
        if inline and inline.get("data"):
            return base64.b64decode(inline["data"])
    raise RuntimeError(f"Yanitta gorsel bulunamadi (sadece metin donmus olabilir): {json.dumps(data)[:800]}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("name", help="ikon adi (coin/vault/goldbar/chart/...) -- cikti dosya adini belirler")
    p.add_argument("prompt", help="Nano Banana prompt (yesil #00FF00 zemin istemeyi unutma, 'transparent' kelimesini KULLANMA)")
    p.add_argument("--out", help="hedef PNG (varsayilan: shared/registry/assets/icon-<name>.png)")
    p.add_argument("--keep-raw", action="store_true", help="ham (yesil zeminli) PNG'yi de sakla (debug)")
    args = p.parse_args()

    key = _load_key()
    print("+ Nano Banana'ya istek gonderiliyor...", flush=True)
    raw_bytes = generate_raw(args.prompt, key)

    raw_path = ROOT / "scripts" / f"_tmp_nanobanana_{args.name}_raw.png"
    raw_path.write_bytes(raw_bytes)
    print(f"+ Ham gorsel alindi: {raw_path} ({len(raw_bytes)} bytes)", flush=True)

    dst = Path(args.out) if args.out else ASSETS_DIR / f"icon-{args.name}.png"

    sys.path.insert(0, str(ROOT / "scripts"))
    from prep_icon_bg import prep as chroma_prep  # noqa: E402

    chroma_prep(raw_path, dst)

    if not args.keep_raw:
        raw_path.unlink(missing_ok=True)

    print(f"+ Bitti: {dst}", flush=True)


if __name__ == "__main__":
    main()
