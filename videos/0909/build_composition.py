# -*- coding: utf-8 -*-
"""Reusable 9:16 talking-head: captions, IG banner, b-roll PIP, punches, SFX.

Per video: cards.html, public/broll, timeline.json, project.json
Look: shared/composition.css + sfx + fonts + banner
"""
import json
import re
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
_SCRIPTS = ROOT.parent / "scripts"
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
cap = layout.get("caption") or {"x": 20, "y": 1208, "w": 1060, "h": 320, "fontSize": 62}

BROLL = list(timeline.get("broll") or [])
for _b in BROLL:
    _b["dur"] = 8.0  # locked — always 8s from start sentence
PUNCHES = [tuple(p) for p in (timeline.get("punches") or [])]
IG_BANNER = list(timeline.get("igBanner") or [])
if not IG_BANNER and DUR > 30:
    IG_BANNER = [
        {"id": "a", "start": 24.0, "dur": 2.3},
        {"id": "b", "start": round(max(26.5, DUR - 11.0), 1), "dur": 2.3},
    ]
CARD_SFX = [tuple(x) for x in (timeline.get("cardSfx") or [])]
MG = list(timeline.get("mg") or [])


def shared_dir():
    for cand in (ROOT.parent / "shared", ROOT.parents[1] / "shared"):
        if cand.exists():
            return cand
    raise SystemExit("shared/ yok")


def q(t):
    return f"{round(float(t) * FPS) / FPS:.4f}"


def mg_html_bits():
    """Motion-graphics overlays from timeline.json mg[] — not cards."""
    bits = []
    for i, m in enumerate(MG):
        mid = re.sub(r"[^a-zA-Z0-9_-]", "", str(m.get("id") or f"m{i}")) or f"m{i}"
        typ = (m.get("type") or "stroke").lower()
        at = float(m.get("at") or 0)
        dur = float(m.get("dur") or 1.2)
        text = (m.get("text") or "").strip()
        y = int(m.get("y") or (520 if typ == "sparkline" else 640 if typ == "ticker" else 480))
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


def cap_line_scale(longest_chars):
    """Shrink long caption lines so Anton 3D stays inside safe margins."""
    if longest_chars >= 26:
        return 0.62
    if longest_chars >= 22:
        return 0.70
    if longest_chars >= 18:
        return 0.78
    if longest_chars >= 15:
        return 0.88
    return 1.0


def fit_caption_line(text, soft_max=15):
    """Split long caption into up to 2 lines + return scale for that block."""
    text = " ".join((text or "").split())
    if not text:
        return "", 1.0
    words = text.split()
    if len(text) <= soft_max and len(words) <= 3:
        return wrap_cap_keywords(text), cap_line_scale(len(text))
    if len(words) == 1:
        return wrap_cap_keywords(text), cap_line_scale(len(text))
    # Prefer ~equal two lines by character count
    best_i, best_score = 1, None
    for i in range(1, len(words)):
        a = " ".join(words[:i])
        b = " ".join(words[i:])
        score = abs(len(a) - len(b))
        if len(a) > soft_max + 6:
            score += (len(a) - soft_max) * 2
        if len(b) > soft_max + 6:
            score += (len(b) - soft_max) * 2
        if best_score is None or score < best_score:
            best_score, best_i = score, i
    a = " ".join(words[:best_i])
    b = " ".join(words[best_i:])
    html = wrap_cap_keywords(a) + "<br>" + wrap_cap_keywords(b)
    return html, cap_line_scale(max(len(a), len(b)))


