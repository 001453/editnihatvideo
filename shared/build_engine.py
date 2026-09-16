# -*- coding: utf-8 -*-
"""Reusable 9:16 talking-head: captions, IG banner, b-roll PIP, punches, SFX.

Per video: cards.html, public/broll, timeline.json, project.json
Look: shared/composition.css + sfx + fonts + banner
"""
import json
import os
import re
from html import escape
from pathlib import Path

import os as _os
# KİLİT (2026-09): shared/build_engine.py — tek ortak motor. Her video klasöründeki
# build_composition.py artık bunu çağıran ince bir shim; asıl mantık burada, TEK yerde.
ROOT = Path(_os.environ.get("NIHAT_BUILD_ROOT") or Path(__file__).resolve().parent)
_SCRIPTS = ROOT.parents[1] / "scripts"  # KİLİT (2026-09): eskiden ROOT.parent idi, hiç var olmayan bir yolu gösteriyordu
if str(_SCRIPTS) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(_SCRIPTS))
try:
    from tr_text import caption_display
except Exception:
    def caption_display(t):
        return (t or "").upper()
proj = json.loads((ROOT / "project.json").read_text(encoding="utf-8"))
timeline = {}
if (ROOT / "timeline.json").exists():
    timeline = json.loads((ROOT / "timeline.json").read_text(encoding="utf-8"))
layout = proj["layout"]
captions = proj.get("captions") or []
ACCOUNT = proj.get("account") or "nihat"
DUR = round(float(proj.get("duration") or 0), 2) or 1.0
FPS = 30
WORDS = proj.get("words") or []
cap = layout.get("caption") or {"x": 48, "y": 1180, "w": 860, "h": 420, "fontSize": 69}
# Enforce IG right-rail safe box (like/comment) — never full-bleed captions
cap["x"] = int(cap.get("x") if cap.get("x") is not None else 48)
cap["w"] = int(cap.get("w") if cap.get("w") is not None else 860)
cap["y"] = int(cap.get("y") if cap.get("y") is not None else 1180)
cap["h"] = int(cap.get("h") if cap.get("h") is not None else 420)
cap["fontSize"] = int(cap.get("fontSize") if cap.get("fontSize") is not None else 69)
# Tall enough for 2 lines at ~69px — drag down must not clip mid-glyph
cap["h"] = max(int(cap["h"]), 400)
# serbest konum — tek layout.caption (ok tuşları); Studio tek tek sürükleme yok
cap["x"] = max(0, min(int(cap["x"]), 1000))
cap["y"] = max(0, min(int(cap["y"]), 1850))
cap["w"] = max(480, min(int(cap["w"]), 1080 - cap["x"] - 40))

BROLL = list(timeline.get("broll") or [])
for _b in BROLL:
    _b["dur"] = 8.0  # locked — always 8s from start sentence
PUNCHES = [tuple(p) for p in (timeline.get("punches") or [])]
IG_BANNER = list(timeline.get("igBanner") or [])
if not IG_BANNER and DUR > 30:
    IG_BANNER = [
        {"id": "mid", "start": round(max(40.0, DUR * 0.55), 1), "dur": 4.5},
        {"id": "end", "start": round(max(50.0, DUR - 11.0), 1), "dur": 4.5},
    ]
CARD_SFX = [tuple(x) for x in (timeline.get("cardSfx") or [])]
MG = list(timeline.get("mg") or [])
PRO_CARDS = list(timeline.get("proCards") or [])
TIP_SCENES = list(timeline.get("tipScenes") or [])


def shared_dir():
    for cand in (ROOT.parent / "shared", ROOT.parents[1] / "shared"):
        if cand.exists():
            return cand
    raise SystemExit("shared/ yok")


