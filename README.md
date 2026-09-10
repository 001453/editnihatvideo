# editnihatvideo — Nihat / Mehmet 9:16 pipeline

Talking-head videoları **HyperFrames 0.8.30** ile paketleyen yerel hat: kesim + altyazı → konu-özel kartlar / b-roll / punch / SFX → Studio preview → MP4 render.

Format: **9:16 · 1080×1920**. Standart: `shared/SHOW_STANDARD.md` + `shared/show-flow.json`.

**Güncel çalışan örnek:** `videos/0909` (Diyanet / TLK). Referans kalıp: `videos/0910`, `videos/0907b`.

Repo: [github.com/001453/editnihatvideo](https://github.com/001453/editnihatvideo)

---

## Ne sabit, ne değişir?

| Sabit (kalıp) | Her videoda yeni |
| --- | --- |
| Face-safe layout + cam kart look | Transcript’ten kart metni |
| Montserrat karaoke altyazı | Caption zamanları |
| IG Follow anim (mid+end) | Punch / IG / hero zamanları |
| Kart motion ailesi `soft\|rise\|slide\|scale` | Enter çeşidi + geçişler |
| `template/build_composition.py` motoru | `cards.html`, `timeline.json` |
| Max **2×8s** b-roll (sen eklersin) | Kelime + start; dashboard drop |
| Dashboard sürükle-bırak | Slot dosyaları `public/broll/<ad>.mp4` |

Konuya göre ek: drone / mockup / split vb. (video başına en fazla **1** büyük özel an).

---

## Gereksinimler

- Windows (PowerShell)
- **Python 3.12** (`py -3.12`)
- **Node.js** + `npx` (HyperFrames CLI)
- Cursor (agent paketleme için)
- Kaynak MP4 (talking-head) + isteğe bağlı 2× **8 sn** 9:16 b-roll

NVENC burada yok; encode **libx264**. `--gpu` kullanma.

---

## Hızlı başlangıç (önerilen)

```powershell
cd <repo>
start_dashboard.bat
# veya: py -3.12 scripts\dashboard_server.py
```

Tarayıcı: **http://127.0.0.1:8765/**

### Adımlar

1. **Kaynak MP4** sürükle-bırak → Video ID (örn. `0911`) → **Hazırla**
2. `editor.html` / dashboard ile kesim + caption → `project.json`
3. Altyazı düzelt: **/captions?id=0911** (Türkçe İ/ç vb.)
4. Cursor’a paket cümlesini yapıştır → agent `cards.html` + `timeline.json` yazar  
   *(hazır paket silinmez; `Hazırla` force etmez)*
5. Agent **2 b-roll kelimesi + başlangıç saniyesi** verir (hep **8 sn**)
6. Dashboard’da **B-roll sürükle-bırak** kutularına 9:16 MP4 bırak → encode → bağla
7. İkisi yeşil → rebuild → **Studio** → **Ctrl+F5**
8. Draft / high render

Agent `videos/<id>/PACKAGE_ME.json` görürse doğrudan paketler.

---

## B-roll kuralı (kilit)

- En fazla **2** clip
- Süre **hep 8 saniye** — sen başlangıç cümlesine göre hazırlarsın
- Agent sadece **kelime + start** verir
- Dashboard `/api/upload-broll` → `public/broll/<id>.mp4` (9:16, muted, `-t 8`)
- Slim chip kartlar b-roll üstüne binebilir; büyük cam kart b-roll penceresine binmez

Örnek (0909):

| Slot | Kelime | Start |
| --- | --- | --- |
| 1 | VAKIF | 46.0s |
| 2 | GETİRİ | 111.0s |

---

## CLI akış (dashboard’suz)

### 1) Yeni video

```powershell
cd <repo>
py -3.12 scripts\new_video.py 0911 --source "D:\path\to\source.mp4" --account nihat
```

Hesap: `nihat` veya `mehmet`.

### 2) İnsan: kes + altyazı

`editor.html` → kaydet → `videos/<id>/project.json`  
Eski `Downloads\project.json` (C0082) kullanma.

### 3) Agent paketle

Skill: `.cursor/skills/package-nihat-video/SKILL.md`  
Kurallar: `.cursor/rules/nihat-pipeline.mdc`

### 4) Build

```powershell
Copy-Item -Force template\build_composition.py videos\0911\build_composition.py
py -3.12 videos\0911\build_composition.py
```

Studio’da **Ctrl+F5**.

### 5) Preview / render

```powershell
cd videos\0911
$env:HYPERFRAMES_SKIP_SKILLS='1'
npx --yes hyperframes@0.8.30 preview
npx --yes hyperframes@0.8.30 render --quality draft --fps 30 --output renders\0911-draft.mp4
npx --yes hyperframes@0.8.30 render --quality high --fps 30 --output renders\0911-high.mp4
```

High ~2 dk video ≈ **15–20 dk**. Bitene kadar Studio’yu yenileme.

---

## Klasör yapısı

```
scripts/            dashboard, encode, new_video, TR caption fix
shared/             look, SFX, show-flow, SHOW_STANDARD
template/           build_composition.py (kaynak)
videos/0909/        güncel örnek paket (metadata; MP4 git’te yok)
videos/0910/        önceki örnek
videos/<id>/
  project.json      kesim + caption
  cards.html        konu kartları
  timeline.json     punch / b-roll / IG / hero / mg / special
  index.html        build çıktısı
  public/           input-video, broll, sfx, fonts, IG png
  renders/          MP4 (gitignore)
captions.html       tek sayfa altyazı editörü
dashboard.html      hub + b-roll drop
editor.html         kesim / caption
start_dashboard.bat dashboard başlat
.cursor/            rules + package-nihat-video skill
```

---

## Kilit kurallar (kısa)

- Tek `#caption-host`, Anton 3D; ton `.cap-item` üzerinde
- Talking-head: unmuted `data-has-audio="true"` — aynı dosyadan ikinci VO yok
- `#overlays` untimed; kartlar nested
- IG: PNG only, exclusive (~24s ve bitişten ~11s önce, 2.3s)
- Punch: hold + ease out; soft click in/out
- Kart in: `pop.mp3` + sheen; b-roll muted 9:16 + PIP sol + whoosh
- Disclaimer şeffaf altta **YATIRIM TAVSİYESİ DEĞİL**
- Paketlenmiş klasörü (`cards.html` + `project.json`) prepare **silebilir** — force kullanma

Detay: `shared/SHOW_STANDARD.md`

---

## Git / medya

Repoda **kod + şablon + paket metadata** vardır. Büyük medya **gitignore**:

- `*.mp4` (ve `videos/*/public/broll/*.mp4`, `input-video.mp4`)
- `videos/*/renders/`
- cache / waveform / thumbnails / `_inbox/`

Klon sonrası: kendi kaynak MP4 + 2×8s b-roll’ünü dashboard ile koy, rebuild et.

---

## Cursor’a yapıştır (örnek)

```
videos/0909 hazir. project.json + transcript var. 0907 akisiyla paketle:
kartlar, b-roll, punch, IG, build. Ctrl+F5 soyle. Kod bilmiyorum; soru sorma, dogrudan uygula.
```

B-roll ekledikten sonra aynı cümleyi tekrar kullanabilirsin; agent slotları bağlar ve rebuild eder.
