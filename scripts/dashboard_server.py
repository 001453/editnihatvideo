# -*- coding: utf-8 -*-
"""Yerel dashboard: surukle-birak upload, hazirla, studio ac."""
from __future__ import annotations

import cgi
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent
VIDEOS = ROOT / "videos"
INBOX = ROOT / "_inbox"
DASH = ROOT / "dashboard.html"
CAPS_PAGE = ROOT / "captions.html"
PORT = 8765
PY = sys.executable

JOBS: dict[str, dict] = {}


def py312():
    try:
        r = subprocess.run(
            ["py", "-3.12", "-c", "import sys; print(sys.executable)"],
            capture_output=True, text=True,
        )
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    except Exception:
        pass
    return PY


def sanitize_id(raw: str) -> str:
    s = unquote(raw or "").strip()
    s = re.sub(r"\.mp4$", "", s, flags=re.I)
    s = re.sub(r"[^\w\-]+", "", s, flags=re.U)
    return s


def set_job(vid, **kw):
    JOBS.setdefault(vid, {"id": vid, "log": []})
    JOBS[vid].update(kw)
    if "msg" in kw:
        JOBS[vid]["log"].append(kw["msg"])
        JOBS[vid]["log"] = JOBS[vid]["log"][-60:]


def _kill_pid_tree(pid: int) -> None:
    if not pid:
        return
    try:
        if os.name == "nt":
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(pid)],
                capture_output=True, text=True,
            )
        else:
            os.kill(pid, 15)
    except Exception:
        pass