def caption_items():
    parts = []
    for i, c in enumerate(captions):
        start = float(c["start"])
        end = min(float(c["end"]), DUR)
        tone = "fixed" if ACCOUNT == "mehmet" else (c.get("tone") or "yumusak")
        top = caption_display((c.get("top") or "").strip())
        bot = caption_display((c.get("bottom") or c.get("text") or "").strip())
        top_html, top_scale = fit_caption_line(top)
        bot_html, bot_scale = fit_caption_line(bot)
        cid = f"cap-{i:03d}"
        top_style = f' style="--lineScale:{top_scale:.2f}"' if top_html else ""
        bot_style = f' style="--lineScale:{bot_scale:.2f}"'
        parts.append(
            f'''        <div class="cap-item tone-{tone}" id="{cid}" data-cap-start="{q(start)}" data-cap-end="{q(end)}">
          <div class="cap-top" id="{cid}-top"{top_style}>{top_html}</div>
          <div class="cap-bot" id="{cid}-bot"{bot_style}>{bot_html}</div>
        </div>'''
        )
    return "\n".join(parts)


def caption_js():
    # Shell fade + keyword pop on .cap-kw only (keeps Studio editable hosts unlocked).
    return '''          document.querySelectorAll(".cap-item").forEach(function(el){
            var s = parseFloat(el.getAttribute("data-cap-start"));
            var e = parseFloat(el.getAttribute("data-cap-end"));
            tl.set(el, {autoAlpha:1}, s);
            var kws = el.querySelectorAll(".cap-kw");
            kws.forEach(function(kw, i){
              tl.fromTo(kw,{scale:1,filter:"brightness(1)"},{scale:1.14,filter:"brightness(1.25)",duration:0.22,yoyo:true,repeat:1,ease:"power2.out",immediateRender:false}, s+0.06+i*0.05);
            });
            tl.set(el, {autoAlpha:0}, e);
          });
'''


def strip_hf(html):
    html = re.sub(r'\s*data-hf-id="[^"]*"', "", html)
    html = re.sub(r'\s*data-media-start="[^"]*"', "", html)
    return html


def sync_cards_from_index():
    """Copy Studio timing/position (and richer inner HTML) from index → cards.html."""
    idx_path = ROOT / "index.html"
    cards_path = ROOT / "cards.html"
    if not idx_path.exists() or not cards_path.exists():
        return False
    idx = idx_path.read_text(encoding="utf-8")
    cards = cards_path.read_text(encoding="utf-8")
    changed = False

    def host_open(html, cid):
        m = re.search(rf'<div[^>]*id="{re.escape(cid)}"[^>]*>', html)
        return m

    def host_inner(html, cid):
        m = re.search(
            rf'(<div[^>]*id="{re.escape(cid)}"[^>]*>)(.*?)(?=<div[^>]*\bid="card-[^"]+-host"|<img[^>]*\bid="ig-ban|<div[^>]*\bid="caption-host")',
            html,
            re.S,
        )
        if not m:
            return None, None
        opens = len(re.findall(r"<div\b", m.group(0), re.I))
        closes = len(re.findall(r"</div>", m.group(0), re.I))
        body = m.group(0)
        if opens > closes:
            body = body + ("</div>" * (opens - closes))
        # split open tag / rest
        om = re.match(r"(<div[^>]*>)(.*)$", body, re.S)
        if not om:
            return None, None
        return om.group(1), om.group(2)

    ids = re.findall(r'id="(card-[^"]+-host)"', cards)
    for cid in ids:
        i_open = host_open(idx, cid)
        c_open = host_open(cards, cid)
        if not i_open or not c_open:
            continue
        i_tag = strip_hf(i_open.group(0))
        # pull attrs from index
        def get(tag, name):
            m = re.search(rf'{name}="([^"]*)"', tag)
            return m.group(1) if m else None

        # Timing/position only — never overwrite card inner markup from Studio.
        for attr in ("data-start", "data-duration", "style"):
            iv, cv = get(i_tag, attr), get(c_open.group(0), attr)
            if iv is not None and iv != cv:
                if cv is None:
                    cards = cards.replace(
                        c_open.group(0),
                        c_open.group(0)[:-1] + f' {attr}="{iv}">',
                        1,
                    )
                else:
                    cards = cards.replace(
                        c_open.group(0),
                        re.sub(rf'{attr}="[^"]*"', f'{attr}="{iv}"', c_open.group(0), count=1),
                        1,
                    )
                c_open = host_open(cards, cid)
                changed = True

    if changed:
        cards_path.write_text(cards, encoding="utf-8")
    return changed


