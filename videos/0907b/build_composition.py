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
PUNCHES = [tuple(p) for p in (timeline.get("punches") or [])]
IG_BANNER = list(timeline.get("igBanner") or [])
if not IG_BANNER and DUR > 30:
    IG_BANNER = [
        {"id": "a", "start": 24.0, "dur": 2.3},
        {"id": "b", "start": round(max(26.5, DUR - 11.0), 1), "dur": 2.3},
    ]
CARD_SFX = [tuple(x) for x in (timeline.get("cardSfx") or [])]


def shared_dir():
    for cand in (ROOT.parent / "shared", ROOT.parents[1] / "shared"):
        if cand.exists():
            return cand
    raise SystemExit("shared/ yok")


def q(t):
    return f"{round(float(t) * FPS) / FPS:.4f}"


def caption_items():
    parts = []
    for i, c in enumerate(captions):
        start = float(c["start"])
        end = min(float(c["end"]), DUR)
        tone = "fixed" if ACCOUNT == "mehmet" else (c.get("tone") or "yumusak")
        top = (c.get("top") or "").strip()
        bot = (c.get("bottom") or c.get("text") or "").strip()
        cid = f"cap-{i:03d}"
        parts.append(
            f'''        <div class="cap-item tone-{tone}" id="{cid}" data-cap-start="{q(start)}" data-cap-end="{q(end)}">
          <div class="cap-top" id="{cid}-top">{escape(top)}</div>
          <div class="cap-bot" id="{cid}-bot">{escape(bot)}</div>
        </div>'''
        )
    return "\n".join(parts)


def caption_js():
    # Only fade the .cap-item shell — do not tween .cap-top/.cap-bot transforms
    # so Studio text edits on caption lines stay unlocked.
    return '''          document.querySelectorAll(".cap-item").forEach(function(el){
            var s = parseFloat(el.getAttribute("data-cap-start"));
            var e = parseFloat(el.getAttribute("data-cap-end"));
            tl.set(el, {autoAlpha:1}, s);
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

sfx_bits = []
for b in BROLL:
    sfx_bits.append(sfx_el(f"sfx-whoosh-{b['id']}", "sfx/whoosh-short.mp3", b["start"], 0.37, "0.16", 13))
for i, (t, hold) in enumerate(PUNCHES):
    sfx_bits.append(sfx_el(f"sfx-cam-in-{i}", "sfx/click-soft.mp3", t, 0.37, "0.14", 14))
    sfx_bits.append(sfx_el(f"sfx-cam-out-{i}", "sfx/click-soft.mp3", t + hold, 0.37, "0.10", 15))
for name, t in CARD_SFX:
    sfx_bits.append(sfx_el(f"sfx-card-{name}", "sfx/pop.mp3", t, 0.42, "0.18", 16))
    sfx_bits.append(sfx_el(f"sfx-card-click-{name}", "sfx/click-soft.mp3", t, 0.30, "0.13", 17))
for i, m in enumerate(re.finditer(r'\bdata-at="([0-9.]+)"', cards_html)):
    sfx_bits.append(
        sfx_el(f"sfx-line-{i}", "sfx/click-soft.mp3", float(m.group(1)), 0.22, "0.09", 18)
    )
sfx_html = "\n".join(sfx_bits)

css = (shared_dir() / "composition.css").read_text(encoding="utf-8")

broll_js = []
for b in BROLL:
    s = b["start"]
    e = b["start"] + b["dur"]
    cam = f"#broll-{b['id']}-cam"
    broll_js.append(f'''
          tl.fromTo("{cam}",{{opacity:0}},{{opacity:1,duration:0.4,ease:"power1.out",immediateRender:false}}, {s});
          tl.to("{cam}",{{opacity:0,duration:0.35,ease:"power1.in"}}, {e - 0.35:.2f});
          tl.fromTo("#video-wrap",{{scale:1,x:0,y:0}},{{scale:0.30,x:350,y:-20,duration:0.45,ease:"power2.inOut",immediateRender:false}}, {s});
          tl.to("#video-wrap",{{scale:1,x:0,y:0,duration:0.45,ease:"power2.inOut"}}, {e - 0.45:.2f});
