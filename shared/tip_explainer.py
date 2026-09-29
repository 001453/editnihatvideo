# -*- coding: utf-8 -*-
"""Tip-explainer scenes — çeşitlendirilmiş profesyonel overlay'ler.

kinds:
  verdict  — editöryel büyük başlık (sahte sosyal kart YOK)
  stat     — dev sayı panosu
  social   — sadece gerçek marka (@cetin.finans); aksi halde verdict'e düşer
  nodes    — akış düğümleri
  branches — 2–3 senaryo kartı

timeline.json tipScenes[] max 2. Her videoda kind değiştir.
"""
from __future__ import annotations

import html as html_lib
import json
import re


def _esc(s) -> str:
    return html_lib.escape(str(s or ""), quote=True)


def _q(t, fps=30):
    return f"{round(float(t) * fps) / fps:.4f}"


_FAKE_HANDLES = re.compile(
    r"^@(hisse|faiz|gumus|gümüş|altin|altın|tcmb|hfuser|user|test|demo).*$",
    re.I,
)


def _normalize_kind(sc: dict) -> str:
    kind = (sc.get("kind") or "verdict").lower().strip()
    if kind == "social":
        handle = str(sc.get("handle") or "").strip()
        if not handle or _FAKE_HANDLES.match(handle) or handle.lower() in ("@",):
            # Sahte @ → profesyonel varyanta çevir
            if sc.get("stat") and re.search(r"\d", str(sc.get("stat"))):
                return "stat"
            return "verdict"
        if "cetin" not in handle.lower() and "nihat" not in handle.lower():
            # Bilinmeyen handle'ı da verdict yap (marka dışı spam önle)
            if sc.get("stat") and re.search(r"\d", str(sc.get("stat"))):
                return "stat"
            return "verdict"
    if kind in ("quote", "headline", "banner"):
        return "verdict"
    if kind in ("number", "meter", "hero-stat"):
        return "stat"
    return kind if kind in ("verdict", "stat", "social", "nodes", "branches") else "verdict"