sync_cards_from_index()

def sfx_el(sid, src, start, dur, vol, track):
    return (
        f'      <audio id="{sid}" src="{src}" data-start="{q(start)}" '
        f'data-duration="{q(dur)}" data-track-index="{track}" data-volume="{vol}"></audio>'
    )


cards_html = ""
if (ROOT / "cards.html").exists():
    cards_html = (ROOT / "cards.html").read_text(encoding="utf-8").rstrip()

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

ig_html = "\n".join(
    f'''      <img id="ig-ban-{ig["id"]}" class="clip ig-banner" src="follow_banner.png" data-start="{q(ig["start"])}" data-duration="{q(ig["dur"])}" data-track-index="8" style="left:0;top:36px;width:1080px;height:310px;" alt="banner"/>'''
    for ig in IG_BANNER
)

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
    if kind == "hook":
        sfx_bits.append(sfx_el(f"sfx-card-{name}", "sfx/pop.mp3", t, 0.42, "0.20", 16))
        sfx_bits.append(sfx_el(f"sfx-card-click-{name}", "sfx/sub-hit.mp3", t, 0.28, "0.10", 17))
    elif kind == "punch":
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

# One special moment per video — timeline.json "special": {"type":"drone","at":86.0,"dur":1.4}
SPECIAL = timeline.get("special") or {}
if (SPECIAL.get("type") or "").lower() == "drone" and SPECIAL.get("at") is not None:
    st = float(SPECIAL["at"])
    sfx_bits.append(sfx_el("sfx-drone-whoosh", "sfx/whoosh-long.mp3", st, 0.45, "0.14", 26))
    sfx_bits.append(sfx_el("sfx-drone-tick", "sfx/tick.mp3", st + 0.08, 0.14, "0.08", 26))

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
          tl.fromTo("{cam}",{{opacity:0,x:140,scale:1.14}},{{opacity:1,x:0,scale:1,duration:0.36,ease:"power3.out",immediateRender:false}}, {s});
          tl.to("{cam}",{{opacity:0,x:-100,scale:1.06,duration:0.3,ease:"power2.in"}}, {e - 0.3:.2f});
          tl.fromTo("#video-wrap",{{scale:1,x:0,y:0,borderRadius:"0px",rotation:0}},{{scale:0.30,x:-350,y:-20,borderRadius:"36px",rotation:-1.5,duration:0.36,ease:"power3.inOut",immediateRender:false}}, {s});
          tl.to("#video-wrap",{{rotation:0,duration:0.2,ease:"power1.out"}}, {s + 0.36:.2f});
          tl.to("#video-wrap",{{scale:1,x:0,y:0,borderRadius:"0px",rotation:0,duration:0.36,ease:"power3.inOut"}}, {e - 0.36:.2f});
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
if (SPECIAL.get("type") or "").lower() == "drone" and SPECIAL.get("at") is not None:
    st = float(SPECIAL["at"])
    sd = float(SPECIAL.get("dur") or 1.5)
    card = (SPECIAL.get("card") or "").strip()
    # Prefer named card fx; else first card-host overlapping `at`
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
            /* Visible "drone" on card: pull back in Z / scale, then return */
            tl.to(sel,{{scale:0.68,y:-90,rotateX:18,rotateY:-22,z:-120,duration:up,ease:"power2.inOut"}}, st);
            tl.to(sel,{{scale:1,y:0,rotateX:0,rotateY:0,z:0,duration:down,ease:"power3.out"}}, st+up);
          }})();
