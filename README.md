# editnihatvideo — Nihat / Mehmet 9:16 pipeline

Talking-head videoları **HyperFrames 0.8.30** ile paketleyen yerel hat: kesim + altyazı → konu-özel kartlar / b-roll / punch / SFX → Studio preview → MP4 render.

Format: **9:16 · 1080×1920**. Show bible: `videos/0907`. Standart: `shared/SHOW_STANDARD.md` + `shared/show-flow.json`.

Repo: [github.com/001453/editnihatvideo](https://github.com/001453/editnihatvideo)

---

## Ne sabit, ne değişir?

| Sabit (kalıp) | Her videoda yeni |
| --- | --- |
| Kart tipleri, cam look, enter anim havuzu | Transcript’ten kart metni |
| Anton 3D altyazı + keyword pop | Caption zamanları / keyword’ler |
| Punch, PIP (sol), IG banner, SFX pack | Punch / IG / hero zamanları |
| `template/build_composition.py` motoru | `cards.html`, `timeline.json`, b-roll |
| Max 2×8s b-roll kuralı | Konuya özel Labs prompt + dosyalar |

Konuya göre ek: drone pull-back, mockup, split A/B, crash zoom vb. (video başına en fazla **1** büyük özel an).

---

## Gereksinimler

- Windows (PowerShell)
- **Python 3.12** (`py -3.12`)
- **Node.js** + `npx` (HyperFrames CLI)
- Cursor (agent paketleme için)
- Kaynak MP4 (talking-head)

NVENC burada yok; encode **libx264**. `--gpu` kullanma.

---

## Hızlı başlangıç (dashboard)

```powershell
cd <repo>
py -3.12 scripts\dashboard_server.py
```

Tarayıcıda:

1. MP4 **sürükle-bırak**
2. Video ID ver (örn. `0911`)
3. **Hazırla** → oluşan cümleyi Cursor’a yapıştır
4. Agent paketler → **Studio** → Ctrl+F5 → draft / high render

Agent `videos/<id>/PACKAGE_ME.json` görürse doğrudan paketler.

---

## CLI akış (adım adım)

### 1) Yeni video iskeleti

```powershell
cd <repo>
py -3.12 scripts\new_video.py 0911 --source "D:\path\to\source.mp4" --account nihat
```

Hesap: `nihat` veya `mehmet` (altyazı ton renkleri).

### 2) İnsan: kes + altyazı

`editor.html` aç → kesimleri ve caption’ları ayarla → kaydet.  
Çıktı: `videos/0911/project.json` (+ transcript).

**Not:** Eski `C:\Users\...\Downloads\project.json` (C0082) kullanma.

### 3) Agent: paketle (0907 akışı)

Cursor’da skill: `.cursor/skills/package-nihat-video/SKILL.md`

Agent:

- Transcript’i okur, beat planlar
- **Bu konuya** `cards.html` yazar (0907 metnini kopyalamaz)
- `public/broll` + `timeline.json` (punch, IG, hero, special)
- `build_composition.py` çalıştırır → `index.html`

### 4) Build (manuel gerekirse)

```powershell
Copy-Item -Force template\build_composition.py videos\0911\build_composition.py
py -3.12 videos\0911\build_composition.py
```

Studio’da **Ctrl+F5** (cache temiz).

### 5) Preview / render

```powershell
cd videos\0911
$env:HYPERFRAMES_SKIP_SKILLS='1'
npx --yes hyperframes@0.8.30 preview
npx --yes hyperframes@0.8.30 render --quality draft --fps 30 --output renders\0911-draft.mp4
npx --yes hyperframes@0.8.30 render --quality high --fps 30 --output renders\0911-high.mp4
```

High ~2 dk video için genelde **~15–20 dk** (low-memory / 1 worker). Bitene kadar Studio’yu yenileme.

Çıktı örneği: `videos/0911/renders/0911-high.mp4`

---

## Klasör yapısı

```
scripts/          dashboard, new_video, yardımcılar
shared/           look, SFX, show-flow, SHOW_STANDARD
template/         build_composition.py (kaynak)
videos/0907/      show bible (referans paket)
videos/<id>/      her bölüm
  project.json    kesim + caption (editor)
  cards.html      konu kartları
  timeline.json   punch / b-roll / IG / special
  index.html      HyperFrames composition (build çıktısı)
  public/         input-video, broll, sfx, fonts, IG png
  renders/        MP4 çıktılar (git’te yok)
.cursor/          rules + package-nihat-video skill
editor.html       insan kesim / caption UI
dashboard.html    sürükle-bırak giriş
```

---

## Kilit kurallar (kısa)

- Tek `#caption-host`, Anton 3D; ton `.cap-item` üzerinde
- Talking-head: unmuted `data-has-audio="true"` — aynı dosyadan ikinci VO yok
- `#overlays` untimed; kartlar içine nested
- IG: PNG only, exclusive pencere (~24s ve bitişten ~11s önce, 2.3s)
- Punch: hold + ease out; soft click in/out
- Kart in: `pop.mp3` + sheen; b-roll muted 9:16 + PIP + whoosh
- Full-frame karartma yok; disclaimer şeffaf altta **YATIRIM TAVSİYESİ DEĞİL**

Detay: `shared/SHOW_STANDARD.md`

---

## Git / medya

Repoda **kod + şablon + örnek paket metadata** vardır. Büyük medya genelde **gitignore**:

- `videos/*/public/input-video.mp4`
- `videos/*/renders/`
- cache / waveform / thumbnails

Klonladıktan sonra her video için kendi kaynak MP4’ünü `new_video.py` / dashboard ile koy.

---

## Sonraki videolar

Kalıp aynı. Konu değişince agent yeni kart / b-roll / punch yazar; geçiş, mockup, drone vb. konuya uygun **tek** özel jest olarak eklenir.