def tip_html_bits(scenes: list, fps: int = 30) -> str:
    if not scenes:
        return ""
    scenes = list(scenes)[:2]
    parts = []
    for sc in scenes:
        sid = _esc(sc.get("id") or "tip")
        kind = _normalize_kind(sc)
        start = float(sc["start"])
        dur = float(sc.get("dur") or 3)
        half = bool(sc.get("halfPip", False))
        mode_cls = "tip-half" if half else "tip-fullblur"
        tone = (sc.get("tone") or "").lower()
        tone_cls = f" tip-tone-{tone}" if tone in ("warn", "ok", "gold") else ""

        parts.append(
            f'''      <div class="clip tip-scene tip-{kind} {mode_cls}{tone_cls}" id="tip-{sid}" data-tip="{kind}" data-start="{_q(start, fps)}" data-duration="{_q(dur, fps)}" data-track-index="6" style="left:0;top:0;width:1080px;height:1920px;z-index:4;">
        <div class="tip-scene-bg" aria-hidden="true"></div>
        <div class="tip-grid tip-grid-{kind}" aria-hidden="true"></div>'''
        )
        if half:
            parts.append('        <div class="tip-blur-band" aria-hidden="true"></div>')

        if kind == "verdict":
            kicker = _esc(sc.get("kicker") or sc.get("name") or "")
            title = _esc(sc.get("title") or sc.get("stat") or "")
            body = _esc(sc.get("body") or "")
            note = _esc(sc.get("note") or sc.get("statLabel") or "")
            parts.append(
                f'''        <div class="tip-verdict" id="tip-{sid}-card">
          <div class="tip-verdict-rule" aria-hidden="true"></div>
          <div class="tip-verdict-kicker" id="tip-{sid}-kick">{kicker}</div>
          <div class="tip-verdict-title" id="tip-{sid}-title">{title}</div>
          <p class="tip-verdict-body" id="tip-{sid}-body">{body}</p>
          {f'<div class="tip-verdict-note" id="tip-{sid}-note">{note}</div>' if note else ''}
        </div>'''
            )

        elif kind == "stat":
            kicker = _esc(sc.get("kicker") or sc.get("name") or "")
            stat = _esc(sc.get("stat") or "")
            suffix = _esc(sc.get("suffix") or "")
            label = _esc(sc.get("label") or sc.get("statLabel") or "")
            note = _esc(sc.get("note") or sc.get("body") or "")
            parts.append(
                f'''        <div class="tip-stat" id="tip-{sid}-card">
          <div class="tip-stat-kicker" id="tip-{sid}-kick">{kicker}</div>
          <div class="tip-stat-row" id="tip-{sid}-row">
            <span class="tip-stat-num" id="tip-{sid}-num">{stat}</span>
            {f'<span class="tip-stat-suf">{suffix}</span>' if suffix else ''}
          </div>
          <div class="tip-stat-label" id="tip-{sid}-label">{label}</div>
          {f'<p class="tip-stat-note" id="tip-{sid}-note">{note}</p>' if note else ''}
        </div>'''
            )

        elif kind == "nodes":
            parts.append(f'        <svg class="tip-wires" id="tip-{sid}-wires" viewBox="0 0 1080 1920" preserveAspectRatio="none"></svg>')
            for n in sc.get("nodes") or []:
                nid = _esc(n.get("id") or "n")
                x = int(n.get("x") or 120)
                y = int(n.get("y") or 600)
                title = _esc(n.get("title") or "")
                body = _esc(n.get("body") or "")
                icon = _esc(n.get("icon") or "◆")
                tiles = n.get("tiles") or []
                tile_html = "".join(
                    f'<div class="tip-tile"><b>{_esc(t)}</b></div>' for t in tiles[:4]
                )
                parts.append(
                    f'''        <div class="tip-node" id="tip-{sid}-{nid}" style="left:{x}px;top:{y}px;">
          <div class="tip-node-hd"><span class="tip-ico">{icon}</span><span>{title}</span></div>
          <div class="tip-node-bd">{tile_html or f'<p>{body}</p>'}</div>
          <i class="tip-port tip-port-l"></i><i class="tip-port tip-port-r"></i>
        </div>'''
                )
            if sc.get("cursor", True):
                parts.append(f'        <div class="tip-cursor" id="tip-{sid}-cur"></div>')

        elif kind == "social":
            name = _esc(sc.get("name") or "Nihat Çetinkaya")
            handle = _esc(sc.get("handle") or "@cetin.finans")
            body = _esc(sc.get("body") or "")
            stat = _esc(sc.get("stat") or "")
            stat_label = _esc(sc.get("statLabel") or "")
            parts.append(
                f'''        <div class="tip-social tip-social-pro" id="tip-{sid}-card">
          <div class="tip-social-hd">
            <span class="tip-avatar tip-avatar-brand"></span>
            <div><b>{name}</b><i>{handle}</i></div>
          </div>
          <p class="tip-social-body">{body}</p>
          {f'<div class="tip-social-stat"><strong>{stat}</strong><span>{stat_label}</span></div>' if stat else ''}
        </div>'''
            )

        elif kind == "branches":
            hub = _esc(sc.get("hub") or "MERKEZ")
            title = _esc(sc.get("title") or "Nereye yöneliyor?")
            cards = []
            for i, br in enumerate((sc.get("branches") or [])[:3]):
                name = _esc(br.get("name") or f"A{i+1}")
                note = _esc(br.get("note") or "")
                color = _esc(br.get("color") or "#FACC15")
                cards.append(
                    f'''          <div class="tip-pro-card" id="tip-{sid}-b{i}" style="--accent:{color}">
            <div class="tip-pro-bar"></div>
            <div class="tip-pro-body"><b>{name}</b><span>{note}</span></div>
          </div>'''
                )
            parts.append(
                f'''        <div class="tip-panel" id="tip-{sid}-panel">
          <div class="tip-panel-kicker" id="tip-{sid}-kick">{hub}</div>
          <div class="tip-panel-title" id="tip-{sid}-title">{title}</div>
          <div class="tip-cards-row">
{chr(10).join(cards)}
          </div>
        </div>'''
            )
        parts.append("      </div>")
    return "\n".join(parts)


