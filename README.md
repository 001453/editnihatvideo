# editnihatvideo — Nihat / Mehmet 9:16 pipeline

Talking-head videoları **HyperFrames 0.8.30** ile paketleyen yerel hat: kesim + altyazı → konu-özel kartlar / b-roll / punch / SFX → Studio preview → MP4 render.

Format: **9:16 · 1080×1920**. Standart: `shared/SHOW_STANDARD.md` + `shared/show-flow.json` (tüm kilitli kurallar orada, detaylı).

Repo: [github.com/001453/editnihatvideo](https://github.com/001453/editnihatvideo)

**Önemli (2026-09):** GitHub'a artık **sadece ortak altyapı** (motor/şablon/scriptler) gider. `videos/` klasörünün tamamı `.gitignore`'da — hiçbir video, kart metni veya timeline GitHub'a gitmiyor. Her hesabın videoları kendine özel/gizli kalır.

---

## A'dan Z'ye: bir video nasıl çıkıyor (tüm adımlar)

Aşağıdaki liste, bir videonun kaynak dosyadan Instagram'a hazır MP4'e kadar geçtiği **her adımı** — Nihat'ın yaptığını ve agent'ın (Claude/Cursor) arka planda yaptığını — sırayla anlatır.

### 1) Kaynak video
- **Nihat:** Talking-head videoyu çeker/kaydeder (göğüs üstü, yüz orta-üst çekim).

### 2) Yeni video başlat
- **Nihat:** Dashboard'da (`start_dashboard.bat` → `http://127.0.0.1:8765/`) kaynak MP4'ü sürükle-bırak, bir Video ID verir (örn. `0930`) → **Hazırla**'ya basar.
- **Sistem:** `videos/<id>/` klasörü oluşur, kaynak video `public/input-video.mp4` olarak kopyalanır, ses metne çevrilir (Whisper/transcribe) → `transcripts/input-video.json`.

### 3) Kesim + altyazı taslağı
- **Nihat:** `editor.html` (veya dashboard üzerinden) ile videoyu keser, konuşma segmentlerini ayarlar → kaydeder → `videos/<id>/project.json` (kesim noktaları + `layout.caption`/`layout.banner` gibi ekran-konumu ayarları burada tutulur).

### 4) Altyazı düzeltme
- **Nihat:** `/captions?id=0930` sayfasında Türkçe karakter hatalarını (İ/ç/ş vb.) düzeltir, gerekirse altyazının ekrandaki konumunu ok tuşlarıyla ayarlar (40px adım).

### 5) Agent paketleme — kartlar + zamanlama
- **Nihat:** Cursor'a "0930 hazır, paketle" tarzı bir cümle yapıştırır (bkz. aşağıdaki hazır şablon).
- **Agent (ben):**
  1. `videos/<id>/transcripts/input-video.json`'ı okur, konudan (altın, gümüş, FED, petrol vb.) hangi sayıların/başlıkların kart olacağına karar verir.
  2. `shared/SHOW_STANDARD.md`'deki **kilitli kurallara** göre yazar — en önemlileri:
     - Kartlar **`cards.html` içine gömülü** yazılır (`.card-host > .card > .card-fx > .root`), registry `proCard` olarak DEĞİL — registry proCard Studio canlı önizlemede görünmüyor.
     - Video başına **5–8 kart**, ilk 10 saniyede kart yok, kartlar arası en az ~6s boşluk.
     - **Punch (kamera zoom) ZORUNLU** — `timeline.json → punches[]` her videoda **3–5 tane**, hold 6–10s, scale 1.10–1.14, asla boş bırakılmaz.
     - **B-roll asla ilk sırada gelmez** — ilk b-roll'un `start` değeri **en az 20.0 saniye**.
     - Punch, hero, IG Follow (mid + end, 4.5s) zamanlarını videonun akışına göre dağıtır.
  3. `videos/<id>/cards.html` ve `videos/<id>/timeline.json` dosyalarını yazar.
  4. Cihaza yazdıktan sonra **dosyayı tekrar okuyup içeriği doğrular** (bazen ilk yazım sessizce eski haline dönebiliyor — bu bilinen bir aksaklık; olursa aynı yazmayı bir kere daha, zorla tekrarlar).

### 6) B-roll (görsel destek klipleri)
- **Agent:** Konuya uygun **en fazla 2** b-roll için sadece **kelime (arama ifadesi) + başlangıç saniyesi** verir — klibi kendisi indirmez.
- **Nihat:** İki yoldan biriyle klip bulur:
  - Google Labs'ten elle indirir, veya
  - **ZSky web** (ücretsiz hesap, zsky.ai) üzerinden ~5 saniyelik klip üretip indirir.
- **Nihat:** Klibi dashboard'daki ilgili b-roll kutusuna sürükle-bırak yapar.
- **Sistem/Agent:** Klip 9:16'ya kırpılır, sessizleştirilir, gerekiyorsa `scripts/prep_zsky_broll.py` ile ileri-geri (ping-pong) yöntemiyle tam **8 saniyeye** uzatılır → `public/broll/<slot>.mp4`.

### 7) Build (derleme)
- **Agent:** `template/build_composition.py`'yi `videos/<id>/build_composition.py`'ye kopyalar, çalıştırır → `cards.html` + `timeline.json`'dan gerçek `index.html` ve (varsa) `compositions/*.html` dosyalarını üretir.
- Bu adım her `cards.html`/`timeline.json` değişikliğinden sonra **tekrar** çalıştırılmalı — yoksa Studio/dashboard'da değişiklik görünmez.

### 8) Studio önizleme
- **Nihat:** HyperFrames Studio'da videoyu açar, **Ctrl+F5** ile sert yeniler (Studio kendi içinde ayrıca dosyaları derleyip önbelleğe alıyor — bazen bu adım atlanırsa eski hal görünür).
- Kartların, punch'ların, b-roll'un, IG Follow banner'ının doğru zamanda/konumda geldiği burada kontrol edilir.

### 9) Render
- **Nihat/Agent:** Önce **draft** kalite render alınır (hızlı kontrol), sorun yoksa **high** kalite render alınır (2 dk'lık video ≈ 15–20 dk sürer). Render biterken Studio yenilenmez.
- Çıktı: `videos/<id>/renders/*.mp4` (bu klasör git'e hiç gitmez).

### 10) Paylaşım
- **Nihat:** Render edilen MP4'ü Instagram'a (`@cetin.finans`) elle yükler.

### 11) Ortak altyapıyı GitHub'a gönderme (video'lar HARİÇ)
- Sadece `shared/`, `template/`, `scripts/`, kök config dosyaları gibi **ortak motor** değiştiğinde gönderilir — örn. yeni bir kilitli kural eklendiğinde, bir script düzeltildiğinde.
- `git_guvenli_gonder.bat`'a çift tıkla → otomatik commit + push. `.gitignore` artık `videos/` klasörünün tamamını dışarıda tuttuğu için hiçbir video/kart/timeline GitHub'a gitmez, sadece motor gider.
- Çakışma / hata çıkarsa ekran görüntüsünü veya tüm terminal çıktısını agent'a yapıştır — tek başına çözmeye çalışma.

---

## Ne sabit, ne değişir?

| Sabit (kalıp) | Her videoda yeni |
| --- | --- |
| Face-safe layout + cam kart look | Transcript'ten kart metni/sayılar |
| Montserrat karaoke altyazı | Caption zamanları |
| IG Follow anim (mid+end, 4.5s) | Punch / IG / hero zamanları |
| Kart motion ailesi `soft\|rise\|slide\|scale` | Enter çeşidi + geçişler |
| `template/build_composition.py` motoru | `cards.html`, `timeline.json` |
| Punch **3–5, zorunlu, asla boş değil** | Punch saniyeleri (kart akışına göre) |
| B-roll max **2×8s**, ilk 20s'den önce gelmez | Kelime + start; dashboard drop |
| Dashboard sürükle-bırak | Slot dosyaları `public/broll/<ad>.mp4` |
| GitHub'a sadece ortak motor gider | Video içeriği hep yerelde/özel kalır |

Konuya göre ek: drone / mockup / split vb. (video başına en fazla **1** büyük özel an, bkz. `shared/SHOW_STANDARD.md` bölüm C).

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

### Adımlar (özet — detaylı anlatım yukarıda "A'dan Z'ye")

1. **Kaynak MP4** sürükle-bırak → Video ID (örn. `0930`) → **Hazırla**
2. `editor.html` / dashboard ile kesim + caption → `project.json`
3. Altyazı düzelt: **/captions?id=0930** (Türkçe İ/ç vb.)
4. Cursor'a paket cümlesini yapıştır → agent `cards.html` + `timeline.json` yazar
   *(hazır paket silinmez; `Hazırla` force etmez)*
5. Agent **b-roll kelimesi + başlangıç saniyesi** verir (hep **8 sn**, ilk 20s'den sonra)
6. Dashboard'da **B-roll sürükle-bırak** kutularına 9:16 MP4 bırak → encode → bağla
7. İkisi yeşil → rebuild → **Studio** → **Ctrl+F5**
8. Draft / high render

Agent `videos/<id>/PACKAGE_ME.json` görürse doğrudan paketler.

---

## B-roll kuralı (kilit)

- En fazla **2** clip
- Süre **hep 8 saniye** — sen başlangıç cümlesine göre hazırlarsın
- **İlk sırada/açılışta asla b-roll gelmez** — ilk b-roll'un başlangıcı en az **20.0 saniye**
- Agent sadece **kelime + start** verir
- Kaynak: Google Labs (elle indir) veya **ZSky web** (ücretsiz, elle indir + `prep_zsky_broll.py` ile 8sn'e uzatılır)
- Dashboard `/api/upload-broll` → `public/broll/<id>.mp4` (9:16, muted, `-t 8`)
- Slim chip kartlar b-roll üstüne binebilir; büyük cam kart b-roll penceresine binmez

---

## CLI akış (dashboard'suz)

### 1) Yeni video

```powershell
cd <repo>
py -3.12 scripts\new_video.py 0930 --source "D:\path\to\source.mp4" --account nihat
```

Hesap: `nihat` veya `mehmet`.

### 2) İnsan: kes + altyazı

`editor.html` → kaydet → `videos/<id>/project.json`
Eski `Downloads\project.json` kullanma.

### 3) Agent paketle

Skill: `.cursor/skills/package-nihat-video/SKILL.md`
Kurallar: `.cursor/rules/nihat-pipeline.mdc` + `shared/SHOW_STANDARD.md`

### 4) Build

```powershell
Copy-Item -Force template\build_composition.py videos\0930\build_composition.py
py -3.12 videos\0930\build_composition.py
```

Studio'da **Ctrl+F5**.

### 5) Preview / render

```powershell
cd videos\0930
$env:HYPERFRAMES_SKIP_SKILLS='1'
npx --yes hyperframes@0.8.30 preview
npx --yes hyperframes@0.8.30 render --quality draft --fps 30 --output renders\0930-draft.mp4
npx --yes hyperframes@0.8.30 render --quality high --fps 30 --output renders\0930-high.mp4
```

High ~2 dk video ≈ **15–20 dk**. Bitene kadar Studio'yu yenileme.

---

## Klasör yapısı

```
scripts/            dashboard, encode, new_video, TR caption fix, zsky broll hazırlama, ikon üretimi
shared/              look, SFX, show-flow, SHOW_STANDARD, PRO_CARDS registry, build_engine
template/            build_composition.py (kaynak)
videos/<id>/         her video kendi klasöründe (GitHub'a gitmez, sadece yerel)
  project.json       kesim + caption + layout
  transcripts/       ses-metin dönüşümü
  cards.html         konu kartları (inline, registry değil)
  timeline.json      punch / b-roll / IG / hero / mg / proCards / special
  index.html         build çıktısı
  compositions/      build çıktısı pro-card composition'ları (varsa)
  public/            input-video, broll, sfx, fonts, IG png
  renders/            MP4 (gitignore)
captions.html         tek sayfa altyazı editörü
dashboard.html        hub + b-roll drop
editor.html            kesim / caption
start_dashboard.bat    dashboard başlat
git_guvenli_gonder.bat güvenli commit + push (sadece ortak motor)
.cursor/               rules + package-nihat-video skill
```

---

## Kilit kurallar (kısa — tam liste `shared/SHOW_STANDARD.md`)

- Kart bandı altyazı ile aynı bölgede; yüz alanı (y 300–1100) boş kalır
- Kartlar `cards.html` içine inline yazılır, registry proCard olarak değil
- Her kart-host ekranda en fazla 3.0 saniye; ilk 10 saniyede kart yok
- **Punch 3–5, asla boş değil**, hold 6–10s, scale 1.10–1.14
- **B-roll ilk 20 saniyeden önce gelmez**, max 2×8s
- IG Follow: mid + end, 4.5s, exclusive
- Disclaimer şeffaf altta **YATIRIM TAVSİYESİ DEĞİL**
- Paketlenmiş klasörü (`cards.html` + `project.json`) prepare **silebilir** — force kullanma
- GitHub'a sadece ortak motor gider; `videos/` hiç gitmez

Detay: `shared/SHOW_STANDARD.md`

---

## Git / medya

Repoda **sadece ortak kod + şablon** vardır. `videos/` klasörünün tamamı `.gitignore`'da — hiçbir video, kart metni, timeline, transcript veya render GitHub'a gitmez; her hesabın içeriği kendine özel kalır.

Ayrıca gitignore'da: `*.mp4`, cache/waveform/thumbnail klasörleri, `_inbox/`, `.cursor/mcp.json` (gizli anahtar).

Klon sonrası: kendi video klasörünü (`videos/<id>/`) kendin oluşturursun/taşırsın — repo'da hazır video gelmez, sadece motor gelir.

---

## Cursor'a yapıştır (örnek)

```
videos/0930 hazir. project.json + transcript var. onceki videolarin akisiyla paketle:
kartlar, b-roll, punch, IG, build. Ctrl+F5 soyle. Kod bilmiyorum; soru sorma, dogrudan uygula.
```

B-roll ekledikten sonra aynı cümleyi tekrar kullanabilirsin; agent slotları bağlar ve rebuild eder.
