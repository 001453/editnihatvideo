# Nihat show standard (KİLİTLİ)

Her yeni video: **aynı motor** (look / anim / SFX / geçiş) + **sadece bu konunun** yazıları, kart kopyası, b-roll, punch zamanı.

Format: **9:16 · 1080×1920 · yüz önde · üstte kart boşluğu · altyazı · ses**.

---

## A) Her videoda zorunlu

### Çerçeve
- Talking-head full-bleed, sesli, tek VO. **Çekim dili:** göğüs üstü, yüz orta-üst.
- **Face-safe layout (1080×1920):**
  - Kart bandı: **y 56–280** (alın üstü) — chip `h≤100`, data kart `h≤230`, `face-safe` dense
  - Yüz boş: **y 300–1100** (alın/göz/yüz) — kart / MG yok
  - Altyazı: **y ~1208** göğüs
  - Disclaimer: **y ~1580**
  - Sağ ~150px IG rail boş. PIP **sol**. Kart max ~880px.
- Kartlar: cam kit + video başına **1–3 pro registry kart** (üst bant, scale ≤0.34). Captions sekmesi / Liquid Glass VFX yok.
- **Full-frame karartma yok.**

### Altyazı
- **Montserrat Black karaoke**: kelimeler silik → konuşulunca accent (`#FACC15`/kırmızı/lime) → sonra beyaz. 4 köşe siyah outline. En fazla **2 satır**.
- Giriş: **sadece opacity** (y/x yok — Studio sürüklemesiyle çakışmasın).
- **Tek ortak konum:** `project.json` → `layout.caption` `{x,y,w,h,fontSize}`. Varsayılan ~`x:40 y:1208`.
- Konum ayarı: dashboard **`/captions?id=…`** ok tuşları (adım 40px) veya `POST /api/caption-pos` → rebuild → Studio **Ctrl+F5**.
- Studio’da altyazı sürükleme **yasak** (kasar; seek’te kaybolur). Satır bazlı `captions[i].x/y` kullanılmaz.
- Punto varsayılan **~58–69**; CapCut-style fit. Sağda IG rail payı.
- Zamanlama: `project.json` `words[]` + caption `wordStart`/`wordEnd`.
- Metin sadece editor transcript’inden.

### Kartlar (şeffaf cam — siyah kutu yok)
- `rgba` cam + text-shadow; punch kartlarda hafif kırmızı tint.
- **IG Reels motion lock** (AI Video Studio): enter **0.42s `expo.out`**, exit **0.38s**, soft blur land — **bounce / glitch / snap yok**.
- Enter ailesi (unique): `soft | rise | slide | scale` — eski slam/glitch/tilt otomatik map edilir.
- Hold: sadece hafif breathe (`y:-5`). Shake/pulse/nudge yok.
- Parça girişleri: yumuşak rise + kelime stagger — spin/back.out yok.
- Video başına **1 hero 3D** (`timeline.hero`).
- Disclaimer: şeffaf, ortalı **YATIRIM TAVSİYESİ DEĞİL**, alt (~y 1580), NİHAT yok.
- Kopya: **sadece bu transcript**; 0907 faiz/CDS metni kopyalanmaz.

### Punch / B-roll / IG / SFX
- Punch 3–5, hold 6–10s, scale 1.10–1.14, click+sub-hit.
- B-roll **max 2×8s** — **kullanıcı ekler** (dashboard drop); agent sadece keyword + start. Whip + whoosh, PIP sol.
- **IG Follow (KİLİT):** animated banner `shared/instagram-follow.html`
  - Brand: Nihat Çetinkaya · `@cetin.finans` · `shared/ig_avatar.png`
  - **2 kez:** mid (~video ortası, kart boşluğunda) + end (sona yakın, kartlarla çakışmaz)
  - Süre **4.5s**, exclusive (kart/b-roll üstünde değil)
  - Motion: üstten expo slide-in → Takip Et press → Takip → slide-out
  - SFX: `swoosh-up` · frozen PNG / banner m4a **yasak**
- Satır SFX tipine göre (slam dolu, kicker hafif, count → ui-confirm).

### Build
`cards.html` + `timeline.json` → `build_composition.py` → Ctrl+F5.  
Look: `shared/`. Recipe: `shared/show-flow.json`.

---

## B) Konuya özel (her videoda YENİ yazılır)

- Kart metinleri, sayılar, chapter etiketleri  
- B-roll konusu + Labs prompt  
- Punch / hero / IG zamanları  
- Keyword listesi transcript’e göre genişler  

Animasyon **stili kilitli**; içerik **serbest**.

### Motion graphics (`timeline.mg`)
Kart değil — overlay efektler. Video’da **2–5** yeter.
Tipler: `sparkline` | `stroke` | `sparks` | `flash` | `ticker` | `underline`

---

## C) Video başına 1 “özel an” (öneri havuzu)

Her pakette **en fazla 1** büyük jest — tekrar edilirse ucuzlaşır.

| Özel an | Ne | Ne zaman |
| --- | --- | --- |
| **Drone / pull-back** | Kamera scale 1→0.82 + hafif rotate, dünya “yukarıdan” | En güçlü tez cümlesi (~1.2s) |
| **Crash zoom** | Çok sert punch 1.22 + sub-hit | Uyarı / “risk” kelimesi |
| **Mockup phone** | 9:16 telefon çerçevesinde grafik/kart | “şöyle görünür” / app / ekran anlatımı |
| **Split A vs B** | İki şeffaf panel karşı tilt | fon vs hisse, senaryo karşılaştırması |
| **Chart scrub** | Grafik üzerinde imleç + değer | tek hero sayı |
| **Frozen frame + stamp** | Anlık freeze + “DİKKAT” mühür | kural / yasak cümlesi |
| **Whip to B-roll** | (zaten var) ekstra abartılı 1 clip | görsel kanıt anı |

**Drone önerisi (senin örneğin):**  
Tek seferlik `timeline.json` → `"special": {"type":"drone","at":52.4,"dur":1.4}` — talking-head hafif küçülür, üstte chapter/kart sabit kalır, whoosh-long. Her videoda değil; ~2 dk’da bir kez.

---

## D) Sonraki gelişim (öncelik)

1. `special.drone` / `crash` builder desteği (1/video)  
2. Split-tilt compare kart tipi  
3. Mockup telefon frame bileşeni  
4. Açılış 0.5s hook slam (ilk kare)  
5. İsteğe bağlı çok hafif bed + duck (A/B)

Uzak dur: her karta drone, sağ PIP, siyah kart kutusu, 3+ b-roll, full karartma.