def load_tip_explainer():
    import importlib.util

    path = shared_dir() / "tip_explainer.py"
    spec = importlib.util.spec_from_file_location("tip_explainer", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_tip = load_tip_explainer()


def sync_shared_fonts():
    """Copy Montserrat/Anton from shared/fonts → public/fonts on every build."""
    import shutil

    src = shared_dir() / "fonts"
    dst = ROOT / "public" / "fonts"
    if not src.exists():
        return
    dst.mkdir(parents=True, exist_ok=True)
    for f in src.glob("*.woff2"):
        shutil.copy2(f, dst / f.name)


sync_shared_fonts()


def q(t):
    return f"{round(float(t) * FPS) / FPS:.4f}"


def _patch_pro_config(html: str, copy: dict) -> str:
    """Patch registry CONFIG object fields from timeline proCards[].copy."""
    if not copy:
        return html
    for key, val in copy.items():
        if isinstance(val, bool):
            lit = "true" if val else "false"
            html = re.sub(rf"({re.escape(key)}\s*:\s*)(true|false)", rf"\g<1>{lit}", html)
        elif isinstance(val, (int, float)):
            html = re.sub(rf"({re.escape(key)}\s*:\s*)(-?\d+(?:\.\d+)?)", rf"\g<1>{val}", html, count=1)
        else:
            lit = json.dumps(str(val), ensure_ascii=False)
            html = re.sub(
                rf"({re.escape(key)}\s*:\s*)(\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*')",
                rf"\g<1>{lit}",
                html,
                count=1,
            )
    # Nihat talking-head: prefer dark scheme on face footage
    if "scheme" not in copy and "scheme:" in html:
        html = re.sub(r'(scheme\s*:\s*)"(light|dark)"', r'\1"dark"', html, count=1)
    return html


def pro_cards_html():
    """Mount 1–3 curated registry blocks (shared/PRO_CARDS.md) into top band."""
    if not PRO_CARDS:
        return ""
    reg = shared_dir() / "registry" / "compositions"
    dest = ROOT / "compositions"
    dest.mkdir(parents=True, exist_ok=True)
    bits = []
    for i, p in enumerate(PRO_CARDS):
        block = (p.get("block") or p.get("id") or "").strip()
        if not block:
            continue
        src = reg / f"{block}.html"
        if not src.is_file():
            src = reg / "components" / f"{block}.html"
        if not src.is_file():
            print("pro card yok:", block)
            continue
        cid = re.sub(r"[^\w\-]+", "-", (p.get("id") or block).strip()) or f"pro{i}"
        local_name = f"pro-{cid}.html"
        local = dest / local_name
        local.write_text(_patch_pro_config(src.read_text(encoding="utf-8"), p.get("copy") or {}), encoding="utf-8")
        start = float(p.get("start") or 0)
        dur = float(p.get("dur") or 7)
        left = int(p.get("x", -420))
        top = int(p.get("y", 60))
        scale = float(p.get("scale", 0.52))
        # path relative to public/index.html → ../compositions/
        bits.append(
            f'''      <div class="clip pro-card" id="pro-{cid}" data-composition-id="{escape(block)}" data-composition-src="../compositions/{local_name}" data-start="{q(start)}" data-duration="{q(dur)}" data-track-index="11" data-width="1920" data-height="1080" style="left:{left}px;top:{top}px;width:1920px;height:1080px;transform:scale({scale});transform-origin:top center;z-index:12;pointer-events:none;"></div>'''
        )
    return "\n".join(bits)


def mg_html_bits():
    """Motion-graphics overlays from timeline.json mg[] — not cards."""
    bits = []
    for i, m in enumerate(MG):
        mid = re.sub(r"[^a-zA-Z0-9_-]", "", str(m.get("id") or f"m{i}")) or f"m{i}"
        typ = (m.get("type") or "stroke").lower()
        at = float(m.get("at") or 0)
        dur = float(m.get("dur") or 1.2)
        text = (m.get("text") or "").strip()
        y = int(m.get("y") or (200 if typ == "sparkline" else 200 if typ == "ticker" else 180))
        # Never draw MG across the face (clear band y300–1100)
        if typ in ("stroke", "sparkline", "underline", "ticker", "sparks"):
            y = max(56, min(y, 220))
        if typ == "sparkline":
            bits.append(
                f'''      <div class="clip mg-host" id="mg-{mid}" data-mg="{typ}" data-start="{q(at)}" data-duration="{q(dur)}" data-track-index="7" style="left:60px;top:{y}px;width:960px;height:160px;">
        <svg class="mg-sparkline" viewBox="0 0 960 160" preserveAspectRatio="none">
          <path id="mg-{mid}-path" d="M20 120 C120 110,180 40,280 70 S420 140,520 90 S700 20,820 55 S920 100,940 88"/>
          <circle class="mg-dot" id="mg-{mid}-dot" cx="20" cy="120" r="6"/>
        </svg>
      </div>'''
            )
        elif typ == "stroke":
            bits.append(
                f'''      <div class="clip mg-host" id="mg-{mid}" data-mg="{typ}" data-start="{q(at)}" data-duration="{q(dur)}" data-track-index="7" style="left:40px;top:{y}px;width:1000px;height:24px;">
        <div class="mg-stroke" id="mg-{mid}-line"></div>
      </div>'''
            )
        elif typ == "sparks":
            dots = "".join("<i></i>" for _ in range(12))
            bits.append(
                f'''      <div class="clip mg-host" id="mg-{mid}" data-mg="{typ}" data-start="{q(at)}" data-duration="{q(dur)}" data-track-index="7" style="left:240px;top:{y}px;width:600px;height:400px;">
        <div class="mg-sparks" id="mg-{mid}-sparks">{dots}</div>
      </div>'''
            )
        elif typ == "flash":
            bits.append(
                f'''      <div class="clip mg-host" id="mg-{mid}" data-mg="{typ}" data-start="{q(at)}" data-duration="{q(max(dur, 0.2))}" data-track-index="9" style="left:0;top:0;width:1080px;height:1920px;">
        <div class="mg-flash" id="mg-{mid}-flash"></div>
      </div>'''
            )
        elif typ == "ticker":
            label = escape(text or "· MOTION ·")
            bits.append(
                f'''      <div class="clip mg-host" id="mg-{mid}" data-mg="{typ}" data-start="{q(at)}" data-duration="{q(dur)}" data-track-index="7" style="left:0;top:{y}px;width:1080px;height:56px;">
        <div class="mg-ticker"><div class="mg-ticker-track" id="mg-{mid}-track"><span>{label}</span><span>{label}</span><span>{label}</span><span>{label}</span></div></div>
      </div>'''
            )
        elif typ == "underline":
            bits.append(
                f'''      <div class="clip mg-host" id="mg-{mid}" data-mg="{typ}" data-start="{q(at)}" data-duration="{q(dur)}" data-track-index="7" style="left:40px;top:{y}px;width:920px;height:40px;">
        <div class="mg-underline" id="mg-{mid}-ul"></div>
      </div>'''
            )
        else:
            continue
    return "\n".join(bits)


def mg_js_bits():
    lines = ["          /* Motion graphics from timeline.mg */"]
    for i, m in enumerate(MG):
        mid = re.sub(r"[^a-zA-Z0-9_-]", "", str(m.get("id") or f"m{i}")) or f"m{i}"
        typ = (m.get("type") or "").lower()
        at = float(m.get("at") or 0)
        dur = float(m.get("dur") or 1.2)
        if typ == "sparkline":
            lines.append(
                f'''          (function(){{
            var path = document.getElementById("mg-{mid}-path");
            var dot = document.getElementById("mg-{mid}-dot");
            if(!path || !dot) return;
            var len = path.getTotalLength();
            var t0 = {at + 0.08:.3f};
            tl.set(path,{{strokeDasharray:len,strokeDashoffset:len}}, Math.max(0,t0-0.05));
            tl.to(path,{{strokeDashoffset:0,duration:Math.min(2.2,{dur}*0.7),ease:"power2.inOut"}}, t0);
            var obj = {{p:0}};
            tl.to(obj,{{p:1,duration:Math.min(2.2,{dur}*0.7),ease:"power2.inOut",onUpdate:function(){{
              var pt = path.getPointAtLength(obj.p * len);
              dot.setAttribute("cx", pt.x); dot.setAttribute("cy", pt.y);
            }}}}, t0);
            tl.fromTo("#mg-{mid}",{{opacity:0}},{{opacity:1,duration:0.2,immediateRender:false}}, {at});
            tl.to("#mg-{mid}",{{opacity:0,duration:0.28,ease:"power1.in"}}, {at}+{dur}-0.3);
          }})();'''
            )
        elif typ == "stroke":
            lines.append(
                f'''          (function(){{
            var el = document.getElementById("mg-{mid}-line");
            if(!el) return;
            tl.fromTo(el,{{scaleX:0,opacity:0}},{{scaleX:1,opacity:1,duration:0.45,ease:"power3.out",immediateRender:false}}, {at});
            tl.to(el,{{opacity:0,scaleX:0.2,duration:0.28,ease:"power2.in"}}, {at}+{dur}-0.3);
          }})();'''
            )
        elif typ == "sparks":
            lines.append(
                f'''          (function(){{
            var host = document.getElementById("mg-{mid}-sparks");
            if(!host) return;
            var dots = host.querySelectorAll("i");
            dots.forEach(function(d, i){{
              var ang = (i / Math.max(1,dots.length)) * Math.PI * 2;
              var dist = 90 + (i % 3) * 40;
              tl.fromTo(d,{{opacity:0,x:0,y:0,scale:0.4}},{{opacity:1,x:Math.cos(ang)*dist,y:Math.sin(ang)*dist,scale:1,duration:0.35,ease:"power2.out",immediateRender:false}}, {at}+i*0.02);
              tl.to(d,{{opacity:0,scale:0.2,duration:0.35,ease:"power1.in"}}, {at}+0.4+i*0.02);
            }});
          }})();'''
            )
        elif typ == "flash":
            lines.append(
                f'''          (function(){{
            var el = document.getElementById("mg-{mid}-flash");
            if(!el) return;
            tl.fromTo(el,{{opacity:0}},{{opacity:1,duration:0.06,ease:"none",immediateRender:false}}, {at});
            tl.to(el,{{opacity:0,duration:0.22,ease:"power2.out"}}, {at}+0.06);
          }})();'''
            )
        elif typ == "ticker":
            lines.append(
                f'''          (function(){{
            var track = document.getElementById("mg-{mid}-track");
            if(!track) return;
            tl.fromTo("#mg-{mid}",{{opacity:0,y:12}},{{opacity:1,y:0,duration:0.28,ease:"power2.out",immediateRender:false}}, {at});
            tl.fromTo(track,{{x:0}},{{x:-540,duration:Math.max(2.5,{dur}),ease:"none",immediateRender:false}}, {at});
            tl.to("#mg-{mid}",{{opacity:0,duration:0.25,ease:"power1.in"}}, {at}+{dur}-0.28);
          }})();'''
            )
        elif typ == "underline":
            lines.append(
                f'''          (function(){{
            var el = document.getElementById("mg-{mid}-ul");
            if(!el) return;
            tl.fromTo(el,{{scaleX:0,opacity:0}},{{scaleX:1,opacity:1,duration:0.4,ease:"power3.out",immediateRender:false}}, {at});
            tl.to(el,{{opacity:0,duration:0.25}}, {at}+{dur}-0.28);
          }})();'''
            )
    return "\n".join(lines) if len(lines) > 1 else ""


CAP_KW_RE = re.compile(
    r"(?i)(\d+[.,]?\d*\s*(?:bin|milyon|tl|%|m)?|"
    r"altın|altin|faiz|fon|hisse|kripto|risk|borsa|bist|acil|yatırım|yatirim|"
    r"para|kazanç|kazanc|getiri|mevduat|temettü|temettu|metal|fırsat|firsat|"
    r"doğru|dogru|yanlış|yanlis|neden|nereye|kural|eşik|esik)"
)


CAP_ANIMS = ("soft",)  # tek giriş — fazla animasyon yok (CapCut sade)
TONE_ACCENT = {
    "yumusak": "#FACC15",
    "sert": "#FF2A2A",
    "yukselis": "#C8FF00",
    "fixed": "#FFFFFF",
}


def wrap_cap_keywords(text):
    if not text:
        return ""
    parts = []
    last = 0
    for m in CAP_KW_RE.finditer(text):
        if m.start() > last:
            parts.append(escape(text[last : m.start()]))
        parts.append(f'<span class="cap-kw">{escape(m.group(0))}</span>')
        last = m.end()
    if last < len(text):
        parts.append(escape(text[last:]))
    return "".join(parts) if parts else escape(text)


def assign_word_times(n_display, timed, cap_start, cap_end):
    """Map N on-screen words onto transcript word timings (AI Video Studio karaoke)."""
    if n_display <= 0:
        return []
    if not timed:
        span = max(0.2, float(cap_end) - float(cap_start))
        step = span / n_display
        return [
            (float(cap_start) + i * step, float(cap_start) + (i + 1) * step)
            for i in range(n_display)
        ]
    m = len(timed)
    out = []
    for i in range(n_display):
        i0 = int(i * m / n_display)
        i1 = max(i0, int((i + 1) * m / n_display) - 1)
        out.append((float(timed[i0]["start"]), float(timed[i1]["end"])))
    return out


def wrap_cap_words_timed(text, times):
    """Each word → .cap-w with data-ws/data-we for karaoke light-up."""
    text = " ".join((text or "").split())
    if not text:
        return ""
    toks = text.split(" ")
    out = []
    for i, w in enumerate(toks):
        cls = "cap-w cap-kw" if CAP_KW_RE.search(w) else "cap-w"
        ws, we = times[i] if i < len(times) else (0.0, 0.0)
        out.append(
            f'<span class="{cls}" data-ws="{q(ws)}" data-we="{q(we)}">{escape(w)}</span>'
        )
    return " ".join(out)


def wrap_cap_words(text):
    return wrap_cap_words_timed(text, [])


def cap_line_scale(longest_chars, n_words=1):
    """Conservative pre-fit (CapCut-style). Final fit is measured in caption_js."""
    if longest_chars <= 0:
        return 1.0
    fs = float(cap["fontSize"])
    box = max(400.0, float(cap["w"]) - 32.0)
    # Montserrat Black + word gaps — err wide so we never start overflowing
    need = float(longest_chars) * fs * 0.72 + max(0, int(n_words) - 1) * fs * 0.2
    if need <= box:
        return 1.0
    return max(0.50, box / need)


def balance_caption_lines(top, bot):
    """Pack words into max 2 centered lines; minimize longest line so 69px stays."""
    words = f"{top} {bot}".split()
    words = [w for w in words if w]
    if not words:
        return "", ""
    if len(words) == 1:
        return "", words[0]
    if len(words) == 2:
        return words[0], words[1]
    best_top, best_bot = " ".join(words[:-1]), words[-1]
    best_score = max(len(best_top), len(best_bot))
    best_bal = abs(len(best_top) - len(best_bot))
    for i in range(1, len(words)):
        a = " ".join(words[:i])
        b = " ".join(words[i:])
        score = max(len(a), len(b))
        bal = abs(len(a) - len(b))
        if score < best_score or (score == best_score and bal < best_bal):
            best_score, best_bal = score, bal
            best_top, best_bot = a, b
    return best_top, best_bot


def fit_caption_line(text, soft_max=22):
    """One visual line only (top OR bottom). Never insert <br> — max 2 rows total."""
    text = " ".join((text or "").split())
    if not text:
        return "", 1.0
    return wrap_cap_words(text), cap_line_scale(len(text), len(text.split()))


def caption_layout_for(c):
    """Tek ortak kutu — layout.caption. Per-caption Studio sürükleme yok (kasmasın)."""
    cx = int(cap["x"])
    cy = int(cap["y"])
    cw = int(cap["w"])
    ch = int(cap["h"])
    fs = int(cap["fontSize"])
    sc = float(cap.get("scale") or 1)
    cw = max(480, min(int(cw), 1000))
    cx = max(0, min(int(cx), 1080 - cw - 40))
    cy = max(0, min(int(cy), 1850))
    ch = max(ch, 400)
    return cx, cy, cw, ch, fs, sc


def caption_items():
    parts = []
    for i, c in enumerate(captions):
        start = float(c["start"])
        end = min(float(c["end"]), DUR)
        dur = max(0.2, end - start)
        tone = "fixed" if ACCOUNT == "mehmet" else (c.get("tone") or "yumusak")
        accent = TONE_ACCENT.get(tone, "#FACC15")
        anim = CAP_ANIMS[i % len(CAP_ANIMS)]
        top = caption_display((c.get("top") or "").strip())
        bot = caption_display((c.get("bottom") or c.get("text") or "").strip())
        top, bot = balance_caption_lines(top, bot)
        # Max 2 stacked lines only — never wrap further
        top_toks = top.split() if top else []
        bot_toks = bot.split() if bot else []
        n_vis = len(top_toks) + len(bot_toks)
        w0 = int(c.get("wordStart") if c.get("wordStart") is not None else 0)
        w1 = int(c.get("wordEnd") if c.get("wordEnd") is not None else w0)
        timed = WORDS[w0 : w1 + 1] if WORDS else []
        times = assign_word_times(n_vis, timed, start, end)
        top_times = times[: len(top_toks)]
        bot_times = times[len(top_toks) :]
        top_html = wrap_cap_words_timed(top, top_times) if top else ""
        bot_html = wrap_cap_words_timed(bot, bot_times)
        longest = top if len(top) >= len(bot) else bot
        line_scale = cap_line_scale(len(longest), len(longest.split()) if longest else 1)
        cid = f"cap-{i:03d}"
        cx, cy, cw, ch, fs, sc = caption_layout_for(c)
        top_style = f' style="--lineScale:{line_scale:.2f}"' if top_html else ""
        bot_style = f' style="--lineScale:{line_scale:.2f}"'
        # Her altyazı ayrı clip — host'ta transform YOK (Studio left/top anlık)
        parts.append(
            f'''      <div class="clip cap-stage cap-host" id="{cid}-host" data-start="{q(start)}" data-duration="{q(dur)}" data-track-index="12" style="left:{cx}px;top:{cy}px;width:{cw}px;height:{ch}px;z-index:30;--capSize:{fs};--capScale:{sc:.2f};">
        <div class="cap-scale">
        <div class="cap-item tone-{tone}" id="{cid}" data-cap-start="{q(start)}" data-cap-end="{q(end)}" data-accent="{accent}" data-anim="{anim}">
          <div class="cap-top" id="{cid}-top"{top_style}>{top_html}</div>
          <div class="cap-bot" id="{cid}-bot"{bot_style}>{bot_html}</div>
        </div>
        </div>
      </div>'''
        )
    return "\n".join(parts)


def caption_js():
    # CapCut-style: measure real glyph width → uniform shrink, stay centered, no side clip.
    # Karaoke: dim → accent → spoken white. Seek-safe GSAP only.
    return r'''          function fitCapCutBlock(el){
            if(!el) return;
            var lines = Array.prototype.slice.call(el.querySelectorAll(".cap-top, .cap-bot")).filter(function(l){
              return l && String(l.textContent || "").trim();
            });
            if(!lines.length) return;
            lines.forEach(function(line){ line.style.setProperty("--lineScale", "1"); });
            void el.offsetWidth;
            var worst = 1;
            lines.forEach(function(line){
              var box = line.clientWidth || 0;
              var need = line.scrollWidth || 0;
              if(box > 0 && need > box){
                worst = Math.min(worst, box / need);
              }
            });
            worst = Math.max(0.5, Math.min(1, worst * 0.96));
            lines.forEach(function(line){
              line.style.setProperty("--lineScale", worst.toFixed(3));
            });
          }
          function fitAllCaptions(){
            document.querySelectorAll(".cap-item").forEach(fitCapCutBlock);
          }
          if(document.fonts && document.fonts.ready){
            document.fonts.ready.then(fitAllCaptions).catch(fitAllCaptions);
          } else {
            fitAllCaptions();
          }
          tl.call(fitAllCaptions, null, 0);
          document.querySelectorAll(".cap-item").forEach(function(el){
            var s = parseFloat(el.getAttribute("data-cap-start"));
            var e = parseFloat(el.getAttribute("data-cap-end"));
            var accent = el.getAttribute("data-accent") || "#FACC15";
            var words = el.querySelectorAll(".cap-w");
            var outline = "-2px -2px 0 #000, 2px -2px 0 #000, -2px 2px 0 #000, 2px 2px 0 #000, 0 2px 8px rgba(0,0,0,.5)";
            tl.call(fitCapCutBlock, [el], Math.max(0, s - 0.01));
            // Soft enter — sadece opacity (y/x YOK: Studio sürüklemesiyle çakışmasın)
            tl.fromTo(el,{autoAlpha:0},{autoAlpha:1,duration:0.28,ease:"power2.out",immediateRender:false}, s);
            words.forEach(function(w, i){
              var ws = parseFloat(w.getAttribute("data-ws"));
              var we = parseFloat(w.getAttribute("data-we"));
              if(!isFinite(ws)) ws = s + i * 0.14;
              if(!isFinite(we)) we = ws + 0.28;
              ws = Math.max(s, Math.min(e - 0.05, ws));
              we = Math.max(ws + 0.08, Math.min(e, we));
              var next = words[i+1];
              var handoff = next ? parseFloat(next.getAttribute("data-ws")) : we;
              if(!isFinite(handoff)) handoff = we;
              handoff = Math.max(ws + 0.1, Math.min(e, handoff));
              var hold = Math.max(0.1, Math.min(0.42, (handoff - ws) * 0.55));
              var settleAt = Math.min(handoff - 0.02, ws + hold);
              // Edit-safe karaoke: color/opacity only — filter+glow scrub’da kasma
              tl.set(w,{opacity:0.62,color:"#ffffff",scale:1,textShadow:outline}, s);
              tl.to(w,{
                opacity:1,color:accent,textShadow:outline,
                duration:0.12,ease:"power2.out"
              }, ws);
              tl.to(w,{
                color:"#ffffff",textShadow:outline,
                duration:0.16,ease:"power1.inOut"
              }, settleAt);
            });
            tl.to(el,{autoAlpha:0,duration:0.18,ease:"power1.in"}, Math.max(s+0.4, e-0.18));
          });
'''


def strip_hf(html):
    html = re.sub(r'\s*data-hf-id="[^"]*"', "", html)
    html = re.sub(r'\s*data-media-start="[^"]*"', "", html)
    return html


def parse_studio_gsap_sets(html: str) -> dict:
    """Studio drag often writes gsap.set('#id', {x,y}) — not seek-safe. Bake to left/top."""
    out: dict = {}
    for m in re.finditer(r'(?:gsap|tl)\.set\(\s*"#([^"]+)"\s*,\s*\{([^}]*)\}', html):
        sel, body = m.group(1), m.group(2)
        props = {}
        for pm in re.finditer(r"(\w+)\s*:\s*([-+0-9.]+)", body):
            props[pm.group(1)] = float(pm.group(2))
        if props:
            out.setdefault(sel, {}).update(props)
    return out


def _style_px(style: str, prop: str):
    mm = re.search(rf"(?:^|;)\s*{prop}:\s*([-+0-9.]+)px", style or "")
    return float(mm.group(1)) if mm else None


def _set_style_px(tag: str, **vals) -> str:
    m = re.search(r'style="([^"]*)"', tag)
    if not m:
        extras = ";".join(f"{k}:{int(round(v))}px" for k, v in vals.items() if v is not None)
        return tag[:-1] + f' style="{extras}">'
    style = m.group(1)
    for k, v in vals.items():
        if v is None:
            continue
        px = f"{int(round(v))}px"
        if re.search(rf"(?:^|;)\s*{k}:\s*[^;]*", style):
            style = re.sub(rf"((?:^|;)\s*{k}:\s*)[^;]*", rf"\g<1>{px}", style, count=1)
        else:
            style = style.rstrip(";") + f";{k}:{px}"
    return tag[: m.start(1)] + style + tag[m.end(1) :]


def _pick_studio_index(*, prefer_gsap: bool = False, prefer_cards: bool = False) -> Path | None:
    """Studio hangi dosyaya yazdıysa onu seç (gsap / kart sayısı öncelikli)."""
    candidates = [p for p in (ROOT / "index.html", ROOT / "public" / "index.html") if p.exists()]
    if not candidates:
        return None
    scored = []
    for p in candidates:
        text = p.read_text(encoding="utf-8")
        n_gsap = len(parse_studio_gsap_sets(text))
        n_cards = len(re.findall(r'id="card-[^"]+-host"', text))
        mtime = p.stat().st_mtime
        if prefer_gsap:
            scored.append((n_gsap, mtime, n_cards, p))
        elif prefer_cards:
            scored.append((n_cards, mtime, n_gsap, p))
        else:
            scored.append((mtime, n_gsap, n_cards, p))
    scored.sort(reverse=True)
    return scored[0][-1]


def sync_cards_from_index():
    """Studio timeline → cards.html: start/duration/left/top; silinen kartı çıkar."""
    cards_path = ROOT / "cards.html"
    if not cards_path.exists():
        return False
    idx_path = _pick_studio_index(prefer_cards=True)
    if not idx_path:
        return False
    # KİLİT (2026-09): index.html cards.html'den daha ESKİYSE Studio'da gerçekten
    # yeni bir şey olmamış demektir — senkronu atla. Kalıntı/stale Studio verisi
    # dashboard'un fast-patch ettiği taze cards.html'i sessizce ezmesin.
    try:
        if idx_path.stat().st_mtime <= cards_path.stat().st_mtime:
            return False
    except OSError:
        pass
    idx = idx_path.read_text(encoding="utf-8")
    cards = cards_path.read_text(encoding="utf-8")
    changed = False
    sets = parse_studio_gsap_sets(idx)

    def host_open(html, cid):
        return re.search(rf'<div[^>]*id="{re.escape(cid)}"[^>]*>', html)

    def get(tag, name):
        m = re.search(rf'{name}="([^"]*)"', tag)
        return m.group(1) if m else None

    def delete_card_block(html, cid):
        m = host_open(html, cid)
        if not m:
            return html, False
        start_i = m.start()
        rest = html[m.end() :]
        next_m = re.search(r'<div\b[^>]*\bclass="[^"]*\bcard-host\b', rest, re.I)
        end_i = m.end() + next_m.start() if next_m else len(html)
        out = html[:start_i] + html[end_i:]
        out = re.sub(r"\n{3,}", "\n\n", out)
        return out, True

    idx_ids = set(re.findall(r'id="(card-[^"]+-host)"', idx))
    card_ids = re.findall(r'id="(card-[^"]+-host)"', cards)

    # Sadece Studio'da gerçekten silindiyse çıkar (en az 1 kart kalsın + idx boş olmasın)
    if idx_ids:
        for cid in card_ids:
            if cid not in idx_ids:
                cards, did = delete_card_block(cards, cid)
                if did:
                    changed = True

    card_ids = re.findall(r'id="(card-[^"]+-host)"', cards)
    for cid in card_ids:
        i_open = host_open(idx, cid)
        c_open = host_open(cards, cid)
        if not i_open or not c_open:
            continue
        c_tag = c_open.group(0)
        new_tag = c_tag
        i_tag = strip_hf(i_open.group(0))

        for attr in ("data-start", "data-duration"):
            iv, cv = get(i_tag, attr), get(new_tag, attr)
            if iv is not None and iv != cv:
                if cv is None:
                    new_tag = new_tag[:-1] + f' {attr}="{iv}">'
                else:
                    new_tag = re.sub(rf'{attr}="[^"]*"', f'{attr}="{iv}"', new_tag, count=1)

        itrack = get(i_tag, "data-track-index")
        if itrack is not None:
            if get(new_tag, "data-track-index") is None:
                new_tag = new_tag[:-1] + f' data-track-index="{itrack}">'
            elif get(new_tag, "data-track-index") != itrack:
                new_tag = re.sub(r'data-track-index="[^"]*"', f'data-track-index="{itrack}"', new_tag, count=1)

        # Konum: Studio style left/top (+ gsap.set x/y bake)
        i_style = get(i_tag, "style") or ""
        c_style = get(new_tag, "style") or ""
        left = _style_px(i_style, "left")
        top = _style_px(i_style, "top")
        w = _style_px(i_style, "width")
        h = _style_px(i_style, "height")
        # gsap on host / fx / root
        base = cid.replace("-host", "")
        props = {}
        for key in (cid, base, f"{base}-fx", f"{base}-root"):
            props.update(sets.get(key) or {})
        if left is None:
            left = _style_px(c_style, "left")
        if top is None:
            top = _style_px(c_style, "top")
        if left is not None and "x" in props:
            left = left + props["x"]
        if top is not None and "y" in props:
            top = top + props["y"]
            # face-safe band for upper cards (disclaimer bottom OK)
            if top < 1400:
                top = max(40, min(320, top))
        style_vals = {}
        if left is not None and left != _style_px(c_style, "left"):
            style_vals["left"] = left
        if top is not None and top != _style_px(c_style, "top"):
            style_vals["top"] = top
        if w is not None and w != _style_px(c_style, "width"):
            style_vals["width"] = w
        if h is not None and h != _style_px(c_style, "height"):
            style_vals["height"] = h
        if style_vals:
            new_tag = _set_style_px(new_tag, **style_vals)

        if new_tag != c_tag:
            cards = cards.replace(c_tag, new_tag, 1)
            changed = True

    if changed:
        cards_path.write_text(cards, encoding="utf-8")
        print(f"sync_cards: {idx_path.name} -> cards.html", flush=True)
    return changed


sync_cards_from_index()


def sync_caption_layout_from_index():
    """Studio gsap.set(#cap-*) → tek layout.caption left/top. Per-caption transform yok."""
    from statistics import median

    proj_path = ROOT / "project.json"
    if not proj_path.exists():
        return 0
    idx_path = _pick_studio_index(prefer_gsap=True)
    if not idx_path:
        return 0
    idx = idx_path.read_text(encoding="utf-8")
    sets = parse_studio_gsap_sets(idx)

    xs, ys = [], []
    for sel, props in sets.items():
        if not re.match(r"^cap-\d+", sel):
            continue
        if "x" in props:
            xs.append(props["x"])
        if "y" in props:
            ys.append(props["y"])

    # Host style (Studio bazen left/top yazar)
    host_m = re.search(r'id="cap-\d+-host"[^>]*style="([^"]*)"', idx)
    host_left = _style_px(host_m.group(1), "left") if host_m else None
    host_top = _style_px(host_m.group(1), "top") if host_m else None

    if not xs and not ys and host_left is None and host_top is None:
        return 0

    project = json.loads(proj_path.read_text(encoding="utf-8"))
    layout = project.setdefault("layout", {})
    cap = layout.setdefault(
        "caption",
        {"x": 48, "y": 1320, "w": 984, "h": 280, "fontSize": 68},
    )
    base_x = float(host_left if host_left is not None else cap.get("x", 48))
    base_y = float(host_top if host_top is not None else cap.get("y", 1320))
    dx = median(xs) if xs else 0.0
    dy = median(ys) if ys else 0.0
    # Host zaten taşındıysa gsap offset'i tekrar ekleme (çift sayım)
    if host_left is not None and abs(dx) < 1:
        new_x = base_x
    else:
        new_x = base_x + dx
    if host_top is not None and abs(dy) < 1:
        new_y = base_y
    else:
        # gsap y negatif = yukarı — layout.caption top'a ekle
        new_y = base_y + dy

    new_x = int(round(max(0, min(200, new_x))))
    new_y = int(round(max(980, min(1550, new_y))))
    old = (int(cap.get("x", 0)), int(cap.get("y", 0)))
    if old == (new_x, new_y) and not xs and not ys:
        return 0
    cap["x"] = new_x
    cap["y"] = new_y
    proj_path.write_text(json.dumps(project, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"bake_caption: {idx_path.name} gsap -> layout.caption x={new_x} y={new_y} "
        f"(median d {dx:.0f},{dy:.0f})",
        flush=True,
    )
    return 1


# KİLİT (2026-09): otomatik çalıştırma kapatıldı. SHOW_STANDARD.md "Studio'da altyazı
# sürükleme yasak" der; ama bu fonksiyon her build'de index.html'deki (Studio'nun kendi
# runtime'ının bıraktığı) eski gsap/host stilini "kullanıcı Studio'da taşıdı" sanıp
# project.json -> layout.caption'ı sessizce eziyordu — /captions sayfasından yapılan
# ayarın rebuild sonrası kaybolmasının asıl sebebi buydu. Tek doğru kaynak artık
# project.json -> layout.caption (dashboard /captions + /api/caption-pos).
# sync_caption_layout_from_index()

# Hizli edit: sadece Studio → cards/layout sync, full HTML rewrite yok
if os.environ.get("NIHAT_SYNC_ONLY") == "1":
    print("sync-only OK", flush=True)
    raise SystemExit(0)

# Rebuild project layout into `cap` used below — re-read after bake
if (ROOT / "project.json").exists():
    project = json.loads((ROOT / "project.json").read_text(encoding="utf-8"))
    layout = project.get("layout") or {}
    cap = layout.get("caption") or cap
    for k in ("x", "y", "w", "h", "fontSize"):
        if k in (layout.get("caption") or {}):
            try:
                cap[k] = int(float(layout["caption"][k])) if k != "fontSize" else int(float(layout["caption"][k]))
            except Exception:
                pass
    if layout.get("caption") and layout["caption"].get("scale") is not None:
        try:
            cap["scale"] = float(layout["caption"]["scale"])
        except Exception:
            pass

def sfx_el(sid, src, start, dur, vol, track):
    return (
        f'      <audio id="{sid}" src="{src}" data-start="{q(start)}" '
        f'data-duration="{q(dur)}" data-track-index="{track}" data-volume="{vol}"></audio>'
    )


cards_html = ""
if (ROOT / "cards.html").exists():
    cards_html = (ROOT / "cards.html").read_text(encoding="utf-8").rstrip()


def uniquify_card_tracks(html: str) -> str:
    """Her kart ayrı Studio lane — kenardan kısalt/uzat çalışsın."""
    if not html:
        return html
    n = 0
    parts = []
    last = 0
    for m in re.finditer(r'<div\b[^>]*\bclass="[^"]*\bcard-host\b[^"]*"[^>]*>', html):
        n += 1
        tag = m.group(0)
        track = str(40 + n)
        if re.search(r'data-track-index="', tag):
            tag = re.sub(r'data-track-index="[^"]*"', f'data-track-index="{track}"', tag, count=1)
        else:
            tag = tag[:-1] + f' data-track-index="{track}">'
        parts.append(html[last : m.start()])
        parts.append(tag)
        last = m.end()
    parts.append(html[last:])
    return "".join(parts)


if cards_html:
    new_cards = uniquify_card_tracks(cards_html)
    if new_cards != cards_html:
        cards_html = new_cards
        (ROOT / "cards.html").write_text(cards_html + "\n", encoding="utf-8")

if not CARD_SFX:
    for m in re.finditer(
        r'id="(card-[^"]+)-host"[^>]*data-start="([0-9.]+)"',
        cards_html,
    ):
        CARD_SFX.append((m.group(1).replace("card-", ""), float(m.group(2))))

broll_html = "\n".join(
    f'''      <div class="broll-cam" id="broll-{b["id"]}-cam">
        <video id="broll-{b["id"]}" class="clip broll-vid" src="{b["file"]}" muted playsinline data-start="{q(b["start"])}" data-duration="{q(b["dur"])}" data-track-index="4"></video>
      </div>'''
    for b in BROLL
)

def ensure_ig_follow_composition():
    """Write branded animated Instagram Follow (Nihat) — one file per banner window (unique ids)."""
    src = shared_dir() / "instagram-follow.html"
    if not src.is_file():
        return False
    dest_dir = ROOT / "compositions"
    dest_dir.mkdir(parents=True, exist_ok=True)
    av_src = shared_dir() / "ig_avatar.png"
    if av_src.is_file():
        (ROOT / "public").mkdir(parents=True, exist_ok=True)
        (ROOT / "public" / "ig_avatar.png").write_bytes(av_src.read_bytes())
    base = src.read_text(encoding="utf-8")
    base = base.replace("IG_AVATAR_SRC", "../public/ig_avatar.png")
    for ig in IG_BANNER:
        iid = re.sub(r"[^\w\-]+", "", str(ig.get("id") or "a")) or "a"
        cid = f"instagram-follow-{iid}"
        html = base.replace('data-composition-id="instagram-follow"', f'data-composition-id="{cid}"')
        html = html.replace('window.__timelines["instagram-follow"]', f'window.__timelines["{cid}"]')
        html = html.replace(
            '[data-composition-id="instagram-follow"]',
            f'[data-composition-id="{cid}"]',
        )
        (dest_dir / f"{cid}.html").write_text(html, encoding="utf-8")
    return True


ensure_ig_follow_composition()

ig_html_bits = []
for ig in IG_BANNER:
    dur = float(ig.get("dur") or 4.5)
    if dur < 3.5:
        dur = 4.5
    iid = re.sub(r"[^\w\-]+", "", str(ig.get("id") or "a")) or "a"
    cid = f"instagram-follow-{iid}"
    start = float(ig["start"])
    ig_html_bits.append(
        f'''      <div class="clip ig-follow-host" id="ig-ban-{iid}" data-composition-id="{cid}" data-composition-src="../compositions/{cid}.html" data-start="{q(start)}" data-duration="{q(dur)}" data-track-index="8" data-width="1080" data-height="1920" style="left:0;top:0;width:1080px;height:1920px;z-index:18;pointer-events:none;"></div>'''
    )
ig_html = "\n".join(ig_html_bits)

def card_kind(cid, block):
    if "hook" in cid or 'class="root hook' in block or "root hook" in block:
        return "hook"
    if "disclaimer" in cid or "banner" in block:
        return "banner"
    if "chips" in block or " slim" in block:
        return "slim"
    if "stats" in block or "hero-num" in block:
        return "stats"
    if "levels" in block or "graph-card" in block:
        return "levels"
    if "warn-badge" in block or ("title red" in block and "punch" in block):
        return "punch"
    return "glass"


def card_blocks():
    out = []
    for m in re.finditer(
        r'<div[^>]*id="(card-[^"]+-host)"[^>]*data-start="([0-9.]+)"[^>]*>(.*?)(?=<div[^>]*\bid="card-[^"]+-host"|$)',
        cards_html,
        re.S,
    ):
        out.append((m.group(1), float(m.group(2)), m.group(3)[:1200]))
    return out


sfx_bits = []
for b in BROLL:
    sfx_bits.append(sfx_el(f"sfx-whoosh-{b['id']}", "sfx/whoosh-short.mp3", b["start"], 0.37, "0.16", 13))
    sfx_bits.append(
        sfx_el(
            f"sfx-whoosh-out-{b['id']}",
            "sfx/whoosh-long.mp3",
            b["start"] + b["dur"] - 0.45,
            0.45,
            "0.12",
            13,
        )
    )
for i, punch in enumerate(PUNCHES):
    t = float(punch[0])
    hold = float(punch[1]) if len(punch) > 1 else 7.0
    sfx_bits.append(sfx_el(f"sfx-cam-in-{i}", "sfx/click-soft.mp3", t, 0.37, "0.14", 14))
    sfx_bits.append(sfx_el(f"sfx-cam-sub-{i}", "sfx/sub-hit.mp3", t, 0.28, "0.11", 21))
    sfx_bits.append(sfx_el(f"sfx-cam-out-{i}", "sfx/click-soft.mp3", t + hold, 0.37, "0.10", 15))

blocks = card_blocks()
kind_by_name = {}
if not CARD_SFX:
    for cid, t, block in blocks:
        name = cid.replace("card-", "").replace("-host", "")
        CARD_SFX.append((name, t))
        kind_by_name[name] = card_kind(cid, block)
else:
    for cid, t, block in blocks:
        name = cid.replace("card-", "").replace("-host", "")
        kind_by_name[name] = card_kind(cid, block)

for name, t in CARD_SFX:
    kind = kind_by_name.get(name, "glass")
    # Açılış hook kartı + sesi kaldırıldı (tüm projeler)
    if kind == "hook" or name == "hook":
        continue
    if kind == "punch":
        sfx_bits.append(sfx_el(f"sfx-card-{name}", "sfx/pop.mp3", t, 0.42, "0.18", 16))
        sfx_bits.append(sfx_el(f"sfx-card-warn-{name}", "sfx/alarm-soft.mp3", t + 0.08, 0.28, "0.14", 17))
    elif kind == "slim":
        sfx_bits.append(sfx_el(f"sfx-card-{name}", "sfx/tick.mp3", t, 0.18, "0.12", 16))
    elif kind == "stats":
        sfx_bits.append(sfx_el(f"sfx-card-{name}", "sfx/pop.mp3", t, 0.42, "0.17", 16))
        sfx_bits.append(sfx_el(f"sfx-card-click-{name}", "sfx/click-soft.mp3", t, 0.30, "0.11", 17))
    elif kind == "banner":
        sfx_bits.append(sfx_el(f"sfx-card-{name}", "sfx/paper.mp3", t, 0.30, "0.14", 16))
    else:
        sfx_bits.append(sfx_el(f"sfx-card-{name}", "sfx/pop.mp3", t, 0.42, "0.18", 16))
        sfx_bits.append(sfx_el(f"sfx-card-click-{name}", "sfx/click-soft.mp3", t, 0.30, "0.12", 17))

for i, m in enumerate(re.finditer(r'<[^>]*\bdata-at="([0-9.]+)"[^>]*>', cards_html)):
    tag = m.group(0).lower()
    t = float(m.group(1))
    if "banner" in tag:
        continue
    # Line-type SFX density: louder / layered on emphasis, soft on kickers
    if 'data-in="slam"' in tag or "danger" in tag:
        sfx_bits.append(sfx_el(f"sfx-line-{i}", "sfx/sub-hit.mp3", t, 0.22, "0.12", 18))
        sfx_bits.append(sfx_el(f"sfx-line-t-{i}", "sfx/tick.mp3", t + 0.04, 0.14, "0.08", 22))
    elif 'data-in="back"' in tag or "title red" in tag or 'class="title' in tag:
        sfx_bits.append(sfx_el(f"sfx-line-{i}", "sfx/click-soft.mp3", t, 0.24, "0.13", 18))
        sfx_bits.append(sfx_el(f"sfx-line-b-{i}", "sfx/sub-hit.mp3", t, 0.2, "0.07", 22))
    elif 'data-in="spin"' in tag or "chip" in tag:
        sfx_bits.append(sfx_el(f"sfx-line-{i}", "sfx/tick.mp3", t, 0.14, "0.11", 18))
    elif "kicker" in tag or "chapter" in tag:
        sfx_bits.append(sfx_el(f"sfx-line-{i}", "sfx/tick.mp3", t, 0.12, "0.05", 18))
    elif "lvl" in tag:
        sfx_bits.append(sfx_el(f"sfx-line-{i}", "sfx/tick.mp3", t, 0.14, "0.09", 18))
    elif 'data-in="drop"' in tag:
        sfx_bits.append(sfx_el(f"sfx-line-{i}", "sfx/paper.mp3", t, 0.22, "0.10", 18))
    else:
        sfx_bits.append(sfx_el(f"sfx-line-{i}", "sfx/tick.mp3", t, 0.14, "0.07", 18))

# Hero 3D sting (one per video) — timeline.json "hero": {"id":"split","at":37.04}
HERO = timeline.get("hero") or {}
if HERO.get("at") is not None:
    ht = float(HERO["at"])
    sfx_bits.append(sfx_el("sfx-hero-whoosh", "sfx/whoosh-short.mp3", ht, 0.37, "0.18", 23))
    sfx_bits.append(sfx_el("sfx-hero-hit", "sfx/sub-hit.mp3", ht + 0.06, 0.28, "0.14", 25))

# One special moment per video — timeline.json "special": {"type":"drone|crash",...}
SPECIAL = timeline.get("special") or {}
if (SPECIAL.get("type") or "").lower() == "drone" and SPECIAL.get("at") is not None:
    st = float(SPECIAL["at"])
    sfx_bits.append(sfx_el("sfx-drone-whoosh", "sfx/whoosh-long.mp3", st, 0.45, "0.14", 26))
    sfx_bits.append(sfx_el("sfx-drone-tick", "sfx/tick.mp3", st + 0.08, 0.14, "0.08", 26))
elif (SPECIAL.get("type") or "").lower() == "crash" and SPECIAL.get("at") is not None:
    st = float(SPECIAL["at"])
    sfx_bits.append(sfx_el("sfx-crash-sub", "sfx/sub-hit.mp3", st, 0.28, "0.16", 26))
    sfx_bits.append(sfx_el("sfx-crash-whoosh", "sfx/whoosh-short.mp3", st, 0.32, "0.12", 26))

# Tip scenes SFX
for sc in TIP_SCENES:
    st = float(sc["start"])
    sfx_bits.append(sfx_el(f"sfx-tip-{sc.get('id')}", "sfx/whoosh-short.mp3", st, 0.35, "0.12", 27))
    sfx_bits.append(sfx_el(f"sfx-tip-tick-{sc.get('id')}", "sfx/tick.mp3", st + 0.2, 0.14, "0.08", 27))

# Whip accent on each b-roll cut (extra energy on top of whoosh)
for i, b in enumerate(BROLL):
    sfx_bits.append(sfx_el(f"sfx-whip-{b['id']}", "sfx/whoosh-long.mp3", b["start"], 0.28, "0.10", 24))


seen_count_ends = set()
for m in re.finditer(r"<[^>]*\bdata-count=[^>]*>", cards_html):
    tag = m.group(0)
    at = re.search(r'data-count-at="([0-9.]+)"', tag)
    dur = re.search(r'data-count-dur="([0-9.]+)"', tag)
    if not at:
        continue
    end_t = float(at.group(1)) + (float(dur.group(1)) if dur else 1.0)
    key = round(end_t, 2)
    if key in seen_count_ends:
        continue
    seen_count_ends.add(key)
    sfx_bits.append(
        sfx_el(f"sfx-count-{len(seen_count_ends)}", "sfx/ui-confirm.mp3", end_t, 0.22, "0.12", 19)
    )

for ig in IG_BANNER:
    sfx_bits.append(sfx_el(f"sfx-ig-{ig['id']}", "sfx/swoosh-up.mp3", ig["start"], 0.42, "0.13", 20))

for i, m in enumerate(MG):
    typ = (m.get("type") or "").lower()
    at = float(m.get("at") or 0)
    mid = re.sub(r"[^a-zA-Z0-9_-]", "", str(m.get("id") or f"m{i}")) or f"m{i}"
    if typ in ("sparks", "flash"):
        sfx_bits.append(sfx_el(f"sfx-mg-{mid}", "sfx/tick.mp3", at, 0.12, "0.08", 21))
    elif typ in ("sparkline", "stroke", "underline"):
        sfx_bits.append(sfx_el(f"sfx-mg-{mid}", "sfx/whoosh-short.mp3", at, 0.28, "0.08", 21))
    elif typ == "ticker":
        sfx_bits.append(sfx_el(f"sfx-mg-{mid}", "sfx/swoosh-up.mp3", at, 0.35, "0.09", 21))

sfx_html = "\n".join(sfx_bits)

css = (shared_dir() / "composition.css").read_text(encoding="utf-8")

broll_js = []
for b in BROLL:
    s = b["start"]
    e = b["start"] + b["dur"]
    cam = f"#broll-{b['id']}-cam"
    # Whip in/out: lateral blur-ish motion + PIP settle left
    broll_js.append(f'''
          tl.fromTo("{cam}",{{opacity:0,x:100,scale:1.08}},{{opacity:1,x:0,scale:1,duration:0.42,ease:"expo.out",immediateRender:false}}, {s});
          tl.to("{cam}",{{opacity:0,x:-72,scale:1.04,duration:0.36,ease:"power2.in"}}, {e - 0.36:.2f});
          tl.fromTo("#video-wrap",{{scale:1,x:0,y:0,borderRadius:"0px",rotation:0}},{{scale:0.30,x:-350,y:-20,borderRadius:"36px",rotation:-1.0,duration:0.42,ease:"power3.inOut",immediateRender:false}}, {s});
          tl.to("#video-wrap",{{rotation:0,duration:0.22,ease:"power1.out"}}, {s + 0.42:.2f});
          tl.to("#video-wrap",{{scale:1,x:0,y:0,borderRadius:"0px",rotation:0,duration:0.42,ease:"power3.inOut"}}, {e - 0.42:.2f});
''')
broll_js_txt = "".join(broll_js)

punch_js_lines = []
for punch in PUNCHES:
    t = float(punch[0])
    hold = float(punch[1]) if len(punch) > 1 else 7.0
    scale = float(punch[2]) if len(punch) > 2 else 1.12
    punch_js_lines.append(f"          punchHold({t}, {hold}, {scale});")
punch_js = "\n".join(punch_js_lines)

hero_id = (HERO.get("id") or "").strip()
hero_at = HERO.get("at")
hero_js = ""
if hero_id and hero_at is not None:
    hero_js = f'''
          (function(){{
            var heroHost = document.getElementById("card-{hero_id}-host");
            if(!heroHost) return;
            var fx = heroHost.querySelector(".card-fx");
            if(!fx || !fx.id) return;
            var ht = {float(hero_at)};
            var sel = "#"+fx.id;
            /* Mid-card hero 3D flourish (enter still runs at card start) */
            tl.to(sel,{{rotateY:-42,rotateX:10,scale:0.94,duration:0.26,ease:"power2.in"}}, ht);
            tl.to(sel,{{rotateY:0,rotateX:0,scale:1,duration:0.62,ease:"power4.out"}}, ht+0.26);
          }})();
'''

special_js = ""
_stype = (SPECIAL.get("type") or "").lower()
if _stype == "drone" and SPECIAL.get("at") is not None:
    st = float(SPECIAL["at"])
    sd = float(SPECIAL.get("dur") or 1.5)
    card = (SPECIAL.get("card") or "").strip()
    special_js = f'''
          (function(){{
            var st = {st}, sd = {sd};
            var cardId = {json.dumps(card)};
            var fx = null;
            if(cardId){{
              var host = document.getElementById("card-"+cardId+"-host");
              if(host) fx = host.querySelector(".card-fx");
            }}
            if(!fx){{
              document.querySelectorAll(".card-host").forEach(function(h){{
                if(fx) return;
                var s = parseFloat(h.getAttribute("data-start"))||0;
                var d = parseFloat(h.getAttribute("data-duration"))||0;
                if(st >= s && st <= s+d) fx = h.querySelector(".card-fx");
              }});
            }}
            if(!fx || !fx.id) return;
            var sel = "#"+fx.id;
            var up = Math.max(0.5, sd * 0.4);
            var down = Math.max(0.55, sd - up);
            tl.to(sel,{{scale:0.68,y:-90,rotateX:18,rotateY:-22,z:-120,duration:up,ease:"power2.inOut"}}, st);
            tl.to(sel,{{scale:1,y:0,rotateX:0,rotateY:0,z:0,duration:down,ease:"power3.out"}}, st+up);
          }})();
'''
elif _stype == "crash" and SPECIAL.get("at") is not None:
    st = float(SPECIAL["at"])
    sd = float(SPECIAL.get("dur") or 0.9)
    special_js = f'''
          (function(){{
            var st = {st}, sd = {sd};
            tl.to("#video-cam", {{scale:1.22, duration:Math.min(0.28, sd*0.35), ease:"power3.in", immediateRender:false}}, st);
            tl.to("#video-cam", {{scale:1, duration:Math.max(0.45, sd*0.65), ease:"power2.out"}}, st + Math.min(0.28, sd*0.35));
          }})();
'''

tip_html = _tip.tip_html_bits(TIP_SCENES, FPS)
tip_js = _tip.tip_js_bits(TIP_SCENES)

js = f'''
        (function(){{
          const tl = window.gsap.timeline({{paused:true}});
          const cam = "#video-cam";
          function punchHold(t, hold, scale){{
            var sc = Math.min(scale || 1.12, 1.14);
            tl.to(cam, {{scale:sc, duration:0.34, ease:"power3.out", immediateRender:false}}, t);
            tl.to(cam, {{scale:1, duration:0.55, ease:"power2.inOut"}}, t+hold);
          }}
          /* Instagram Reels motion lock (AI Video Studio tokens):
             enter ~0.42s expo.out, exit ~0.38s, soft land — no bounce/glitch. */
          var EASE_IN = "expo.out";
          var EASE_OUT = "power2.in";
          var ENTER_SEC = 0.42;
          var EXIT_SEC = 0.38;
          function enterMode(host){{
            var forced = host.getAttribute("data-enter");
            if(forced) return normalizeEnter(forced);
            var root = host.querySelector(".root");
            if(!root) return "soft";
            if(root.classList.contains("punch") || root.querySelector(".warn-badge")) return "rise";
            if(root.classList.contains("slim")) return "soft";
            if(root.classList.contains("levels") || root.classList.contains("graph-card")) return "slide";
            return "soft";
          }}
          function normalizeEnter(mode){{
            // Map legacy gimmick names → IG-pro family
            if(mode === "glitch" || mode === "slam" || mode === "snap" || mode === "zoom") return "rise";
            if(mode === "tilt" || mode === "flip" || mode === "fold" || mode === "drift") return "slide";
            if(mode === "wipe" || mode === "pop" || mode === "zoom") return "scale";
            if(mode === "soft" || mode === "rise" || mode === "slide" || mode === "scale") return mode;
            return "soft";
          }}
          var ENTER_POOL = ["soft","rise","slide","scale"];
          var enterUsed = {{}};
          function uniqueEnter(host, idx){{
            var forced = host.getAttribute("data-enter");
            if(forced){{
              forced = normalizeEnter(forced);
              host.setAttribute("data-enter", forced);
              if(!enterUsed[forced]){{
                enterUsed[forced] = 1;
                return forced;
              }}
            }}
            for(var i=0;i<ENTER_POOL.length;i++){{
              var m = ENTER_POOL[(idx+i) % ENTER_POOL.length];
              if(!enterUsed[m]){{
                enterUsed[m] = 1;
                host.setAttribute("data-enter", m);
                return m;
              }}
            }}
            return forced || ENTER_POOL[idx % ENTER_POOL.length];
          }}
          function exitMode(host){{
            var forced = host.getAttribute("data-exit");
            if(forced === "scale" || forced === "slide" || forced === "fade") return forced;
            var mode = host.getAttribute("data-enter") || enterMode(host);
            if(mode === "slide") return "slide";
            if(mode === "scale" || mode === "rise") return "scale";
            return "fade";
          }}
          function exitCard(fxSel, host, tEnd){{
            var mode = exitMode(host);
            var t = tEnd - EXIT_SEC;
            if(t < (parseFloat(host.getAttribute("data-start")) || 0) + 0.55) return;
            // Edit-safe: blur filter yok (scrub’da kasma)
            if(mode === "scale"){{
              tl.to(fxSel,{{opacity:0,scale:0.96,y:-6,duration:EXIT_SEC,ease:EASE_OUT}}, t);
            }} else if(mode === "slide"){{
              tl.to(fxSel,{{opacity:0,x:22,duration:EXIT_SEC,ease:EASE_OUT}}, t);
            }} else {{
              tl.to(fxSel,{{opacity:0,y:-4,duration:EXIT_SEC,ease:EASE_OUT}}, t);
            }}
          }}
          function progressCard(fxSel, t, dur, mode){{
            // Hold breathe scrub’da pahalı — kapalı
            return;
          }}
          /* Shell enters soft — content pieces animate on data-at. */
          function popCard(fxSel, t, mode){{
            mode = normalizeEnter(mode || "soft");
            var from, to;
            if(mode === "rise"){{
              from = {{opacity:0,y:22,scale:0.96}};
              to = {{opacity:1,y:0,scale:1,duration:ENTER_SEC,ease:EASE_IN,immediateRender:false}};
            }} else if(mode === "slide"){{
              from = {{opacity:0,x:32,scale:0.97}};
              to = {{opacity:1,x:0,scale:1,duration:ENTER_SEC,ease:EASE_IN,immediateRender:false}};
            }} else if(mode === "scale"){{
              from = {{opacity:0,scale:0.92,y:8}};
              to = {{opacity:1,scale:1,y:0,duration:ENTER_SEC,ease:EASE_IN,immediateRender:false}};
            }} else {{
              from = {{opacity:0,y:12,scale:0.98}};
              to = {{opacity:1,y:0,scale:1,duration:ENTER_SEC,ease:EASE_IN,immediateRender:false}};
            }}
            tl.fromTo(fxSel, from, to, t);
            var host = document.querySelector(fxSel);
            if(!host) return;
            var accent = host.querySelector(".card-accent");
            var sheen = host.querySelector(".card-sheen");
            var warn = host.querySelector(".warn-badge");
            if(accent){{
              tl.fromTo(accent,{{scaleY:0}},{{scaleY:1,duration:0.42,ease:EASE_IN,immediateRender:false}}, t+0.05);
            }}
            if(sheen){{
              tl.fromTo(sheen,{{x:-420,opacity:0}},{{x:860,opacity:0.7,duration:0.5,ease:"power2.out",immediateRender:false}}, t+0.12);
              tl.to(sheen,{{opacity:0,duration:0.22,ease:EASE_OUT}}, t+0.58);
            }}
            if(warn){{
              tl.fromTo(warn,{{opacity:0,scale:0.9}},{{opacity:1,scale:1,duration:0.32,ease:EASE_IN,immediateRender:false}}, t+0.14);
            }}
            host.querySelectorAll(".kicker,.title,.q,.note,.chapter,.lvl,.chip").forEach(function(el){{
              if(!el.hasAttribute("data-at")) return;
              gsap.set(el, {{opacity:0}});
            }});
          }}
          function explodeCardWords(el){{
            if(el.getAttribute("data-in") !== "words") return false;
            if(el.querySelector(".cw")) return true;
            var raw = (el.textContent || "").trim();
            if(!raw) return false;
            var parts = raw.split(/\\s+/).filter(Boolean);
            if(parts.length < 2) return false;
            el.innerHTML = parts.map(function(w){{ return '<span class="cw">'+w+'</span>'; }}).join(" ");
            return true;
          }}
          function animCardPiece(el, t, kind){{
            if(kind === "words" && explodeCardWords(el)){{
              gsap.set(el, {{opacity:1}});
              var words = el.querySelectorAll(".cw");
              words.forEach(function(w, i){{
                tl.fromTo(w,
                  {{opacity:0,y:10}},
                  {{opacity:1,y:0,duration:0.28,ease:EASE_IN,immediateRender:false}},
                  t + i * 0.055);
              }});
              return;
            }}
            // All piece kinds → same IG-pro rise (spin/slam/back demoted)
            tl.fromTo(el,
              {{opacity:0,y:12,scale:0.97}},
              {{opacity:1,y:0,scale:1,duration:0.36,ease:EASE_IN,immediateRender:false}},
              t);
          }}
          function countNum(el, t, end, dur, decimals){{
            var obj = {{v:0}};
            tl.to(obj, {{
              v:end,
              duration:dur,
              ease:"power2.out",
              onUpdate:function(){{
                if(!el) return;
                var n = decimals ? obj.v.toFixed(decimals) : String(Math.round(obj.v));
                el.textContent = n.replace(/\\B(?=(\\d{{3}})+(?!\\d))/g, ".");
              }}
            }}, t);
          }}
{caption_js()}
{broll_js_txt}
{punch_js}
{hero_js}
{special_js}
{mg_js_bits()}
{tip_js}
          var cardIdx = 0;
          document.querySelectorAll(".card-host").forEach(function(host){{
            var t = parseFloat(host.getAttribute("data-start")) || 0;
            var dur = parseFloat(host.getAttribute("data-duration")) || 4;
            var fx = host.querySelector(".card-fx");
            if(fx && fx.id){{
              var mode = uniqueEnter(host, cardIdx++);
              popCard("#"+fx.id, t, mode);
              progressCard("#"+fx.id, t, dur, mode);
              exitCard("#"+fx.id, host, t + dur);
            }} else {{
              var ban = host.querySelector(".banner");
              if(ban && ban.id){{
                tl.fromTo("#"+ban.id,{{opacity:0,y:18,scale:0.98}},{{opacity:1,y:0,scale:1,duration:0.36,ease:"power3.out",immediateRender:false}}, t);
              }}
            }}
          }});
          document.querySelectorAll("[data-at]").forEach(function(el){{
            if(el.classList.contains("banner")) return;
            var t = parseFloat(el.getAttribute("data-at"));
            var kind = el.getAttribute("data-in") || "";
            animCardPiece(el, t, kind);
          }});
          document.querySelectorAll("[data-out]").forEach(function(el){{
            var kind = el.getAttribute("data-out-kind") || "fade";
            var t = parseFloat(el.getAttribute("data-out"));
            if(kind === "scale") tl.to(el,{{opacity:0,scale:0.9,duration:0.28,ease:"power2.in"}}, t);
            else tl.to(el,{{opacity:0,duration:0.22,ease:"power2.in"}}, t);
          }});
          document.querySelectorAll("[data-count]").forEach(function(el){{
            var t = parseFloat(el.getAttribute("data-count-at") || "0");
            var end = parseFloat(el.getAttribute("data-count"));
            var decimals = parseInt(el.getAttribute("data-decimals") || "0", 10);
            var dur = parseFloat(el.getAttribute("data-count-dur") || "1");
            el.textContent = decimals ? (0).toFixed(decimals) : "0";
            countNum(el, t, end, dur, decimals);
            if(el.hasAttribute("data-scale-in")){{
              tl.fromTo(el,{{scale:0.78}},{{scale:1,duration:dur,ease:"power2.out",immediateRender:false}}, t);
            }}
          }});
          document.querySelectorAll("path[data-draw]").forEach(function(path){{
            var t = parseFloat(path.getAttribute("data-draw-at") || "0");
            var len = path.getTotalLength();
            tl.set(path,{{strokeDasharray:len,strokeDashoffset:len}}, Math.max(0, t-0.15));
            tl.to(path,{{strokeDashoffset:0,duration:1.85,ease:"power2.inOut"}}, t);
          }});
          document.querySelectorAll("[data-fill]").forEach(function(el){{
            var t = parseFloat(el.getAttribute("data-fill-at") || "0");
            var v = parseFloat(el.getAttribute("data-fill"));
            tl.fromTo(el,{{scaleX:0}},{{scaleX:v,duration:0.75,ease:"power3.out",immediateRender:false}}, t);
          }});
          var punches = {json.dumps([[float(p[0]), float(p[1]) if len(p)>1 else 7.0] for p in PUNCHES])};
          // Caption punch pulse kaldırıldı — fazla animasyon yok
          window.__timelines["talking-head-recut"] = tl;
        }})();
        /* Kart süre paneli — anında kaydet + soft yenile (full rebuild yok) */
        (function cardTimingDock(){{
          if (navigator.webdriver || window.__HF_CAPTURE__ || window.__HF_IS_RENDERING__) return;
          try {{
            if (new URLSearchParams(location.search).get("edit") === "0") return;
          }} catch (e) {{}}
          var VID = {json.dumps(ROOT.name)};
          var dock = document.createElement("div");
          dock.id = "card-timing-dock";
          dock.innerHTML = ''
            + '<div class="ctd-row">'
            + '<b id="ctd-name">kart</b>'
            + '<label>Başlangıç (sn) <input id="ctd-start" type="number" step="0.05" min="0"></label>'
            + '<label>Süre (sn) <input id="ctd-dur" type="number" step="0.05" min="0.2"></label>'
            + '<button type="button" id="ctd-m05" title="Yarım saniye kısalt">−0.5 sn</button>'
            + '<button type="button" id="ctd-p05" title="Yarım saniye uzat">+0.5 sn</button>'
            + '<button type="button" id="ctd-save">Kaydet ve gör</button>'
            + '<button type="button" id="ctd-sync" title="Alttaki şeritte değiştirdiğin süreleri yaz">Şeritten al</button>'
            + '<button type="button" id="ctd-del">Kartı sil</button>'
            + '<button type="button" id="ctd-x">Kapat</button>'
            + '</div><div class="ctd-msg" id="ctd-msg">Karta tıkla → süreyi ayarla → Kaydet ve gör. Uzun bekleme yok.</div>';
          var st = document.createElement("style");
          st.textContent = "#card-timing-dock{{position:fixed;left:0;right:0;bottom:0;z-index:99999;display:none;padding:14px 16px 18px;background:rgba(10,12,16,.94);border-top:1px solid rgba(226,184,74,.45);font-family:Segoe UI,system-ui,sans-serif;color:#f2f0ea}}" +
            "#card-timing-dock .ctd-row{{display:flex;flex-wrap:wrap;gap:10px;align-items:center}}" +
            "#card-timing-dock label{{font-size:13px;color:#9a9aaa}}" +
            "#card-timing-dock input{{width:88px;margin-left:6px;padding:8px;border-radius:8px;border:1px solid #2a2f3a;background:#0d0f14;color:#fff}}" +
            "#card-timing-dock button{{padding:10px 12px;border-radius:10px;border:1px solid #2a2f3a;background:#1a1e28;color:#fff;cursor:pointer;font-weight:650}}" +
            "#card-timing-dock #ctd-save{{background:linear-gradient(180deg,#f0d06a,#c99620);color:#1a1406;border-color:#e2b84a}}" +
            "#card-timing-dock #ctd-del{{background:#3a1515;border-color:#ff5c5c;color:#ffb4b4}}" +
            "#card-timing-dock .ctd-msg{{margin-top:8px;font-size:12px;color:#9a9aaa}}" +
            ".card-host.ctd-on{{outline:2px solid #e2b84a;outline-offset:2px}}";
          document.head.appendChild(st);
          document.body.appendChild(dock);
          var cur = null;
          var obs = null;
          var saveTimer = null;
          function readIntoInputs(host){{
            if(!host) return;
            document.getElementById("ctd-start").value = parseFloat(host.getAttribute("data-start")||0).toFixed(2);
            document.getElementById("ctd-dur").value = parseFloat(host.getAttribute("data-duration")||4).toFixed(2);
          }}
          function watch(host){{
            if(obs){{ try{{ obs.disconnect(); }}catch(e){{}} obs = null; }}
            if(!host || !window.MutationObserver) return;
            obs = new MutationObserver(function(){{ readIntoInputs(host); }});
            obs.observe(host, {{ attributes:true, attributeFilter:["data-start","data-duration","data-track-index"] }});
          }}
          function show(host){{
            cur = host;
            document.querySelectorAll(".card-host.ctd-on").forEach(function(h){{ h.classList.remove("ctd-on"); }});
            host.classList.add("ctd-on");
            document.getElementById("ctd-name").textContent = host.getAttribute("data-card-id") || host.id;
            readIntoInputs(host);
            watch(host);
            document.getElementById("ctd-msg").textContent = "±0.5 sn veya kutuya yaz → Kaydet ve gör. Şerit kenarı = süre, ortası = başlangıç.";
            dock.style.display = "block";
          }}
          function hide(){{
            dock.style.display = "none";
            document.querySelectorAll(".card-host.ctd-on").forEach(function(h){{ h.classList.remove("ctd-on"); }});
            if(obs){{ try{{ obs.disconnect(); }}catch(e){{}} obs = null; }}
            cur = null;
          }}
          document.addEventListener("click", function(ev){{
            var host = ev.target && ev.target.closest && ev.target.closest(".card-host");
            if(host){{ show(host); return; }}
            if(dock.style.display === "block" && !dock.contains(ev.target)) hide();
          }}, true);
          document.addEventListener("keydown", function(ev){{
            if(!cur) return;
            var t = ev.target;
            if(t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA")) return;
            if(ev.key === "Delete" || ev.key === "Backspace"){{
              ev.preventDefault();
              if(confirm("Bu kart silinsin mi?")){{
                post({{ cardId: cur.getAttribute("data-card-id") || cur.id, delete:true }}, true);
              }}
            }}
            if(ev.key === "[" || ev.key === "-"){{
              ev.preventDefault();
              nudgeDur(-0.5);
            }}
            if(ev.key === "]" || ev.key === "=" || ev.key === "+"){{
              ev.preventDefault();
              nudgeDur(0.5);
            }}
          }});
          function nudgeDur(delta){{
            if(!cur) return;
            var el = document.getElementById("ctd-dur");
            var v = Math.max(0.2, (parseFloat(el.value)||4) + delta);
            el.value = v.toFixed(2);
            cur.setAttribute("data-duration", v.toFixed(2));
            // Kısa bekleyip otomatik kaydet + yenile
            if(saveTimer) clearTimeout(saveTimer);
            saveTimer = setTimeout(function(){{ saveNow(true); }}, 450);
          }}
          document.getElementById("ctd-x").onclick = hide;
          document.getElementById("ctd-m05").onclick = function(){{ nudgeDur(-0.5); }};
          document.getElementById("ctd-p05").onclick = function(){{ nudgeDur(0.5); }};
          async function post(body, doReload){{
            var msg = document.getElementById("ctd-msg");
            msg.textContent = "kaydediliyor…";
            try{{
              var r = await fetch("http://127.0.0.1:8765/api/card-timing", {{
                method:"POST", headers:{{"Content-Type":"application/json"}},
                body: JSON.stringify(Object.assign({{id: VID, rebuild:false}}, body))
              }});
              var j = await r.json();
              if(r.ok && body.delete && cur){{
                cur.style.display = "none";
                hide();
                msg.textContent = "kart silindi";
                if(doReload) setTimeout(function(){{ location.reload(); }}, 250);
                return;
              }}
              msg.textContent = r.ok ? "kaydedildi — akış yenileniyor…" : (j.error || "hata");
              if(r.ok && doReload) setTimeout(function(){{ location.reload(); }}, 280);
            }}catch(e){{
              msg.textContent = "Panel kapalı. Komut: py -3.12 scripts/dashboard_server.py";
            }}
          }}
          function saveNow(doReload){{
            if(!cur) return;
            readIntoInputs(cur);
            var st = document.getElementById("ctd-start").value;
            var du = document.getElementById("ctd-dur").value;
            cur.setAttribute("data-start", st);
            cur.setAttribute("data-duration", du);
            post({{
              cardId: cur.getAttribute("data-card-id") || cur.id,
              start: st,
              duration: du
            }}, doReload !== false);
          }}
          document.getElementById("ctd-save").onclick = function(){{ saveNow(true); }};
          document.getElementById("ctd-sync").onclick = async function(){{
            var msg = document.getElementById("ctd-msg");
            msg.textContent = "şeritten alınıyor…";
            try{{
              var r = await fetch("http://127.0.0.1:8765/api/sync-studio-cards", {{
                method:"POST", headers:{{"Content-Type":"application/json"}},
                body: JSON.stringify({{id: VID, rebuild:false}})
              }});
              var j = await r.json();
              msg.textContent = r.ok ? "şeritten alındı — yenileniyor…" : (j.error || "hata");
              if(r.ok) setTimeout(function(){{ location.reload(); }}, 280);
            }}catch(e){{
              msg.textContent = "Panel kapalı.";
            }}
          }};
          document.getElementById("ctd-del").onclick = function(){{
            if(!cur) return;
            if(!confirm("Bu kart silinsin mi?")) return;
            post({{ cardId: cur.getAttribute("data-card-id") || cur.id, delete:true }}, true);
          }};
        }})();
'''

vars_json = json.dumps([
    {"id": "capSize", "type": "number", "label": "Altyazı punto", "default": int(cap["fontSize"]), "min": 56, "max": 110, "step": 1},
    {"id": "capX", "type": "number", "label": "Altyazı yatay", "default": int(cap["x"]), "min": 0, "max": 200, "step": 2},
    {"id": "capY", "type": "number", "label": "Altyazı dikey", "default": int(cap["y"]), "min": 900, "max": 1550, "step": 4},
    {"id": "capScale", "type": "number", "label": "Altyazı büyüklük", "default": float(cap.get("scale") or 1), "min": 0.7, "max": 1.35, "step": 0.02},
], ensure_ascii=False)

n_cards = len(re.findall(r'class="card-host', cards_html))

html_doc = f'''<!doctype html>
<html lang="tr" data-resolution="portrait" data-composition-variables='{vars_json}'>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <title>{ROOT.name}</title>
    <style>
{css}
    </style>
  </head>
  <body>
    <div id="stage" data-composition-id="talking-head-recut" data-start="0" data-duration="{DUR}" data-fps="{FPS}" data-width="1080" data-height="1920">
      <div id="broll-layer">
{broll_html}
      </div>
      <div class="video-wrapper" id="video-wrap">
        <div id="video-cam">
          <video id="bg-video" src="input-video.mp4" playsinline data-has-audio="true" data-start="0" data-duration="{DUR}" data-track-index="1"></video>
        </div>
      </div>
      <div class="legibility"></div>
      <div id="overlays">
{cards_html}
{pro_cards_html()}
{ig_html}
{mg_html_bits()}
{tip_html}
{caption_items()}
      </div>
{sfx_html}
      <script src="vendor/gsap.min.js"></script>
      <script>
{js}
      </script>
    </div>
  </body>
</html>
'''

public = ROOT / "public" / "index.html"
public.parent.mkdir(parents=True, exist_ok=True)
public.write_text(html_doc, encoding="utf-8")
root_html = (
    html_doc.replace('src="input-video.mp4"', 'src="public/input-video.mp4"')
    .replace('src="vendor/gsap.min.js"', 'src="public/vendor/gsap.min.js"')
    .replace('src="broll/', 'src="public/broll/')
    .replace('src="sfx/', 'src="public/sfx/')
    .replace('src="follow_banner.', 'src="public/follow_banner.')
    .replace("url('fonts/", "url('public/fonts/")
    .replace('data-composition-src="../compositions/', 'data-composition-src="compositions/')
)
(ROOT / "index.html").write_text(root_html, encoding="utf-8")
print(
    "yazildi",
    ROOT.name,
    "kart",
    n_cards,
    "pro",
    len(PRO_CARDS),
    "broll",
    [b["id"] for b in BROLL],
    "ig",
    [ig["start"] for ig in IG_BANNER],
    "altyazi",
    len(captions),
    "special",
    (SPECIAL.get("type") if SPECIAL else None),
    "mg",
    len(MG),
    "tip",
    len(TIP_SCENES),
)