def tip_js_bits(scenes: list) -> str:
    if not scenes:
        return ""
    scenes = list(scenes)[:2]
    lines = ["          /* Tip-explainer — verdict|stat|social|nodes|branches (max 2) */"]
    for sc in scenes:
        sid = sc.get("id") or "tip"
        kind = _normalize_kind(sc)
        start = float(sc["start"])
        dur = float(sc.get("dur") or 3)
        end = start + dur
        half = bool(sc.get("halfPip", False))
        lines.append(
            f"""          (function(){{
            var sid = {json.dumps(sid)};
            var start = {start};
            var dur = {dur};
            var end = {end};
            var host = document.getElementById("tip-"+sid);
            if(!host) return;
            tl.set(host, {{autoAlpha:0}}, 0);
            tl.fromTo(host, {{autoAlpha:0}}, {{autoAlpha:1, duration:0.28, ease:"power2.out", immediateRender:false}}, start);
            tl.to(host, {{autoAlpha:0, duration:0.28, ease:"power2.in"}}, end - 0.3);
"""
        )
        if half:
            lines.append(
                f"""            tl.to(".cap-stage", {{autoAlpha:0, duration:0.18}}, start);
            tl.to(".cap-stage", {{autoAlpha:1, duration:0.22}}, end - 0.3);
            tl.set("#video-wrap", {{zIndex:3}}, start);
            tl.fromTo("#video-wrap",
              {{y:0, borderRadius:"0px"}},
              {{y:900, borderRadius:"36px 36px 0px 0px", duration:0.55, ease:"power3.inOut", immediateRender:false}},
              start);
            tl.fromTo("#video-cam",
              {{y:0, scale:1}},
              {{y:-120, scale:1.08, duration:0.55, ease:"power3.inOut", immediateRender:false}},
              start);
            tl.to("#video-wrap",
              {{y:0, borderRadius:"0px", duration:0.45, ease:"power3.inOut"}},
              end - 0.45);
            tl.to("#video-cam",
              {{y:0, scale:1, duration:0.45, ease:"power3.inOut"}},
              end - 0.45);
            tl.set("#video-wrap", {{clearProps:"y,borderRadius,zIndex"}}, end);
            tl.set("#video-cam", {{clearProps:"y,scale"}}, end);
"""
            )
        else:
            lines.append("            /* fullBlur: CSS overlay; video filter yok */\n")

        if kind in ("verdict", "stat", "social"):
            lines.append(
                f"""            tl.fromTo("#tip-"+sid+"-card",
              {{autoAlpha:0, y:36, scale:0.96}},
              {{autoAlpha:1, y:0, scale:1, duration:0.48, ease:"expo.out", immediateRender:false}},
              start + 0.12);
"""
            )
            if kind == "verdict":
                lines.append(
                    f"""            tl.fromTo("#tip-"+sid+"-kick",
              {{autoAlpha:0, y:10}},
              {{autoAlpha:1, y:0, duration:0.28, ease:"power2.out", immediateRender:false}},
              start + 0.18);
            tl.fromTo("#tip-"+sid+"-title",
              {{autoAlpha:0, y:18}},
              {{autoAlpha:1, y:0, duration:0.4, ease:"expo.out", immediateRender:false}},
              start + 0.26);
"""
                )
            if kind == "stat":
                lines.append(
                    f"""            tl.fromTo("#tip-"+sid+"-num",
              {{autoAlpha:0, scale:0.82}},
              {{autoAlpha:1, scale:1, duration:0.5, ease:"expo.out", immediateRender:false}},
              start + 0.22);
"""
                )

        elif kind == "nodes":
            nodes = sc.get("nodes") or []
            wires = sc.get("wires") or []
            for i, n in enumerate(nodes):
                nid = n.get("id") or "n"
                delay = start + 0.15 + i * 0.22
                lines.append(
                    f"""            tl.fromTo("#tip-"+sid+"-{nid}",
              {{autoAlpha:0, y:28, scale:0.92}},
              {{autoAlpha:1, y:0, scale:1, duration:0.42, ease:"expo.out", immediateRender:false}},
              {delay});
"""
                )
            if wires and len(nodes) >= 2:
                by_id = {n.get("id"): n for n in nodes}
                for wi, (a, b) in enumerate(wires[:3]):
                    na, nb = by_id.get(a), by_id.get(b)
                    if not na or not nb:
                        continue
                    x1 = int(na.get("x") or 0) + 380
                    y1 = int(na.get("y") or 0) + 90
                    x2 = int(nb.get("x") or 0)
                    y2 = int(nb.get("y") or 0) + 90
                    mid_x = (x1 + x2) / 2
                    d = f"M{x1} {y1} C {mid_x} {y1}, {mid_x} {y2}, {x2} {y2}"
                    lines.append(
                        f"""            (function(){{
              var svg = document.getElementById("tip-"+sid+"-wires");
              if(!svg) return;
              var path = document.createElementNS("http://www.w3.org/2000/svg", "path");
              path.setAttribute("d", {json.dumps(d)});
              path.setAttribute("class", "tip-wire");
              path.id = "tip-"+sid+"-w{wi}";
              svg.appendChild(path);
              var len = path.getTotalLength();
              tl.set(path, {{strokeDasharray:len, strokeDashoffset:len, opacity:1}}, start);
              tl.to(path, {{strokeDashoffset:0, duration:0.7, ease:"power2.inOut"}}, start + 0.45);
            }})();
"""
                    )
            if sc.get("cursor", True) and nodes:
                n0, n1 = nodes[0], nodes[-1]
                x0 = int(n0.get("x") or 200) + 200
                y0 = int(n0.get("y") or 600) + 80
                x1 = int(n1.get("x") or 500) + 200
                y1 = int(n1.get("y") or 800) + 80
                lines.append(
                    f"""            tl.fromTo("#tip-"+sid+"-cur",
              {{autoAlpha:0, x:{x0}, y:{y0}}},
              {{autoAlpha:1, duration:0.2, immediateRender:false}},
              start + 0.5);
            tl.to("#tip-"+sid+"-cur", {{x:{x1}, y:{y1}, duration:1.1, ease:"power1.inOut"}}, start + 0.7);
            tl.to("#tip-"+sid+"-cur", {{autoAlpha:0, duration:0.25}}, end - 0.6);
"""
                )

        elif kind == "branches":
            lines.append(
                f"""            tl.fromTo("#tip-"+sid+"-kick",
              {{autoAlpha:0, y:12}},
              {{autoAlpha:1, y:0, duration:0.32, ease:"power2.out", immediateRender:false}},
              start + 0.12);
            tl.fromTo("#tip-"+sid+"-title",
              {{autoAlpha:0, y:16}},
              {{autoAlpha:1, y:0, duration:0.4, ease:"expo.out", immediateRender:false}},
              start + 0.2);
"""
            )
            for i, _br in enumerate((sc.get("branches") or [])[:3]):
                delay = start + 0.32 + i * 0.14
                lines.append(
                    f"""            tl.fromTo("#tip-"+sid+"-b{i}",
              {{autoAlpha:0, y:28, scale:0.94}},
              {{autoAlpha:1, y:0, scale:1, duration:0.42, ease:"expo.out", immediateRender:false}},
              {delay});
"""
                )
        lines.append("          })();")
    return "\n".join(lines)