'''

js = f'''
        (function(){{
          const tl = window.gsap.timeline({{paused:true}});
          const cam = "#video-cam";
          function punchHold(t, hold, scale){{
            var sc = scale || 1.12;
            tl.set(cam, {{scale:sc, immediateRender:false}}, t);
            tl.to(cam, {{scale:1, duration:0.48, ease:"power2.inOut"}}, t+hold);
          }}
          function enterMode(host){{
            var forced = host.getAttribute("data-enter");
            if(forced) return forced;
            var root = host.querySelector(".root");
            if(!root) return "pop";
            if(root.classList.contains("hook")) return "slam";
            if(root.classList.contains("punch") || root.querySelector(".warn-badge")) return "glitch";
            if(root.classList.contains("slim")) return "soft";
            if(root.classList.contains("levels") || root.classList.contains("graph-card")) return "tilt";
            if(root.classList.contains("stats")) return "wipe";
            return "pop";
          }}
          var ENTER_POOL = ["slam","soft","glitch","tilt","wipe","pop","rise","flip","snap","drift","zoom","fold"];
          var enterUsed = {{}};
          function uniqueEnter(host, idx){{
            var forced = host.getAttribute("data-enter");
            if(forced && !enterUsed[forced]){{
              enterUsed[forced] = 1;
              return forced;
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
            if(forced) return forced;
            var mode = host.getAttribute("data-enter") || enterMode(host);
            if(mode === "soft" || mode === "wipe" || mode === "drift") return "fade";
            if(mode === "glitch" || mode === "slam" || mode === "snap" || mode === "zoom") return "scale";
            if(mode === "tilt" || mode === "flip" || mode === "fold") return "slide";
            return "fade";
          }}
          function exitCard(fxSel, host, tEnd){{
            var mode = exitMode(host);
            var t = tEnd - 0.34;
            if(t < (parseFloat(host.getAttribute("data-start")) || 0) + 0.5) return;
            if(mode === "scale"){{
              tl.to(fxSel,{{opacity:0,scale:0.88,y:-16,duration:0.32,ease:"power2.in"}}, t);
            }} else if(mode === "slide"){{
              tl.to(fxSel,{{opacity:0,x:48,rotateY:8,duration:0.34,ease:"power2.in"}}, t);
            }} else {{
              tl.to(fxSel,{{opacity:0,y:-8,duration:0.3,ease:"power1.in"}}, t);
            }}
          }}
          function progressCard(fxSel, t, dur, mode){{
            if(dur < 2.2) return;
            var mid = t + Math.min(dur * 0.4, 2.8);
            if(mode === "tilt" || mode === "flip" || mode === "fold"){{
              tl.to(fxSel,{{rotateY:7,duration:Math.min(dur*0.35,2.2),ease:"sine.inOut",yoyo:true,repeat:1}}, mid);
            }} else if(mode === "drift" || mode === "soft" || mode === "rise"){{
              tl.to(fxSel,{{y:-12,duration:Math.min(dur*0.4,2.4),ease:"sine.inOut",yoyo:true,repeat:1}}, t+0.55);
            }} else if(mode === "wipe" || mode === "zoom" || mode === "pop"){{
              tl.to(fxSel,{{scale:1.035,duration:0.85,ease:"sine.inOut",yoyo:true,repeat:1}}, mid);
            }} else if(mode === "slam" || mode === "snap" || mode === "glitch"){{
              tl.to(fxSel,{{x:6,duration:0.35,ease:"sine.inOut",yoyo:true,repeat:1}}, mid);
            }}
          }}
          /* Motion on .card-fx / accents only — never .card-host (Studio left/top). */
          function popCard(fxSel, t, mode){{
            var from, to;
            if(mode === "slam"){{
              from = {{opacity:0,y:48,scale:1.22,rotateX:0,rotateZ:0}};
              to = {{opacity:1,y:0,scale:1,rotateX:0,rotateZ:0,duration:0.4,ease:"back.out(2.1)",immediateRender:false}};
            }} else if(mode === "soft"){{
              from = {{opacity:0,y:14,scale:0.98,rotateX:4,rotateZ:0}};
              to = {{opacity:1,y:0,scale:1,rotateX:0,rotateZ:0,duration:0.5,ease:"power2.out",immediateRender:false}};
            }} else if(mode === "glitch"){{
              from = {{opacity:0,y:10,scale:0.94,rotateX:6,rotateZ:-2,x:-16}};
              to = {{opacity:1,y:0,scale:1,rotateX:0,rotateZ:0,x:0,duration:0.42,ease:"power3.out",immediateRender:false}};
            }} else if(mode === "tilt"){{
              from = {{opacity:0,y:20,scale:0.92,rotateY:-18,rotateX:6}};
              to = {{opacity:1,y:0,scale:1,rotateY:0,rotateX:0,duration:0.55,ease:"power3.out",immediateRender:false}};
            }} else if(mode === "wipe"){{
              from = {{opacity:0,y:0,scale:1,rotateX:0,clipPath:"inset(0 0 100% 0)"}};
              to = {{opacity:1,y:0,scale:1,rotateX:0,clipPath:"inset(0 0 0% 0)",duration:0.48,ease:"power2.inOut",immediateRender:false}};
            }} else if(mode === "rise"){{
              from = {{opacity:0,y:60,scale:0.9,rotateX:12}};
              to = {{opacity:1,y:0,scale:1,rotateX:0,duration:0.55,ease:"power3.out",immediateRender:false}};
            }} else if(mode === "flip"){{
              from = {{opacity:0,rotateY:85,scale:0.88}};
              to = {{opacity:1,rotateY:0,scale:1,duration:0.58,ease:"power3.out",immediateRender:false}};
            }} else if(mode === "snap"){{
              from = {{opacity:0,scale:1.35,y:-8}};
              to = {{opacity:1,scale:1,y:0,duration:0.32,ease:"back.out(2.4)",immediateRender:false}};
            }} else if(mode === "drift"){{
              from = {{opacity:0,x:-40,y:10,rotateZ:-3}};
              to = {{opacity:1,x:0,y:0,rotateZ:0,duration:0.6,ease:"power2.out",immediateRender:false}};
            }} else if(mode === "zoom"){{
              from = {{opacity:0,scale:0.55,rotateX:8}};
              to = {{opacity:1,scale:1,rotateX:0,duration:0.5,ease:"power4.out",immediateRender:false}};
            }} else if(mode === "fold"){{
              from = {{opacity:0,rotateX:70,y:-24}};
              to = {{opacity:1,rotateX:0,y:0,duration:0.52,ease:"power3.out",immediateRender:false}};
            }} else {{
              from = {{opacity:0,y:36,scale:0.88,rotateX:10,rotateZ:-1.2}};
              to = {{opacity:1,y:0,scale:1,rotateX:0,rotateZ:0,duration:0.52,ease:"power3.out",immediateRender:false}};
            }}
            tl.fromTo(fxSel, from, to, t);
            var host = document.querySelector(fxSel);
            if(!host) return;
            var accent = host.querySelector(".card-accent");
            var sheen = host.querySelector(".card-sheen");
            var warn = host.querySelector(".warn-badge");
            var ring = host.querySelector(".warn-ring");
            var chapter = host.querySelector(".chapter");
            var quote = host.querySelector(".quote-mark");
            if(accent){{
              tl.fromTo(accent,{{scaleY:0}},{{scaleY:1,duration:0.55,ease:"power3.out",immediateRender:false}}, t+0.04);
            }}
            if(sheen){{
              tl.fromTo(sheen,{{x:-520,opacity:0}},{{x:900,opacity:1,duration:0.6,ease:"power2.out",immediateRender:false}}, t+0.08);
              tl.to(sheen,{{opacity:0,duration:0.22,ease:"power1.in"}}, t+0.62);
            }}
            if(warn){{
              tl.fromTo(warn,{{opacity:0,scale:0.45,rotation:-40}},{{opacity:1,scale:1,rotation:0,duration:0.48,ease:"back.out(2)",immediateRender:false}}, t+0.1);
              tl.to(warn,{{scale:1.08,duration:0.18,yoyo:true,repeat:1,ease:"power1.inOut"}}, t+0.55);
            }}
            if(ring){{
              var end = t + (parseFloat(host.closest(".card-host").getAttribute("data-duration")) || 4);
              tl.fromTo(ring,{{rotation:0}},{{rotation:720,duration:Math.max(3, end-t),ease:"none",immediateRender:false}}, t+0.18);
            }}
            if(chapter){{
              tl.fromTo(chapter,{{opacity:0,x:-18}},{{opacity:1,x:0,duration:0.36,ease:"power3.out",immediateRender:false}}, t+0.06);
            }}
            if(quote){{
              tl.fromTo(quote,{{opacity:0,scale:0.6}},{{opacity:1,scale:1,duration:0.4,ease:"back.out(1.8)",immediateRender:false}}, t+0.08);
            }}
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
            if(kind === "back"){{
              tl.fromTo(el,{{opacity:0,scale:0.82,y:22,rotateZ:-2}},{{opacity:1,scale:1,y:0,rotateZ:0,duration:0.5,ease:"back.out(1.8)",immediateRender:false}}, t);
            }} else if(kind === "drop"){{
              tl.fromTo(el,{{opacity:0,y:-18,scale:0.96}},{{opacity:1,y:0,scale:1,duration:0.34,ease:"power3.out",immediateRender:false}}, t);
            }} else if(kind === "spin"){{
              tl.fromTo(el,{{opacity:0,scale:0.7,rotation:-18,y:10}},{{opacity:1,scale:1,rotation:0,y:0,duration:0.4,ease:"back.out(1.9)",immediateRender:false}}, t);
            }} else if(kind === "slam"){{
              tl.fromTo(el,{{opacity:0,scale:1.28,y:28}},{{opacity:1,scale:1,y:0,duration:0.36,ease:"back.out(2.2)",immediateRender:false}}, t);
            }} else {{
              tl.fromTo(el,{{opacity:0,y:18,scale:0.96}},{{opacity:1,y:0,scale:1,duration:0.36,ease:"power3.out",immediateRender:false}}, t);
            }}
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
          punches.forEach(function(p){{
            var t = p[0];
            document.querySelectorAll(".cap-item").forEach(function(el){{
              var s = parseFloat(el.getAttribute("data-cap-start"));
              var e = parseFloat(el.getAttribute("data-cap-end"));
              if(!(s <= t && e >= t)) return;
              var bot = el.querySelector(".cap-bot");
              if(!bot) return;
              tl.fromTo(bot,{{scale:1}},{{scale:1.06,duration:0.28,yoyo:true,repeat:1,ease:"power1.inOut",immediateRender:false}}, t);
            }});
          }});
          window.__timelines["talking-head-recut"] = tl;
        }})();
'''

vars_json = json.dumps([
    {"id": "capSize", "type": "number", "label": "Altyazı punto", "default": 58, "min": 40, "max": 78, "step": 2},
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
{ig_html}
{mg_html_bits()}
      <div class="clip cap-stage" id="caption-host" data-start="0" data-duration="{DUR}" data-track-index="5" style="left:{int(cap['x'])}px;top:{int(cap['y'])}px;width:{int(cap['w'])}px;height:{int(cap['h'])}px;">
{caption_items()}
      </div>
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
)
(ROOT / "index.html").write_text(root_html, encoding="utf-8")
print(
    "yazildi",
    ROOT.name,
    "kart",
    n_cards,
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
)
