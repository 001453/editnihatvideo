# -*- coding: utf-8 -*-
"""Patch build_composition.py animation block + 0910 unique enters."""
from pathlib import Path
import re

builder = Path(r"D:\nihat_pipeline\nihat_pipeline\template\build_composition.py")
text = builder.read_text(encoding="utf-8")

old_start = "          function enterMode(host){{"
old_end = "            tl.to(fxSel,{{scale:1.012,duration:0.7,yoyo:true,repeat:1,ease:\"sine.inOut\"}}, t+0.7);\n          }}"

# Find using single-brace version as in source file (f-string doubles)
src = builder.read_text(encoding="utf-8")
# In the file, braces are doubled for f-string. Match from enterMode to end of popCard.
pat = re.compile(
    r"          function enterMode\(host\)\{\{.*?"
    r"tl\.to\(fxSel,\{\{scale:1\.012,duration:0\.7,yoyo:true,repeat:1,ease:\"sine\.inOut\"\}\}, t\+0\.7\);\n"
    r"          \}\}",
    re.S,
)
new_block = r'''          function enterMode(host){{
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
          }}'''

m = pat.search(src)
if not m:
    raise SystemExit("animation block not found")
src2 = src[: m.start()] + new_block + src[m.end() :]

# Update card-host forEach to use uniqueEnter + progressCard
old_fe = '''          document.querySelectorAll(".card-host").forEach(function(host){{
            var t = parseFloat(host.getAttribute("data-start")) || 0;
            var dur = parseFloat(host.getAttribute("data-duration")) || 4;
            var fx = host.querySelector(".card-fx");
            if(fx && fx.id){{
              popCard("#"+fx.id, t, enterMode(host));
              exitCard("#"+fx.id, host, t + dur);
            }} else {{'''

new_fe = '''          var cardIdx = 0;
          document.querySelectorAll(".card-host").forEach(function(host){{
            var t = parseFloat(host.getAttribute("data-start")) || 0;
            var dur = parseFloat(host.getAttribute("data-duration")) || 4;
            var fx = host.querySelector(".card-fx");
            if(fx && fx.id){{
              var mode = uniqueEnter(host, cardIdx++);
              popCard("#"+fx.id, t, mode);
              progressCard("#"+fx.id, t, dur, mode);
              exitCard("#"+fx.id, host, t + dur);
            }} else {{'''

if old_fe not in src2:
    raise SystemExit("forEach block not found")
src2 = src2.replace(old_fe, new_fe, 1)
builder.write_text(src2, encoding="utf-8")
print("builder patched")

# Unique enters on 0910 cards
cards = Path(r"D:\nihat_pipeline\nihat_pipeline\videos\0910\cards.html")
ct = cards.read_text(encoding="utf-8")
pool = ["slam", "soft", "glitch", "tilt", "wipe", "pop", "rise", "flip", "snap", "drift", "zoom", "fold"]
hosts = list(re.finditer(r'(id="card-[^"]+-host"[^>]*data-enter=")([^"]*)(")', ct))
# rewrite each card-host open tag with unique enter/exit
for i, m in enumerate(re.finditer(r'<div class="card-host clip" id="(card-[^"]+-host)"([^>]*)>', ct)):
    cid, attrs = m.group(1), m.group(2)
    mode = pool[i % len(pool)]
    exit_map = {
        "soft": "fade", "wipe": "fade", "drift": "fade", "pop": "fade",
        "glitch": "scale", "slam": "scale", "snap": "scale", "zoom": "scale", "rise": "scale",
        "tilt": "slide", "flip": "slide", "fold": "slide",
    }
    ex = exit_map.get(mode, "fade")
    attrs2 = attrs
    if 'data-enter="' in attrs2:
        attrs2 = re.sub(r'data-enter="[^"]*"', f'data-enter="{mode}"', attrs2, count=1)
    else:
        attrs2 += f' data-enter="{mode}"'
    if 'data-exit="' in attrs2:
        attrs2 = re.sub(r'data-exit="[^"]*"', f'data-exit="{ex}"', attrs2, count=1)
    else:
        attrs2 += f' data-exit="{ex}"'
    if cid == "card-split-host" and 'data-hero="' not in attrs2:
        attrs2 += ' data-hero="1"'
    ct = ct.replace(m.group(0), f'<div class="card-host clip" id="{cid}"{attrs2}>', 1)
cards.write_text(ct, encoding="utf-8")
print("cards unique enters", len(pool))

# CSS chip cleanup
css = Path(r"D:\nihat_pipeline\nihat_pipeline\shared\composition.css")
c = css.read_text(encoding="utf-8")
c = c.replace(
    ".title,.q,.note,.kicker,.lvl b,.stat b,.hero-num,.chip{text-shadow:0 2px 10px rgba(0,0,0,.55);}\n      .chip{background:rgba(255,221,79,.18);}\n",
    ".title,.q,.note,.kicker,.lvl b,.stat b,.hero-num{text-shadow:0 2px 10px rgba(0,0,0,.55);}\n",
)
c = c.replace(
    "background:rgba(255,221,79,.12);",
    "background:rgba(255,221,79,.20);",
)
css.write_text(c, encoding="utf-8")
print("css ok")
