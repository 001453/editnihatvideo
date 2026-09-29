# Nihat show standard (KİLİTLİ)

Her yeni video: **aynı motor** (look / anim / SFX / geçiş) + **sadece bu konunun** yazıları, kart kopyası, b-roll, punch zamanı.

Format: **9:16 · 1080×1920 · yüz önde · altyazı bandında kart · altyazı · ses**.

---

## A) Her videoda zorunlu

### Çerçeve
- Talking-head full-bleed, sesli, tek VO. **Çekim dili:** göğüs üstü, yüz orta-üst.
- **Face-safe layout (1080×1920) — KİLİT (2026-09, kullanıcı geri bildirimi):**
  - Kart bandı: **altyazı ile aynı bölge** — `project.json → layout.caption.y` civarı (video bazlı değişir, örn. ~y 1440–1690). Kart ekrandayken altyazı zaten otomatik gizleniyor (bkz. Altyazı bölümü), kart o boşluğu doldurur. **Eski üst bant (y 56–280) artık kullanılmıyor** — orada küçük/boş duruyordu, kaldırıldı.
  - Yüz boş: **y 300–1100** (alın/göz/yüz) — kart / MG yok
  - Altyazı: **`layout.caption.y`** (video bazlı, dashboard `/captions?id=…`'den ayarlanır)
  - Disclaimer: **en altta**, kart/altyazı bandının biraz altında (~y 1600–1650) — asla üst bantta değil.
  - Sağ ~150px IG rail boş. PIP **sol**. Kart max ~880-1000px (altyazı genişliğiyle uyumlu, `x:40`).
- Kartlar: cam kit, video başına **1–3 özel/konuya-özgü kart**. Genel çeşitler için `shared/PRO_CARDS.md` registry'sini referans al ama **registry proCard (`data-composition-src`) olarak DEĞİL**, `cards.html` içine gömülü inline `.card-host > .card > .card-fx > .root` yapısı olarak yaz (registry proCard'lar Studio canlı önizlemede görünmüyor — bilinen sınırlama). `timeline.json` → `proCards[]` boş kalsın (`[]`). Captions sekmesi / Liquid Glass VFX yok.
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
- **Punch telafisi (KİLİT — 2026-09, kullanıcı geri bildirimi):** kamera yakınlaşınca (punch) altyazı çeneye binmesin diye yukarı kayıyordu ama tam telafi fazla yukarı/havada bırakıyordu — telafi **%35**'e düşürüldü (`shared/build_engine.py` → `punchCaptionCompensate`). Kamera uzakken (punch dışı) davranış değişmedi.

### Kartlar (şeffaf cam — siyah kutu yok)
- `rgba` cam + text-shadow; punch kartlarda hafif kırmızı tint.
- **IG Reels motion lock** (AI Video Studio): enter **0.42s `expo.out`**, exit **0.38s**, soft blur land — **bounce / glitch / snap yok**.
- Enter ailesi (unique): `soft | rise | slide | scale` — eski slam/glitch/tilt otomatik map edilir.
- Hold: sadece hafif breathe (`y:-5`). Shake/pulse/nudge yok.
- Parça girişleri: yumuşak rise + kelime stagger — spin/back.out yok.
- Video başına **1 hero 3D** (`timeline.hero`).
- Disclaimer: şeffaf, ortalı **YATIRIM TAVSİYESİ DEĞİL**, en altta (~y 1600–1650, kart/altyazı bandının altında), NİHAT yok.
- Kopya: **sadece bu transcript**; 0907 faiz/CDS metni kopyalanmaz.

### Kart ritmi / süre (KİLİT — 2026-09)
- Her kart-host ekranda **en fazla 3.0 saniye** kalır — kicker/title/note bu pencereye sığacak kadar kısa yazılır, tam cümle değil.
- Videonun **ilk 10 saniyesinde hiç kart yok** (hero dahil) — konuşmacı temiz başlar.
- Ondan sonra kartlar **seyrek ve aralıklı** gelir (kartlar arası boşluk en az ~6s, ortalama ~15-20s) — asla art arda, asla sürekli akış.
- Toplamda **5–8 kart** yeter (bkz. `density.cards`); az ve öz, konu değiştikçe bir kart, dolgu için değil.

### Punch / B-roll / IG / SFX
- Punch 3–5, hold 6–10s, scale 1.10–1.14, click+sub-hit.
- **Punch ZORUNLU (KİLİT — 2026-09, kullanıcı geri bildirimi):** `timeline.json`'daki `"punches"` listesi **asla boş bırakılmaz** — her videoda 3-5 punch olmalı. (2026-09'da 0928/0929/0930'da agent bunu unutup boş bıraktı, kamera zoom hiç gelmedi — o videolar düzeltilmedi/olduğu gibi kaldı, ama bundan sonraki her videoda bu adım atlanmaz.) Zamanlama: bir sonraki kartın başlamasına ~1s kala biten aralıklarla (`start + hold ≈ sonraki kartın data-start'ı`), video boyunca dengeli dağıtılmış.
- B-roll **max 2×8s** — **kullanıcı ekler** (dashboard drop); agent sadece keyword + start. Whip + whoosh, PIP sol.
- **B-roll zamanlaması (KİLİT — 2026-09, kullanıcı geri bildirimi):** hiçbir b-roll ilk sırada/açılışta gelmez — ilk b-roll'un `start` değeri **en az 20.0s** olmalı. Videonun ilk 20 saniyesi (kartsız 10s dahil) tamamen konuşmacıda kalır.
- **B-roll kaynağı (KİLİT — 2026-09, güncellendi: ZSky API/MCP ücretli Max plan istiyor, kullanıcı istemedi — o yol iptal):** iki yol var — (1) Google Labs, elle indir/sürükle (eski yol, `videos/<id>/public/broll/LABS_PROMPTS.md`); (2) **ZSky web (ücretsiz, elle)** — zsky.ai'de giriş yapılı ücretsiz hesapla site üzerinden ~5sn klip üretilir, elle indirilir, agent'a verilir; agent `scripts/prep_zsky_broll.py` ile ping-pong (ileri+ters, 8sn'e kırp) yöntemiyle sabit **8sn** kuralına uzatır — sert stream-loop atlaması yerine yön değiştiren yumuşak bir dönüş noktası verir. Çıktı yine `public/broll/<slot>.mp4`'e yazılır, geri kalan encode/crop/PIP kuralları aynı kalır. API/MCP otomasyonu YOK (ücretli Max abonelik + manuel onay gerektiriyor, kullanılmıyor). Pictory şimdilik değerlendirme dışı.
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

### Tip-explainer (`timeline.tipScenes`) — opsiyonel
Max **2** sahne. Default: konuşmacı **tam ekran blur**, üstte örnek kart ~**3s** gelir geçer (`halfPip: false`).
Eski yarım ekran için `halfPip: true`. Kind: `nodes` | `social` | `branches`.
Yüzde `sparks` MG parıltı **kullanma**.

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
