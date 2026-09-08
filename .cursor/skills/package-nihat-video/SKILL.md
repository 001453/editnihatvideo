---
name: package-nihat-video
description: Analyze a new Nihat/Mehmet talking-head like video 0907 and package it with the same show flow — topic-specific cards, b-roll PIP, punches, SFX, IG banner. Use when the user adds a new video, asks to package/dress a clip, or after editor.html saves project.json.
---

# Package like 0907

**Show is LOCKED** (`shared/SHOW_STANDARD.md`, `shared/show-flow.json`). Same transparent cards, unique enters, keyword captions, whip b-roll, SFX, PIP left, hero 3D. **New topic → new copy / times / b-roll only.** Optional: at most **one** `special` moment per video (drone pull-back, crash zoom, mockup, split…).

0907 is the show bible (`videos/0907/`). Do not copy 0907 faiz/CDS copy. Do not leave empty `cards.html`.

## When a new video arrives

1. `python scripts/new_video.py <id> --source "D:\path.mp4" --account nihat|mehmet` if the folder does not exist.
2. Human: `editor.html` → cuts + captions → `videos/<id>/project.json`.
3. Agent (this skill): read `project.json` words + captions + duration. Segment the speech. Write `cards.html` + `timeline.json` + fetch b-roll. Build. Tell user Ctrl+F5.

Do not ask cut/position questions if JSON already has them.

## Analyze

Read `videos/<id>/project.json`. Group words into beats at punctuation / pauses.

For each beat pick a **0907 card type** only if the speech supports it. Pull numbers and quotes from the transcript — do not invent levels, %, CDS, dates.

Typical density for a ~2 min clip: **6–10 cards**, **max 2 b-rolls (8s each, Labs)**, **3–5 punches (hold 6–10s)**. Shorter clip → fewer, same kit.

Map:

| Speech | Card class | Motion |
| --- | --- | --- |
| Opening questions | `.root.hook` + `.q` | `data-at` when each question is spoken |
| Price / level path | `.root.glass.graph-card` | `path[data-draw]` |
| Support vs resistance pair | `.root.glass.levels` | `data-fill` on bars |
| Named drivers (2–4 words) | `.root.glass.chips.slim` | `data-at` stagger |
| One or two stats | `.root.glass.stats` | `data-count` |
| One hero number | `.hero-num` | `data-count` + `data-scale-in` |
| History of a number | `.root.glass.graph-card` | draw path |
| Net verdict | `.root.glass.punch` + `.title.red` | `data-in="back"` |
| Alternate scenario | `.root.glass.punch` | fade title |
| End | `.banner` transparent | **YATIRIM TAVSİYESİ DEĞİL** only, bottom, `data-in="drop"` |

Clone structure from `videos/0907/cards.html`. Change ids, copy, times. Keep `card-accent` + `card-sheen` on glass cards.

Time `data-start` / `data-duration` to the spoken beat. Inner `data-at` = the word time for that line.

## Same flow (locked)

Full notes: `shared/SHOW_STANDARD.md` · machine recipe: `shared/show-flow.json`.

- Captions from editor; Anton 3D. No full-frame video darkening.
- Face full-bleed; cards **top band** (transparent glass, no heavy black); captions mid-lower + **keyword pop**; PIP **left**.
- Card enter/exit: each card a **unique** mode from slam/soft/glitch/tilt/wipe/pop/rise/flip/snap/drift/zoom/fold + mid-hold progress. One hero 3D (`timeline.hero`).
- Punch: hold + click/sub-hit; scales 1.10–1.16; not on IG window.
- B-roll: **max 2×8s**, whip + whoosh, muted, PIP left. Labs: `public/broll/LABS_PROMPTS.md`.
- Line SFX by type (slam louder, kicker softer, count → ui-confirm).
- Disclaimer: transparent centered **YATIRIM TAVSİYESİ DEĞİL** bottom; no NİHAT bar.
- IG: PNG only, 2.3s, exclusive.
- `#overlays` untimed. Unmuted talking-head only.

## B-roll değiştir (Google Labs / elle)

1. Prompt: `videos/<id>/public/broll/LABS_PROMPTS.md` (veya agent yeni yazsın).
2. Labs’te **9:16, ~8sn** üret → MP4 indir.
3. Dosyayı `videos/<id>/public/broll/<ad>.mp4` koy (gerekirse önce `_raw` encode):
   `py -3.12 scripts/encode_input.py videos/<id>/public/broll/<ad>_raw.mp4 videos/<id>/public/broll/<ad>.mp4 --broll`
4. `timeline.json` → `broll` start/dur/file güncelle.
5. Rebuild: `py -3.12 videos/<id>/build_composition.py` → Studio **Ctrl+F5**.

Agent’a: “şu mp4’ü gold slotuna bağla” demen yeterli.

## Write + build

1. `videos/<id>/cards.html`
2. `videos/<id>/timeline.json` — broll, punches `[[t, hold], ...]`, igBanner, optional cardSfx
3. `python videos/<id>/build_composition.py`
4. `$env:HYPERFRAMES_SKIP_SKILLS='1'; npx --yes hyperframes@0.8.30 lint`
5. Tell user Studio **Ctrl+F5**. Do not start a long render unless asked.

## Occupied windows

Do not stack two big glass cards. Slim chips may sit on b-roll. Punches may sit on a card. IG banner is exclusive.

Reference occupancy (0907, scale times to this duration): hook open → graph → b-roll → levels+punch → b-roll+chips → stats → punch → hero stats → history graph → b-roll → punch title → punch hold → scenario → IG near end → disclaimer.