def prepare_worker(vid: str, source: str, account: str, force: bool = False, only: str = "all"):
    set_job(vid, status="running", msg=f"basliyor ({only})", pid=None)
    try:
        src = Path(source) if source else None
        cmd = [
            py312(), str(SCRIPTS / "prepare_video.py"), vid,
            "--account", account,
            "--quality", "draft",
            "--only", only,
        ]
        if src and src.is_file():
            cmd.extend(["--source", str(src)])
        # force sadece acikca istendiğinde; paket silinmesin
        if force and only == "all":
            cmd.append("--force")
        set_job(vid, msg=" ".join(cmd))
        # Canli log: bitene kadar buffer'da bekletme
        proc = subprocess.Popen(
            cmd,
            cwd=str(ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )
        set_job(vid, pid=proc.pid)
        assert proc.stdout is not None
        for line in proc.stdout:
            line = (line or "").rstrip()
            if line:
                set_job(vid, msg=line[:400])
        rc = proc.wait()
        set_job(vid, pid=None)
        if rc != 0:
            set_job(vid, status="error", msg=f"hata kodu {rc}")
            return
        prompt = ""
        p = VIDEOS / vid / "PACKAGE_ME.txt"
        if p.exists():
            prompt = p.read_text(encoding="utf-8").strip()
        set_job(vid, status="ready", msg=f"tamam ({only})", prompt=prompt)
    except Exception as e:
        set_job(vid, status="error", msg=str(e), pid=None)


def rebuild_video(vid: str, *, force_template: bool = False):
    dest = VIDEOS / vid
    builder = dest / "build_composition.py"
    template = ROOT / "template" / "build_composition.py"
    if not dest.exists():
        return False, "klasor yok"
    if template.exists():
        # Sadece template daha yeniyse kopyala — her rebuild’de gereksiz IO yok
        if force_template or (not builder.exists()) or (
            template.stat().st_mtime > builder.stat().st_mtime
        ):
            shutil.copy2(template, builder)
    if not builder.exists():
        return False, "build_composition.py yok"
    r = subprocess.run(
        [py312(), str(builder)],
        cwd=str(dest),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    out = ((r.stdout or "") + (r.stderr or "")).strip()
    if r.returncode != 0:
        return False, out[-800:] or f"hata {r.returncode}"
    return True, out[-400:] or "video güncellendi"


def _set_html_attr(tag: str, name: str, val: str) -> str:
    if re.search(rf'\b{name}="[^"]*"', tag):
        return re.sub(rf'\b{name}="[^"]*"', f'{name}="{val}"', tag, count=1)
    return tag[:-1] + f' {name}="{val}">'


def _set_style_prop(tag: str, prop: str, px_val: float) -> str:
    m = re.search(r'style="([^"]*)"', tag)
    px = f"{int(round(px_val))}px"
    if not m:
        return tag[:-1] + f' style="{prop}:{px}">'
    style = m.group(1)
    if re.search(rf"(?:^|;)\s*{prop}:\s*[^;]*", style):
        style = re.sub(rf"((?:^|;)\s*{prop}:\s*)[^;]*", rf"\g<1>{px}", style, count=1)
    else:
        style = style.rstrip(";") + f";{prop}:{px}"
    return tag[: m.start(1)] + style + tag[m.end(1) :]


def patch_hosts_in_html(html: str, host_id: str, *, start=None, duration=None, left=None, top=None) -> str:
    """index/cards içinde tek host açılış etiketini anında güncelle."""
    m = re.search(rf'(<div\b[^>]*\bid="{re.escape(host_id)}"[^>]*>)', html, re.I)
    if not m:
        return html
    tag = m.group(1)
    if start is not None:
        tag = _set_html_attr(tag, "data-start", f"{float(start):.2f}")
    if duration is not None:
        tag = _set_html_attr(tag, "data-duration", f"{float(duration):.2f}")
    if left is not None:
        tag = _set_style_prop(tag, "left", float(left))
    if top is not None:
        tag = _set_style_prop(tag, "top", float(top))
    return html[: m.start()] + tag + html[m.end() :]


def patch_video_files(vid: str, mutator) -> int:
    """index.html + public/index.html + (opsiyonel) cards.html üzerinde mutator(html)->html."""
    dest = VIDEOS / vid
    n = 0
    for rel in ("index.html", "public/index.html", "cards.html"):
        path = dest / rel
        if not path.exists():
            continue
        old = path.read_text(encoding="utf-8")
        new = mutator(old, rel)
        if new != old:
            path.write_text(new, encoding="utf-8")
            n += 1
    return n


def fast_patch_card(vid: str, card_id: str, start=None, duration=None, delete: bool = False):
    """Full rebuild yok — cards + index anında patch."""
    ok, msg = update_card_timing(vid, card_id, start=start, duration=duration, delete=delete)
    if not ok:
        return False, msg
    cid = card_id.strip()
    if cid.endswith("-host"):
        host = cid
        base = cid[: -len("-host")]
    else:
        host = f"{cid}-host"
        base = cid

    def mut(html, rel):
        if delete:
            if rel == "cards.html":
                return html  # update_card_timing already did
            # index’ten host bloğunu çıkar
            m = re.search(rf'<div\b[^>]*\bid="{re.escape(host)}"[^>]*>', html, re.I)
            if not m:
                return html
            start_i = m.start()
            rest = html[m.end() :]
            next_m = re.search(r'<div\b[^>]*\bclass="[^"]*\bcard-host\b', rest, re.I)
            end_i = m.end() + next_m.start() if next_m else len(html)
            return re.sub(r"\n{3,}", "\n\n", html[:start_i] + html[end_i:])
        if rel == "cards.html":
            return html
        return patch_hosts_in_html(html, host, start=start, duration=duration)

    n = patch_video_files(vid, mut)
    return True, f"{msg} · anında kaydedildi ({n} dosya)"


def fast_patch_caption_pos(vid: str, x: int, y: int):
    """Ortak konum — cap-*-host left/top, rebuild yok.
    KİLİT (2026-09, kilit/kilit-aç): override'lı (x/y'si kendine özel set edilmiş)
    satırların host'unu ATLA — onlar zaten kendi konumunda kalmalı, ortak taşımaya
    dahil olmamalı (project.json'daki gerçekle anında-patch görüntüsü uyuşsun)."""
    overridden = set()
    proj_path = VIDEOS / vid / "project.json"
    if proj_path.exists():
        try:
            proj = json.loads(proj_path.read_text(encoding="utf-8"))
            for i, c in enumerate(proj.get("captions") or []):
                if isinstance(c, dict) and c.get("x") is not None and c.get("y") is not None:
                    overridden.add(i)
        except Exception:
            pass

    def mut(html, rel):
        if rel == "cards.html":
            return html

        def repl(m):
            tag = m.group(0)
            idm = re.search(r'\bid="cap-(\d+)-host"', tag)
            if idm and int(idm.group(1)) in overridden:
                return tag
            tag = _set_style_prop(tag, "left", x)
            tag = _set_style_prop(tag, "top", y)
            return tag

        return re.sub(r'<div\b[^>]*\bid="cap-\d+-host"[^>]*>', repl, html)

    n = patch_video_files(vid, mut)
    return n, f"altyazı konumu yatay={x} dikey={y} · anında kaydedildi ({n} dosya)"


def fast_patch_caption_item_pos(
    vid: str,
    indices,
    *,
    x=None,
    y=None,
    dx=None,
    dy=None,
    step: int = 40,
    reset: bool = False,
):
    """Kilit-açık modu: sadece seçili altyazı(lar) — project.json'a x/y override
    yazar (veya reset=True ise override'ı kaldırıp ortak konuma döndürür), sonra
    sadece o cap-{i:03d}-host div'lerini anında patch eder (rebuild yok)."""
    path = VIDEOS / vid / "project.json"
    if not path.exists():
        return False, "project.json yok", {}
    project = json.loads(path.read_text(encoding="utf-8"))
    caps = project.get("captions") or []
    layout = project.get("layout") or {}
    shared_cap = layout.get("caption") or {"x": 40, "y": 1208}
    shared_x = int(shared_cap.get("x") or 40)
    shared_y = int(shared_cap.get("y") or 1208)
    # KİLİT (2026-09, düzeltme): tek satır override'ları da w/h'yi asla kendi
    # belirlemez, hep ortak kutunun yüksekliğini kullanır — sınır da ona göre.
    shared_h = max(int(shared_cap.get("h") or 400), 400)

    updated: dict[int, tuple[int, int]] = {}
    for raw_i in indices or []:
        try:
            i = int(raw_i)
        except Exception:
            continue
        if i < 0 or i >= len(caps) or not isinstance(caps[i], dict):
            continue
        c = caps[i]
        if reset:
            c.pop("x", None)
            c.pop("y", None)
            updated[i] = (shared_x, shared_y)
            continue
        base_x = int(c.get("x")) if c.get("x") is not None else shared_x
        base_y = int(c.get("y")) if c.get("y") is not None else shared_y
        nx, ny = base_x, base_y
        if x is not None:
            nx = int(x)
        if y is not None:
            ny = int(y)
        if dx is not None:
            nx = base_x + int(dx) * step
        if dy is not None:
            ny = base_y + int(dy) * step
        nx = max(0, min(nx, 1000))
        # KİLİT (2026-09, elle taşıma): bu fonksiyon HER ZAMAN elle taşınan tek
        # tek satırlara yazıyor (override) — metin kutunun ortasında olduğu için
        # tam kutu boyu kadar pay şart değil, "bıraktığın yerde kalsın" ilkesiyle
        # build_engine.py caption_layout_for() ile aynı gevşetilmiş sınır kullanılır.
        ny = max(0, min(ny, min(1920 - shared_h + 140, 1920 - 40)))
        c["x"], c["y"] = nx, ny
        updated[i] = (nx, ny)

    if not updated:
        return False, "geçerli satır yok", {}

    path.write_text(json.dumps(project, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def mut(html, rel):
        if rel == "cards.html":
            return html
        out = html
        for i, (nx, ny) in updated.items():
            cid = f"cap-{i:03d}-host"

            def repl(m, nx=nx, ny=ny):
                tag = m.group(0)
                tag = _set_style_prop(tag, "left", nx)
                tag = _set_style_prop(tag, "top", ny)
                return tag

            out = re.sub(rf'<div\b[^>]*\bid="{re.escape(cid)}"[^>]*>', repl, out)
        return out

    n = patch_video_files(vid, mut)
    bits = ", ".join(f"#{i+1}:({nx},{ny})" for i, (nx, ny) in sorted(updated.items()))
    verb = "sıfırlandı (ortak konuma döndü)" if reset else "taşındı"
    return True, f"{len(updated)} altyazı {verb} [{bits}] · anında kaydedildi ({n} dosya)", updated


def _px(style: str, prop: str):
    m = re.search(rf"(?:^|;)\s*{prop}:\s*(-?[\d.]+)px", style or "")
    return float(m.group(1)) if m else None


def sync_cards_public_from_cards_html(vid: str):
    """cards.html'deki (Stüdyo'dan NIHAT_SYNC_ONLY ile senkronlanmış) kart
    konum/zamanlamasını export'un okuduğu public/index.html'e anında yansıtır.
    Bu, altyazılar için önceden çözülen 'kaldığı yerde kayıt olsun' sorununun
    kartlar için aynısıdır: sync_cards_from_index() SADECE cards.html'e
    yazıyor, public/index.html hızlı (NIHAT_SYNC_ONLY) yolda hiç
    güncellenmiyordu. cards.html burada nihai kaynak kabul edilir; orada
    artık bulunmayan kart public/index.html'den de silinir.

    Döner: (patch_count, deleted_count, files_changed)
    """
    dest = VIDEOS / vid
    cards_path = dest / "cards.html"
    pub_path = dest / "public" / "index.html"
    if not cards_path.exists() or not pub_path.exists():
        return 0, 0, 0

    cards_html = cards_path.read_text(encoding="utf-8")
    pub_html = pub_path.read_text(encoding="utf-8")

    host_re = re.compile(r'<div\b[^>]*\bid="(card-[^"]+-host)"[^>]*>', re.I)

    info = {}
    for m in host_re.finditer(cards_html):
        tag = m.group(0)
        hid = m.group(1)
        sm = re.search(r'data-start="([^"]*)"', tag)
        dm = re.search(r'data-duration="([^"]*)"', tag)
        tm = re.search(r'data-track-index="([^"]*)"', tag)
        style_m = re.search(r'style="([^"]*)"', tag)
        style = style_m.group(1) if style_m else ""
        info[hid] = {
            "start": sm.group(1) if sm else None,
            "duration": dm.group(1) if dm else None,
            "track_index": tm.group(1) if tm else None,
            "left": _px(style, "left"),
            "top": _px(style, "top"),
            "width": _px(style, "width"),
            "height": _px(style, "height"),
        }

    pub_ids = [m.group(1) for m in host_re.finditer(pub_html)]

    patch_count = 0

    def repl(m):
        nonlocal patch_count
        hid = m.group(1)
        d = info.get(hid)
        if not d:
            return m.group(0)
        tag = m.group(0)
        orig = tag
        if d["start"] is not None:
            tag = _set_html_attr(tag, "data-start", d["start"])
        if d["duration"] is not None:
            tag = _set_html_attr(tag, "data-duration", d["duration"])
        if d["track_index"] is not None:
            tag = _set_html_attr(tag, "data-track-index", d["track_index"])
        if d["left"] is not None:
            tag = _set_style_prop(tag, "left", d["left"])
        if d["top"] is not None:
            tag = _set_style_prop(tag, "top", d["top"])
        if d["width"] is not None:
            tag = _set_style_prop(tag, "width", d["width"])
        if d["height"] is not None:
            tag = _set_style_prop(tag, "height", d["height"])
        if tag != orig:
            patch_count += 1
        return tag

    new_pub = host_re.sub(repl, pub_html)

    # cards.html'de artık olmayan kartları public/index.html'den de sil
    # (nihai kaynak cards.html; Stüdyo'da silinen kart export'ta da kalkmalı)
    deleted = 0
    stale_ids = [hid for hid in pub_ids if hid not in info]
    for hid in stale_ids:
        m = re.search(rf'<div\b[^>]*\bid="{re.escape(hid)}"[^>]*>', new_pub, re.I)
        if not m:
            continue
        start_i = m.start()
        rest = new_pub[m.end():]
        next_m = re.search(r'<div\b[^>]*\bclass="[^"]*\bcard-host\b', rest, re.I)
        end_i = m.end() + next_m.start() if next_m else len(new_pub)
        new_pub = re.sub(r"\n{3,}", "\n\n", new_pub[:start_i] + new_pub[end_i:])
        deleted += 1

    files_changed = 0
    if new_pub != pub_html:
        pub_path.write_text(new_pub, encoding="utf-8")
        files_changed = 1

    return patch_count, deleted, files_changed


def sync_studio_caption_items(vid: str, *, patch_root: bool = False):
    """Stüdyoda tek tek (ya da bir kerede birçok farklı) altyazı kutusu sürüklenip
    bırakıldığında, HER birini kendi project.json satırına (captions[i].x/y) ayrı
    ayrı yazar — eski sync_caption_layout_from_index gibi tek bir ortak medyana
    indirgemez (kullanıcı farklı altyazıları farklı yerlere taşıyınca çoğu yanlış
    yere gidiyordu).

    Stüdyo HER ZAMAN kök index.html'e yazar; bu fonksiyon onu SADECE OKUR (taban
    referans = o dosyadaki host'un o anki left/top'u — biz onu değiştirmediğimiz
    sürece sabit kalır, art arda yoklamalarda çift sayım riski olmaz).

    patch_root=False (otomatik/arka plan yoklama): sadece project.json + export'un
    okuduğu public/index.html anında güncellenir; Stüdyo'nun kendi canlı dosyasına
    dokunulmaz — oturumu bozmaz.
    patch_root=True (kullanıcı elle "Şeritten/konumu al" dediğinde): kök index.html
    de güncellenir ve o id'ler için artık "tüketilmiş" olan gsap.set kalıntıları
    silinir (böylece Stüdyo'yu yeniden açtığında/yenilediğinde temiz taban görür,
    aynı fark ikinci kez toplanmaz).
    """
    dest = VIDEOS / vid
    idx_path = dest / "index.html"
    proj_path = dest / "project.json"
    if not idx_path.exists() or not proj_path.exists():
        return False, "dosyalar yok", 0

    idx = idx_path.read_text(encoding="utf-8")

    last: dict[str, tuple[float, float]] = {}
    for m in re.finditer(r'gsap\.set\(\s*"#(cap-\d+(?:-host)?)"\s*,\s*\{([^}]*)\}\s*\)', idx):
        sel, body = m.group(1), m.group(2)
        xm = re.search(r"x:\s*(-?[\d.]+)", body)
        ym = re.search(r"y:\s*(-?[\d.]+)", body)
        dx = float(xm.group(1)) if xm else 0.0
        dy = float(ym.group(1)) if ym else 0.0
        last[sel] = (dx, dy)  # son eşleşme kazanır — Stüdyo eskisini silmez, ekler

    if not last:
        return True, "sürüklenmiş altyazı yok", 0

    by_index: dict[int, tuple[float, float, bool]] = {}
    for sel, (dx, dy) in last.items():
        m = re.match(r"cap-(\d+)(-host)?$", sel)
        if not m:
            continue
        i = int(m.group(1))
        is_host = bool(m.group(2))
        if i not in by_index or is_host:
            by_index[i] = (dx, dy, is_host)

    project = json.loads(proj_path.read_text(encoding="utf-8"))
    caps = project.get("captions") or []
    layout = project.get("layout") or {}
    shared_cap = layout.get("caption") or {"x": 48, "y": 1320, "w": 984, "h": 280}
    shared_w = max(int(shared_cap.get("w") or 1000), 480)
    shared_h = max(int(shared_cap.get("h") or 400), 400)

    updated: dict[int, tuple[int, int]] = {}
    consumed_sels: list[str] = []
    for i, (dx, dy, is_host) in by_index.items():
        if i < 0 or i >= len(caps) or not isinstance(caps[i], dict):
            continue
        c = caps[i]
        cw = int(c["w"]) if c.get("w") is not None else shared_w
        ch = int(c["h"]) if c.get("h") is not None else shared_h
        cw = max(480, min(cw, 1000))
        ch = max(ch, 400)

        host_m = re.search(rf'id="cap-{i:03d}-host"[^>]*style="([^"]*)"', idx)
        base_x = _px(host_m.group(1), "left") if host_m else None
        base_y = _px(host_m.group(1), "top") if host_m else None
        if base_x is None:
            base_x = float(c.get("x")) if c.get("x") is not None else float(shared_cap.get("x", 48))
        if base_y is None:
            base_y = float(c.get("y")) if c.get("y") is not None else float(shared_cap.get("y", 1320))

        nx = int(round(max(0, min(base_x + dx, 1080 - cw - 40))))
        # KİLİT (2026-09, elle taşıma): Stüdyoda elle bırakılan yer — build_engine.py
        # caption_layout_for() ile aynı gevşetilmiş sınır (metin kutu içinde
        # ortalı, tam kutu payı gerekmiyor).
        ny = int(round(max(0, min(base_y + dy, min(1920 - ch + 140, 1920 - 40)))))
        cur_x = int(c["x"]) if c.get("x") is not None else None
        cur_y = int(c["y"]) if c.get("y") is not None else None
        if cur_x == nx and cur_y == ny:
            continue
        c["x"], c["y"] = nx, ny
        updated[i] = (nx, ny)
        consumed_sels.append(f"cap-{i:03d}")
        consumed_sels.append(f"cap-{i:03d}-host")

    if not updated:
        return True, "değişiklik yok (zaten güncel)", 0

    proj_path.write_text(json.dumps(project, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def mut(html, rel):
        if rel == "cards.html":
            return html
        out = html

        def repl(m, upd=updated):
            tag = m.group(0)
            idm = re.search(r'\bid="cap-(\d+)-host"', tag)
            if not idm or int(idm.group(1)) not in upd:
                return tag
            nx, ny = upd[int(idm.group(1))]
            tag = _set_style_prop(tag, "left", nx)
            tag = _set_style_prop(tag, "top", ny)
            return tag

        out = re.sub(r'<div\b[^>]*\bid="cap-\d+-host"[^>]*>', repl, out)
        return out

    pub_path = dest / "public" / "index.html"
    n = 0
    if pub_path.exists():
        old = pub_path.read_text(encoding="utf-8")
        new = mut(old, "index.html")
        if new != old:
            pub_path.write_text(new, encoding="utf-8")
            n += 1

    if patch_root:
        new_root = mut(idx, "index.html")
        for sel in consumed_sels:
            new_root = re.sub(
                r'\s*(?:gsap|tl)\.set\(\s*"#' + re.escape(sel) + r'"\s*,\s*\{[^}]*\}\s*\)\s*;?',
                "",
                new_root,
            )
        if new_root != idx:
            idx_path.write_text(new_root, encoding="utf-8")
            n += 1

    bits = ", ".join(f"#{i+1}:({nx},{ny})" for i, (nx, ny) in sorted(updated.items()))
    return True, f"{len(updated)} altyazı Stüdyodan alındı [{bits}] · ({n} dosya)", len(updated)


def update_card_timing(vid: str, card_id: str, start=None, duration=None, delete: bool = False):
    """cards.html içinde kart start/duration güncelle veya sil."""
    path = VIDEOS / vid / "cards.html"
    if not path.exists():
        return False, "cards.html yok"
    html = path.read_text(encoding="utf-8")
    cid = (card_id or "").strip()
    if cid.endswith("-host"):
        cid = cid[: -len("-host")]
    if not cid:
        return False, "cardId gerekli"
    host_re = re.compile(
        rf'(<div\b[^>]*\bid="{re.escape(cid)}-host"[^>]*>)',
        re.I,
    )
    m = host_re.search(html)
    if not m:
        host_re = re.compile(
            rf'(<div\b[^>]*\bdata-card-id="{re.escape(cid)}"[^>]*>)',
            re.I,
        )
        m = host_re.search(html)
    if not m:
        return False, f"kart bulunamadi: {cid}"

    if delete:
        # Bu card-host bloğunu sonraki card-host'a kadar sil
        start_i = m.start()
        next_m = re.search(r'<div\b[^>]*\bclass="[^"]*\bcard-host\b', html[m.end():], re.I)
        end_i = m.end() + next_m.start() if next_m else len(html)
        # geriye trailing whitespace temizle
        new_html = html[:start_i] + html[end_i:]
        new_html = re.sub(r"\n{3,}", "\n\n", new_html)
        path.write_text(new_html, encoding="utf-8")
        return True, f"{cid} silindi"

    tag = m.group(1)

    if start is not None:
        tag = _set_html_attr(tag, "data-start", f"{float(start):.2f}")
    if duration is not None:
        tag = _set_html_attr(tag, "data-duration", f"{float(duration):.2f}")
    new_html = html[: m.start()] + tag + html[m.end() :]
    path.write_text(new_html, encoding="utf-8")
    bits = []
    if start is not None:
        bits.append(f"start={float(start):.2f}")
    if duration is not None:
        bits.append(f"dur={float(duration):.2f}")
    return True, f"{cid} " + " ".join(bits)


def fix_tr_captions(vid: str):
    path = VIDEOS / vid / "project.json"
    if not path.exists():
        return False, "project.json yok"
    sys.path.insert(0, str(SCRIPTS))
    from tr_text import caption_display  # noqa: E402
    project = json.loads(path.read_text(encoding="utf-8"))
    n = 0
    for c in project.get("captions") or []:
        top = caption_display(c.get("top") or "")
        bot = caption_display(c.get("bottom") or c.get("text") or "")
        if top != (c.get("top") or "") or bot != (c.get("bottom") or ""):
            n += 1
        c["top"] = top
        c["bottom"] = bot
        c["text"] = f"{top} {bot}".strip()
    path.write_text(json.dumps(project, ensure_ascii=False, indent=2), encoding="utf-8")
    return True, f"{n} satir duzeltildi / {len(project.get('captions') or [])} altyazi"


def broll_slots(vid: str):
    """timeline.json broll[] + dosya var mi."""
    dest = VIDEOS / vid
    tl_path = dest / "timeline.json"
    slots = []
    if tl_path.exists():
        try:
            tl = json.loads(tl_path.read_text(encoding="utf-8"))
            for i, b in enumerate(tl.get("broll") or []):
                fid = (b.get("id") or f"b{i+1}").strip()
                fname = (b.get("file") or f"broll/{fid}.mp4").replace("\\", "/")
                path = dest / "public" / fname
                slots.append({
                    "index": i + 1,
                    "id": fid,
                    "keyword": (b.get("keyword") or fid).upper(),
                    "start": float(b.get("start") or 0),
                    "dur": 8.0,  # locked — always 8s
                    "file": fname,
                    "ready": path.is_file() and path.stat().st_size > 1000,
                    "hint": b.get("hint") or "",
                })
        except Exception:
            pass
    return slots


def attach_broll(vid: str, slot_id: str, raw_path: Path):
    """Ham videoyu 9:16 b-roll olarak encode edip public/broll/<id>.mp4 yazar."""
    dest = VIDEOS / vid
    if not dest.exists():
        return False, "klasor yok"
    slots = broll_slots(vid)
    hit = None
    for s in slots:
        if s["id"] == slot_id or str(s["index"]) == str(slot_id) or s["keyword"].lower() == str(slot_id).lower():
            hit = s
            break
    if not hit:
        # fallback: slot_id dosya adi
        hit = {"id": sanitize_id(slot_id) or "broll", "file": f"broll/{sanitize_id(slot_id) or 'broll'}.mp4"}
    out = dest / "public" / hit["file"]
    out.parent.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(SCRIPTS))
    from encode_input import encode  # noqa: E402
    encode(raw_path, out, broll=True, quality="draft")
    # timeline pending kaldir
    tl_path = dest / "timeline.json"
    if tl_path.exists():
        tl = json.loads(tl_path.read_text(encoding="utf-8"))
        for b in tl.get("broll") or []:
            b["dur"] = 8.0  # locked
        remaining = [s for s in broll_slots(vid) if s["id"] != hit["id"] and not s["ready"]]
        tl["brollPending"] = len(remaining) > 0
        tl_path.write_text(json.dumps(tl, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return True, f"{hit.get('keyword', hit['id'])} baglandi → {hit['file']} (8s)"


def open_studio(vid: str):
    vid = sanitize_id(vid)
    dest = VIDEOS / vid
    if not dest.exists():
        return False, "klasor yok"
    env = os.environ.copy()
    env["HYPERFRAMES_SKIP_SKILLS"] = "1"
    builder = dest / "build_composition.py"
    if builder.exists() and (dest / "project.json").exists():
        subprocess.run([py312(), str(builder)], cwd=str(dest))
    subprocess.Popen(
        ["npx", "--yes", "hyperframes@0.8.30", "preview"],
        cwd=str(dest),
        env=env,
        shell=True,
    )
    return True, "Önizleme açılıyor…"


class Handler(BaseHTTPRequestHandler):
    # buyuk video upload
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        print("[%s] %s" % (self.log_date_time_string(), fmt % args))

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _json(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self._cors()
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _file(self, path: Path, ctype="text/html; charset=utf-8"):
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self._cors()
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _serve_video_file(self, path: Path):
        """Altyazı konum aracı (captions.html) için ham video akışı — Range
        destekli (206), böylece <video> tarayıcıda gerçek zamanlı ileri/geri
        sarma yapabilir (tüm dosyayı önden indirmeden)."""
        if not path.exists():
            return self._json(404, {"error": "video yok"})
        try:
            size = path.stat().st_size
            ctype = "video/mp4"
            range_header = self.headers.get("Range")
            if range_header:
                m = re.match(r"bytes=(\d*)-(\d*)", range_header.strip())
                if not m:
                    self.send_response(416)
                    self.send_header("Content-Range", f"bytes */{size}")
                    self._cors()
                    self.end_headers()
                    return
                start_s, end_s = m.groups()
                if not start_s and end_s:
                    # sonek-araligi: son N byte
                    n = int(end_s)
                    start = max(0, size - n)
                    end = size - 1
                else:
                    start = int(start_s) if start_s else 0
                    end = int(end_s) if end_s else size - 1
                end = min(end, size - 1)
                if start > end or start >= size:
                    self.send_response(416)
                    self.send_header("Content-Range", f"bytes */{size}")
                    self._cors()
                    self.end_headers()
                    return
                length = end - start + 1
                self.send_response(206)
                self.send_header("Content-Type", ctype)
                self.send_header("Accept-Ranges", "bytes")
                self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
                self.send_header("Content-Length", str(length))
                self._cors()
                self.end_headers()
                with path.open("rb") as f:
                    f.seek(start)
                    remaining = length
                    chunk = 256 * 1024
                    while remaining > 0:
                        buf = f.read(min(chunk, remaining))
                        if not buf:
                            break
                        self.wfile.write(buf)
                        remaining -= len(buf)
            else:
                self.send_response(200)
                self.send_header("Content-Type", ctype)
                self.send_header("Accept-Ranges", "bytes")
                self.send_header("Content-Length", str(size))
                self._cors()
                self.end_headers()
                with path.open("rb") as f:
                    while True:
                        buf = f.read(256 * 1024)
                        if not buf:
                            break
                        self.wfile.write(buf)
        except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError, OSError):
            # istemci sarma sirasinda onceki istegi iptal eder — normal, yut
            pass

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        u = urlparse(self.path)
        if u.path in ("/", "/dashboard", "/dashboard.html"):
            return self._file(DASH)
        if u.path in ("/captions", "/captions.html"):
            if not CAPS_PAGE.exists():
                return self._json(404, {"error": "captions.html yok"})
            return self._file(CAPS_PAGE)
        if u.path.startswith("/api/status/"):
            vid = sanitize_id(u.path.split("/")[-1])
            job = dict(JOBS.get(vid) or {"id": vid, "status": "idle", "log": []})
            # Diskteki PACKAGE_ME — hazirlik bitince prompt dogru ID ile gelsin
            ptxt = VIDEOS / vid / "PACKAGE_ME.txt"
            if ptxt.exists():
                try:
                    job["prompt"] = ptxt.read_text(encoding="utf-8").strip()
                    if job.get("status") in (None, "idle", "error") and (VIDEOS / vid / "project.json").exists():
                        caps = []
                        try:
                            caps = json.loads((VIDEOS / vid / "project.json").read_text(encoding="utf-8")).get("captions") or []
                        except Exception:
                            pass
                        if caps and job.get("status") != "running":
                            job["status"] = "ready"
                except Exception:
                    pass
            return self._json(200, job)
        if u.path.startswith("/media/"):
            vid = sanitize_id(u.path.split("/")[-1])
            return self._serve_video_file(VIDEOS / vid / "public" / "input-video.mp4")
        if u.path.startswith("/api/project/"):
            vid = sanitize_id(u.path.split("/")[-1])
            path = VIDEOS / vid / "project.json"
            if not path.exists():
                return self._json(404, {"error": f"project.json yok: {vid}"})
            try:
                project = json.loads(path.read_text(encoding="utf-8"))
            except Exception as e:
                return self._json(500, {"error": str(e)})
            timeline = {}
            tl_path = VIDEOS / vid / "timeline.json"
            if tl_path.exists():
                try:
                    timeline = json.loads(tl_path.read_text(encoding="utf-8"))
                except Exception:
                    timeline = {}
            has_video = (VIDEOS / vid / "public" / "input-video.mp4").exists()
            return self._json(200, {"id": vid, "project": project, "timeline": timeline, "has_video": has_video})
        if u.path == "/api/videos":
            items = []
            if VIDEOS.exists():
                for d in sorted(VIDEOS.iterdir()):
                    if not d.is_dir() or d.name.startswith("_"):
                        continue
                    items.append({
                        "id": d.name,
                        "has_video": (d / "public" / "input-video.mp4").exists(),
                        "has_project": (d / "project.json").exists(),
                        "has_captions": False,
                        "package_me": (d / "PACKAGE_ME.txt").exists(),
                        "has_index": (d / "index.html").exists(),
                    })
                    if items[-1]["has_project"]:
                        try:
                            caps = json.loads((d / "project.json").read_text(encoding="utf-8")).get("captions") or []
                            items[-1]["has_captions"] = len(caps) > 0
                            items[-1]["caption_count"] = len(caps)
                        except Exception:
                            pass
            return self._json(200, {"videos": items})
        if u.path.startswith("/api/broll-slots/"):
            vid = sanitize_id(u.path.split("/")[-1])
            if not (VIDEOS / vid).exists():
                return self._json(404, {"error": "klasor yok"})
            slots = broll_slots(vid)
            return self._json(200, {"id": vid, "slots": slots, "ready": all(s["ready"] for s in slots) if slots else False})
        self._json(404, {"error": "not found"})

    def do_POST(self):
        u = urlparse(self.path)
        ctype = self.headers.get("Content-Type", "")

        if u.path == "/api/upload-prepare" and "multipart/form-data" in ctype:
            return self._upload_prepare()
        if u.path == "/api/upload-broll" and "multipart/form-data" in ctype:
            return self._upload_broll()

        n = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(n) if n else b"{}"
        try:
            data = json.loads(raw.decode("utf-8") or "{}")
        except Exception:
            return self._json(400, {"error": "bad json"})

        if u.path == "/api/cancel":
            vid = sanitize_id(data.get("id") or "")
            if not vid:
                return self._json(400, {"error": "Video ID gerekli"})
            job = JOBS.get(vid) or {}
            _kill_pid_tree(job.get("pid") or 0)
            set_job(vid, status="error", msg="iptal / kilit acildi", pid=None)
            return self._json(200, {"ok": True, "id": vid, "msg": "kilit acildi"})

        if u.path == "/api/prepare":
            vid = sanitize_id(data.get("id") or "")
            source = (data.get("source") or "").strip().strip('"')
            account = (data.get("account") or "nihat").strip()
            if not vid:
                return self._json(400, {"error": "Video ID gerekli (orn: 0910)"})
            if not source:
                return self._json(400, {"error": "dosya yolu veya surukle-birak gerekli"})
            src = Path(source)
            if not src.is_file():
                return self._json(400, {"error": f"MP4 dosyasi degil (klasor olamaz): {source}"})
            if JOBS.get(vid, {}).get("status") == "running":
                return self._json(409, {"error": "zaten calisiyor — once 'Kilidi ac'"})
            set_job(vid, status="queued", msg="kuyrukta", prompt="")
            threading.Thread(
                target=prepare_worker, args=(vid, str(src), account, False), daemon=True
            ).start()
            return self._json(200, {"ok": True, "id": vid})

        if u.path == "/api/studio":
            vid = sanitize_id(data.get("id") or "")
            ok, msg = open_studio(vid)
            return self._json(200 if ok else 400, {"ok": ok, "msg": msg})

        if u.path == "/api/rebuild":
            vid = sanitize_id(data.get("id") or "")
            ok, msg = rebuild_video(vid)
            return self._json(200 if ok else 400, {"ok": ok, "msg": msg})

        if u.path == "/api/fix-tr":
            vid = sanitize_id(data.get("id") or "")
            ok, msg = fix_tr_captions(vid)
            if ok and data.get("rebuild"):
                ok2, msg2 = rebuild_video(vid)
                msg = f"{msg} · {msg2}"
                ok = ok and ok2
            return self._json(200 if ok else 400, {"ok": ok, "msg": msg})

        if u.path == "/api/action":
            # Parçalı hızlı işlem: transcribe | captions | flag | rebuild | fix-tr
            vid = sanitize_id(data.get("id") or "")
            action = (data.get("action") or "").strip()
            account = (data.get("account") or "nihat").strip()
            if not vid:
                return self._json(400, {"error": "Video ID gerekli"})
            if action == "rebuild":
                ok, msg = rebuild_video(vid)
                return self._json(200 if ok else 400, {"ok": ok, "msg": msg})
            if action == "fix-tr":
                ok, msg = fix_tr_captions(vid)
                if ok and data.get("rebuild", True):
                    ok2, msg2 = rebuild_video(vid)
                    msg = f"{msg} · {msg2}"
                    ok = ok and ok2
                return self._json(200 if ok else 400, {"ok": ok, "msg": msg})
            if action in ("transcribe", "captions", "flag"):
                if JOBS.get(vid, {}).get("status") == "running":
                    return self._json(409, {"error": "zaten calisiyor — once 'Kilidi ac'"})
                set_job(vid, status="queued", msg=f"kuyruk: {action}", prompt="")
                threading.Thread(
                    target=prepare_worker, args=(vid, "", account, False, action), daemon=True
                ).start()
                return self._json(200, {"ok": True, "id": vid, "action": action})
            return self._json(400, {"error": f"bilinmeyen action: {action}"})

        if u.path == "/api/captions/save":
            vid = sanitize_id(data.get("id") or "")
            caps = data.get("captions")
            if not vid:
                return self._json(400, {"error": "Video ID gerekli"})
            path = VIDEOS / vid / "project.json"
            if not path.exists():
                return self._json(404, {"error": "project.json yok"})
            if not isinstance(caps, list):
                return self._json(400, {"error": "captions listesi gerekli"})
            try:
                sys.path.insert(0, str(SCRIPTS))
                from tr_text import caption_display  # noqa: E402
                project = json.loads(path.read_text(encoding="utf-8"))
                cleaned = []
                for c in caps:
                    if not isinstance(c, dict):
                        continue
                    top = caption_display(c.get("top") or "")
                    bot = caption_display(c.get("bottom") or c.get("text") or "")
                    item = dict(c)
                    item["top"] = top
                    item["bottom"] = bot
                    item["text"] = (c.get("text") or f"{top} {bot}").strip()
                    item["start"] = float(c.get("start") or 0)
                    item["end"] = float(c.get("end") or 0)
                    # KİLİT (2026-09, kilit/kilit-aç): x/y artık BİLEREK korunuyor —
                    # kilit açıkken tek tek taşınan satırların override'ı yazım
                    # düzeltip normal kaydedince kaybolmasın. w/h/fontSize/scale
                    # hâlâ kullanılmıyor, onlar temizlenir.
                    for k in ("w", "h", "fontSize", "scale"):
                        item.pop(k, None)
                    cleaned.append(item)
                project["captions"] = cleaned
                path.write_text(json.dumps(project, ensure_ascii=False, indent=2), encoding="utf-8")
                msg = f"{len(cleaned)} altyazı kaydedildi"
                if data.get("rebuild"):
                    ok, rmsg = rebuild_video(vid)
                    if not ok:
                        return self._json(500, {"error": "kaydedildi ama rebuild hata", "log": rmsg})
                    msg += " · video güncellendi — önizlemeyi yenile"
                return self._json(200, {"ok": True, "msg": msg, "count": len(cleaned)})
            except Exception as e:
                return self._json(500, {"error": str(e)})

        if u.path == "/api/card-timing":
            vid = sanitize_id(data.get("id") or "")
            card_id = (data.get("cardId") or data.get("card") or "").strip()
            if not vid:
                return self._json(400, {"error": "Video ID gerekli"})
            if not card_id:
                return self._json(400, {"error": "cardId gerekli"})
            delete = bool(data.get("delete"))
            start = data.get("start", None)
            duration = data.get("duration", data.get("dur", None))
            try:
                start_f = float(start) if start is not None and start != "" else None
                dur_f = float(duration) if duration is not None and duration != "" else None
            except Exception:
                return self._json(400, {"error": "start/duration sayi olmali"})
            # Varsayilan: aninda patch (full rebuild YOK — hizli edit)
            do_rebuild = bool(data.get("rebuild", False))
            if do_rebuild:
                ok, msg = update_card_timing(
                    vid, card_id, start=start_f, duration=dur_f, delete=delete
                )
                if not ok:
                    return self._json(400, {"error": msg})
                ok2, rmsg = rebuild_video(vid)
                if not ok2:
                    return self._json(500, {"error": f"{msg} ama rebuild hata", "log": rmsg})
                msg = f"{msg} · video güncellendi — önizlemeyi yenile"
            else:
                ok, msg = fast_patch_card(
                    vid, card_id, start=start_f, duration=dur_f, delete=delete
                )
                if not ok:
                    return self._json(400, {"error": msg})
            return self._json(200, {"ok": True, "msg": msg, "fast": not do_rebuild})

        if u.path == "/api/sync-studio-cards":
            vid = sanitize_id(data.get("id") or "")
            if not vid:
                return self._json(400, {"error": "Video ID gerekli"})
            dest = VIDEOS / vid
            if not dest.exists():
                return self._json(404, {"error": "klasor yok"})
            do_rebuild = bool(data.get("rebuild", False))
            if do_rebuild:
                ok, msg = rebuild_video(vid)
                return self._json(
                    200 if ok else 500,
                    {"ok": ok, "msg": msg if ok else "sync/rebuild hata", "log": msg},
                )
            # Hizli: sadece Studio → cards sync (full HTML rewrite yok)
            builder = dest / "build_composition.py"
            if not builder.exists():
                return self._json(400, {"error": "build_composition.py yok"})
            env = os.environ.copy()
            env["NIHAT_SYNC_ONLY"] = "1"
            r = subprocess.run(
                [py312(), str(builder)],
                cwd=str(dest),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=env,
            )
            out = ((r.stdout or "") + (r.stderr or "")).strip()
            ok = r.returncode == 0
            n_pub = 0
            if ok:
                try:
                    n_pub, _del, _files = sync_cards_public_from_cards_html(vid)
                except Exception:
                    n_pub = 0
            return self._json(
                200 if ok else 500,
                {
                    "ok": ok,
                    "msg": (out[-300:] or "sync OK") if ok else (out[-500:] or "sync hata"),
                    "fast": True,
                    "cardsPatched": n_pub,
                },
            )

        if u.path == "/api/caption-pos":
            vid = sanitize_id(data.get("id") or "")
            if not vid:
                return self._json(400, {"error": "Video ID gerekli"})
            path = VIDEOS / vid / "project.json"
            if not path.exists():
                return self._json(404, {"error": "project.json yok"})
            field = (data.get("field") or "y").strip()
            try:
                project = json.loads(path.read_text(encoding="utf-8"))
                layout = project.setdefault("layout", {})
                cap = layout.setdefault(
                    "caption",
                    {"x": 40, "y": 1208, "w": 890, "h": 400, "fontSize": 58},
                )

                # KİLİT (2026-09, yakın/punch konumu): field="yPunch" ise kamera
                # yakınlaşma (punch) anındaki altyazı konumu ayarlanır — bu SADECE
                # gömülü JS formülünü değiştirir (CAP_MANUAL_SHIFT), CSS ile anında
                # patch edilemez, bu yüzden her zaman TAM rebuild gerekir. Tek bir
                # ortak değerdir (satır bazlı override yok) — X ekseni burada
                # anlamsız çünkü punch sırasında sadece dikey kaydırma uygulanıyor.
                if field == "yPunch":
                    if data.get("reset"):
                        cap.pop("yPunch", None)
                        layout["caption"] = cap
                        path.write_text(json.dumps(project, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                        ok, rmsg = rebuild_video(vid)
                        if not ok:
                            return self._json(500, {"error": "sıfırlandı ama rebuild hata", "log": rmsg})
                        return self._json(200, {
                            "ok": True,
                            "msg": "yakın (punch) konumu otomatiğe döndü · video güncellendi",
                            "caption": cap,
                            "yPunch": None,
                        })
                    cap_h = max(int(cap.get("h") or 400), 400)
                    normal_y = int(cap.get("y") or 1208)
                    y_punch = int(cap["yPunch"]) if cap.get("yPunch") is not None else normal_y
                    step_np = int(data.get("step") or 40)
                    if data.get("y") is not None:
                        y_punch = int(data["y"])
                    if data.get("dy") is not None:
                        y_punch += int(data["dy"]) * step_np
                    y_punch = max(0, min(y_punch, 1920 - cap_h))
                    cap["yPunch"] = y_punch
                    layout["caption"] = cap
                    path.write_text(json.dumps(project, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                    ok, rmsg = rebuild_video(vid)
                    if not ok:
                        return self._json(
                            500, {"error": f"yakın konumu dikey={y_punch} ama rebuild hata", "log": rmsg, "yPunch": y_punch}
                        )
                    return self._json(200, {
                        "ok": True,
                        "msg": f"yakın (punch) konumu dikey={y_punch} · video güncellendi",
                        "caption": cap,
                        "yPunch": y_punch,
                    })

                step = int(data.get("step") or 40)
                x = int(cap.get("x") or 40)
                y = int(cap.get("y") or 1208)
                if data.get("x") is not None:
                    x = int(data["x"])
                if data.get("y") is not None:
                    y = int(data["y"])
                if data.get("dx") is not None:
                    x += int(data["dx"]) * step
                if data.get("dy") is not None:
                    y += int(data["dy"]) * step
                x = max(0, min(x, 1000))
                # KİLİT (2026-09, düzeltme): sabit "y<=1850" sınırı kutu yüksekliğini
                # (build_engine.py min 400px'e sabitliyor) hesaba katmıyordu — kutu
                # kanvasın (1920px) altına taşıp altyazı ekran dışına kayabiliyordu.
                cap_h = max(int(cap.get("h") or 400), 400)
                y = max(0, min(y, 1920 - cap_h))
                cap["x"], cap["y"] = x, y
                layout["caption"] = cap
                # KİLİT (2026-09, kilit/kilit-aç): burada artık her satırın x/y'sini
                # SİLMİYORUZ — bu ortak/paylaşılan konum. Kilit açıkken tek tek
                # taşınmış (override edilmiş) satırlar varsa onlar olduğu yerde
                # kalır; sadece override'ı OLMAYAN satırlar bu ortak konumu kullanır
                # (caption_layout_for içinde otomatik).
                path.write_text(json.dumps(project, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                msg = f"altyazi x={x} y={y}"
                # Varsayilan: aninda patch — full rebuild sadece rebuild:true
                if data.get("rebuild", False):
                    ok, rmsg = rebuild_video(vid)
                    if not ok:
                        return self._json(
                            500, {"error": msg + " ama rebuild hata", "log": rmsg, "x": x, "y": y}
                        )
                    msg += " · video güncellendi — önizlemeyi yenile"
                else:
                    _n, pmsg = fast_patch_caption_pos(vid, x, y)
                    msg = pmsg
                return self._json(200, {"ok": True, "msg": msg, "x": x, "y": y, "caption": cap, "fast": not data.get("rebuild")})
            except Exception as e:
                return self._json(500, {"error": str(e)})

        if u.path == "/api/caption-item-pos":
            vid = sanitize_id(data.get("id") or "")
            if not vid:
                return self._json(400, {"error": "Video ID gerekli"})
            idxs = data.get("indices")
            if not isinstance(idxs, list) or not idxs:
                return self._json(400, {"error": "indices (0-index liste) gerekli"})
            try:
                idxs = [int(i) for i in idxs]
            except Exception:
                return self._json(400, {"error": "indices sayi listesi olmali"})
            reset = bool(data.get("reset"))
            try:
                step = int(data.get("step") or 40)
                x = int(data["x"]) if data.get("x") is not None else None
                y = int(data["y"]) if data.get("y") is not None else None
                dx = int(data["dx"]) if data.get("dx") is not None else None
                dy = int(data["dy"]) if data.get("dy") is not None else None
            except Exception:
                return self._json(400, {"error": "x/y/dx/dy sayi olmali"})
            try:
                ok, msg, updated = fast_patch_caption_item_pos(
                    vid, idxs, x=x, y=y, dx=dx, dy=dy, step=step, reset=reset
                )
                if not ok:
                    return self._json(400, {"error": msg})
                return self._json(200, {
                    "ok": True,
                    "msg": msg,
                    "updated": {str(k): {"x": v[0], "y": v[1]} for k, v in updated.items()},
                })
            except Exception as e:
                return self._json(500, {"error": str(e)})

        if u.path == "/api/sync-studio-caption-items":
            vid = sanitize_id(data.get("id") or "")
            if not vid:
                return self._json(400, {"error": "Video ID gerekli"})
            patch_root = bool(data.get("full"))
            try:
                ok, msg, n = sync_studio_caption_items(vid, patch_root=patch_root)
                if not ok:
                    return self._json(400, {"error": msg})
                return self._json(200, {"ok": True, "msg": msg, "count": n})
            except Exception as e:
                return self._json(500, {"error": str(e)})

        self._json(404, {"error": "not found"})

    def _upload_prepare(self):
        try:
            env = {
                "REQUEST_METHOD": "POST",
                "CONTENT_TYPE": self.headers.get("Content-Type", ""),
                "CONTENT_LENGTH": self.headers.get("Content-Length", "0"),
            }
            form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ=env)
            vid_raw = form.getfirst("id") or ""
            account = (form.getfirst("account") or "nihat").strip()
            vid = sanitize_id(vid_raw)
            if not vid:
                return self._json(400, {"error": "Video ID gerekli (orn: 0910)"})
            fileitem = form["file"] if "file" in form else None
            if fileitem is None or not getattr(fileitem, "file", None):
                return self._json(400, {"error": "video dosyasi yok — surukle veya sec"})
            filename = Path(fileitem.filename or "upload.mp4").name
            if not filename.lower().endswith((".mp4", ".mov", ".m4v", ".webm")):
                return self._json(400, {"error": "sadece video dosyasi (mp4/mov)"})
            INBOX.mkdir(parents=True, exist_ok=True)
            safe = re.sub(r"[^\w.\-]+", "_", filename)
            dest = INBOX / f"{vid}__{safe}"
            with open(dest, "wb") as out:
                while True:
                    chunk = fileitem.file.read(1024 * 1024)
                    if not chunk:
                        break
                    out.write(chunk)
            if dest.stat().st_size < 1000:
                dest.unlink(missing_ok=True)
                return self._json(400, {"error": "dosya cok kucuk / bozuk"})
            if JOBS.get(vid, {}).get("status") == "running":
                return self._json(409, {"error": "zaten calisiyor — once 'Kilidi ac'", "id": vid})
            set_job(vid, status="queued", msg=f"yuklendi: {dest.name}", prompt="")
            # force=False: mevcut paketi silme; bos/yarim klasoru prepare kendisi toparlar
            threading.Thread(
                target=prepare_worker, args=(vid, str(dest), account, False), daemon=True
            ).start()
            return self._json(200, {"ok": True, "id": vid, "saved": str(dest)})
        except Exception as e:
            return self._json(500, {"error": str(e)})

    def _upload_broll(self):
        try:
            env = {
                "REQUEST_METHOD": "POST",
                "CONTENT_TYPE": self.headers.get("Content-Type", ""),
                "CONTENT_LENGTH": self.headers.get("Content-Length", "0"),
            }
            form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ=env)
            vid = sanitize_id(form.getfirst("id") or "")
            slot = (form.getfirst("slot") or form.getfirst("keyword") or "").strip()
            if not vid:
                return self._json(400, {"error": "Video ID gerekli"})
            if not slot:
                return self._json(400, {"error": "slot/keyword gerekli (vakif veya getiri)"})
            fileitem = form["file"] if "file" in form else None
            if fileitem is None or not getattr(fileitem, "file", None):
                return self._json(400, {"error": "b-roll videosu yok"})
            filename = Path(fileitem.filename or "broll.mp4").name
            if not filename.lower().endswith((".mp4", ".mov", ".m4v", ".webm")):
                return self._json(400, {"error": "sadece video (mp4/mov)"})
            INBOX.mkdir(parents=True, exist_ok=True)
            safe = re.sub(r"[^\w.\-]+", "_", filename)
            raw = INBOX / f"{vid}__broll_{sanitize_id(slot)}__{safe}"
            with open(raw, "wb") as out:
                while True:
                    chunk = fileitem.file.read(1024 * 1024)
                    if not chunk:
                        break
                    out.write(chunk)
            if raw.stat().st_size < 1000:
                raw.unlink(missing_ok=True)
                return self._json(400, {"error": "dosya cok kucuk"})
            ok, msg = attach_broll(vid, slot, raw)
            if not ok:
                return self._json(400, {"error": msg})
            rebuilt = None
            if (form.getfirst("rebuild") or "").strip() in ("1", "true", "yes"):
                ok2, msg2 = rebuild_video(vid)
                rebuilt = msg2
                if not ok2:
                    return self._json(200, {"ok": True, "msg": msg, "rebuild_error": msg2})
            slots = broll_slots(vid)
            return self._json(200, {
                "ok": True,
                "msg": msg,
                "rebuild": rebuilt,
                "slots": slots,
                "ready": all(s["ready"] for s in slots) if slots else False,
            })
        except Exception as e:
            return self._json(500, {"error": str(e)})


def main():
    if not DASH.exists():
        raise SystemExit(f"dashboard.html yok: {DASH}")
    INBOX.mkdir(parents=True, exist_ok=True)
    # Windows default socket timeout issues with large uploads — bump
    httpd = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    httpd.request_queue_size = 16
    url = f"http://127.0.0.1:{PORT}/"
    print(f"Dashboard: {url}", flush=True)
    print("Surukle-birak MP4; cozunurluk ayni kalir (hizli draft encode).", flush=True)
    threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("kapandi")


if __name__ == "__main__":
    main()