''')
broll_js_txt = "".join(broll_js)

punch_js = "\n".join(
    f'          punchHold({t}, {hold});' for t, hold in PUNCHES
)

js = f'''
        (function(){{
          const tl = window.gsap.timeline({{paused:true}});
          const cam = "#video-cam";
          function punchHold(t, hold){{
            tl.set(cam, {{scale:1.12, immediateRender:false}}, t);
            tl.to(cam, {{scale:1, duration:0.48, ease:"power2.inOut"}}, t+hold);
          }}
          /* Motion on .card-fx / accents only — never .card-host (Studio left/top). */
          function popCard(fxSel, t){{
            tl.fromTo(fxSel,{{opacity:0,y:32,scale:0.90,rotateX:8}},{{opacity:1,y:0,scale:1,rotateX:0,duration:0.48,ease:"power3.out",immediateRender:false}}, t);
            var host = document.querySelector(fxSel);
            if(!host) return;
            var accent = host.querySelector(".card-accent");
            var sheen = host.querySelector(".card-sheen");
            var warn = host.querySelector(".warn-badge");
            var ring = host.querySelector(".warn-ring");
            if(accent){{
              tl.fromTo(accent,{{scaleY:0}},{{scaleY:1,duration:0.5,ease:"power3.out",immediateRender:false}}, t+0.04);
            }}
            if(sheen){{
              tl.fromTo(sheen,{{x:-480,opacity:0}},{{x:860,opacity:1,duration:0.55,ease:"power2.out",immediateRender:false}}, t+0.08);
              tl.to(sheen,{{opacity:0,duration:0.2,ease:"power1.in"}}, t+0.58);
            }}
            if(warn){{
              tl.fromTo(warn,{{opacity:0,scale:0.6,rotation:-25}},{{opacity:1,scale:1,rotation:0,duration:0.42,ease:"back.out(1.7)",immediateRender:false}}, t+0.12);
            }}
            if(ring){{
              var end = t + (parseFloat(host.closest(".card-host").getAttribute("data-duration")) || 4);
              tl.fromTo(ring,{{rotation:0}},{{rotation:360,duration:Math.max(2.5, end-t),ease:"none",immediateRender:false}}, t+0.2);
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
          document.querySelectorAll(".card-host").forEach(function(host){{
            var t = parseFloat(host.getAttribute("data-start")) || 0;
            var fx = host.querySelector(".card-fx");
            if(fx && fx.id) popCard("#"+fx.id, t);
            else {{
              var ban = host.querySelector(".banner");
              if(ban && ban.id){{
                tl.fromTo("#"+ban.id,{{opacity:0,y:-14,scale:0.96}},{{opacity:1,y:0,scale:1,duration:0.32,ease:"power3.out",immediateRender:false}}, t);
              }}
            }}
          }});
          document.querySelectorAll("[data-at]").forEach(function(el){{
            if(el.classList.contains("banner")) return;
            var t = parseFloat(el.getAttribute("data-at"));
            var kind = el.getAttribute("data-in") || "";
            if(kind === "back"){{
              tl.fromTo(el,{{opacity:0,scale:0.84,y:18}},{{opacity:1,scale:1,y:0,duration:0.45,ease:"back.out(1.6)",immediateRender:false}}, t);
            }} else if(kind === "drop"){{
              tl.fromTo(el,{{opacity:0,y:-14}},{{opacity:1,y:0,duration:0.3,ease:"power3.out",immediateRender:false}}, t);
            }} else {{
              tl.fromTo(el,{{opacity:0,y:16}},{{opacity:1,y:0,duration:0.34,ease:"power3.out",immediateRender:false}}, t);
            }}
          }});
          document.querySelectorAll("[data-out]").forEach(function(el){{
            tl.to(el,{{opacity:0,duration:0.2,ease:"power2.in"}}, parseFloat(el.getAttribute("data-out")));
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
          window.__timelines["talking-head-recut"] = tl;
        }})();
'''

vars_json = json.dumps([
    {"id": "capSize", "type": "number", "label": "Altyazı punto", "default": 66, "min": 48, "max": 86, "step": 2},
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
print("yazildi", ROOT.name, "kart", n_cards, "broll", [b["id"] for b in BROLL], "ig", [ig["start"] for ig in IG_BANNER], "altyazi", len(captions))
