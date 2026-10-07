# Profesyonel kart çeşitleri (HyperFrames registry)

Altyazı motoru **kilitli** (Montserrat Black social-hook, 2 satır). Kartlarda çeşit için bu paket kullanılır — her videoda **hep aynı cam kart** olmasın diye.

## Dashboard’daki sekmeler

| Sekme | Bizim iş |
| --- | --- |
| Captions | Altyazı stilleri — **kullanma** (Montserrat kilit) |
| VFX / Liquid Glass | Yüzü örten WebGL — **kullanma** |
| Data / Effects | Sayı, grafik, count-up — **evet** |
| Social / lower-third | İsim / başlık bar — **seçici** |
| Transitions / Scene | Tam sahne — genelde hayır |

## Kurulu paket (`shared/registry/`)

| ID | Ne | Ne zaman |
| --- | --- | --- |
| `mk-progress-stat` | Büyük sayı + progress bar | KAP / getiri / milyar |
| `data-chart` | Veri grafiği | seviye / oran anlatımı |
| `animated-bar-chart` | Bar animasyonu | karşılaştırma (%31→%59) |
| `chart-story` | Grafik hikâye | kısa trend |
| `number-wheel` | Sayı çarkı | tek hero sayı |
| `mk-callout-highlight` | Vurgu / sweep | cümle vurgusu |
| `lt-dark-card` | Koyu lower-third kart | bölüm başlığı |
| `lt-kicker-name` | Kicker + isim | “PEKİ NEDEN” tipi |
| `mk-badge-stat` | Bronz/altın 3D rozet + sayı/metin | tarihsel emsal, “sadece N defa”, sıralı olgu |
| `mk-widget-glow` | Koyu finans widget kartı, ikon + glow alt çizgi | hedef fiyat / tek hero rakam vurgusu |
| `mk-float-icon` | Yüzen altın/amber 3D obje (coin/chart/vault/goldbar) | gerçek broll yoksa, konuya uyan an (fiyat→coin, güvenli liman→vault, külçe→goldbar, trend→chart) |
| `mk-app-mockup` | Sahte hesap kartı / app widget (`variant:"card"` veya `"app"`) | “hesabım”, bakiye, %değişim anlatılan an |
| `mk-mini-disclaimer` | Küçük italik not, kart bandının dışında sürekli durabilir | simülasyon/veri sahnesinde ek uyarı (bitiş bannerinin yerine değil, ek) |
| `mk-scene-break` (+4 varyasyon) | **Tam ekran (1080×1920) sahne kesme** — konuşan kişi tamamen kaybolur. **5 görsel varyasyon havuzu** (KİLİT, 2026-10): `mk-scene-break` (classic — başlık kartı+rozet+noktalı çizgi+2 satır dikey liste), `mk-scene-break-split` (sol panel ikon+ana rakam / sağ panel 2 kutu liste), `mk-scene-break-ticker` (üstte rozet, ortada BÜYÜK tek rakam, altta 2 kutu yan yana), `mk-scene-break-grid` (2 kart yan yana, scoreboard), `mk-scene-break-pulse` (ortada pulse/radar halkalı ikon, altta dikey liste). Hepsi AYNI `copy` şemasını kullanır (`accent/icon/heading/headingValue/badge/rows[{label,value}]/footnote`) — sadece `block` adı değişir. | Videonun en güçlü/karşılaştırmalı istatistik anları — **her videoda ZORUNLU 2 tane, farklı varyasyon** (bkz. aşağıdaki Kural) |

### Bu 5'i nereden geldi

Emre Bayır (@eemrebayirrr) stil incelemesinden uyarlandı: bronz 3D numaralı rozet kartları,
yüzen 3D ikon objeleri (broll yoksa), sahte UI/app widget kartları, glow alt çizgili hero
kartı ve veri sahnelerinde duran küçük italik not. Onun kırmızı-parlama başlık + arkaplan
vignette/blur stili **alınmadı** — kilitli `videoGrade.legibilityOverlay:false` / no-blur
kuralıyla çakışıyor, ayrı onay gerekir. Bunların hepsi sadece kart gövdesi/rozet/ikon dili;
yüzü örtmüyor, glow tamamen kart içinde (küçük bir çizgi/obje üstünde), sayfa geneli
karartma yok. `mk-scene-break` istisna: o bilinçli olarak TAM SAHNE — konuyu tablo halinde
adım adım anlatan aynı hesaptaki "sert kesim" grafiği örnek alındı.

`mk-float-icon`: broll YERİNE değil, broll YOKSA kullan — ikon konuya uygun olmalı (`coin`
fiyat anı, `goldbar` fiziksel külçe anı, `vault` güvenli-liman/risk anı, `chart` trend anı).
Emre'nin gear/uçak/ev gibi genel ikonları burada yok — hepsi finans/altın temalı.

`mk-mini-disclaimer`: outer `scale:1` ile kullan (iç `x:0,y:0` sabit — metin kendi doğal
boyutunda kalır), outer `x:40,y:1520` civarı önerilir (bitiş bannerinin biraz üstü, altyazı
bandına binmez). Bitiş bannerinin (`YATIRIM TAVSİYESİ DEĞİL`) yerine geçmez, ona ek.

## Kural — 4 normal kartın 2'si de pro-tarz + her videoda FARKLI yerleşim (KİLİT, 2026-10-06, kullanıcı isteği)

Yeni projelerden itibaren: 4 "normal" kartın **2'si klasik glass stats** kalır, **diğer 2'si pro registry bloğu**
olur (`mk-progress-stat`, `number-wheel`, `animated-bar-chart`, `mk-callout-highlight` vb.; alttaki 2 sahne-geçişi
pro kartı AYRI, onlara dokunma). Bu 2 pro-tarz kartın **yerleşimi/hareketi her videoda farklı** seçilir ve bir önceki
videoyla aynı olmaz: bazen **dikey, uygun boş alanda** (alt yarıda dikey yığın/çubuk/adım), bazen **akan** (ticker/marquee
şeridi, soldan sağa akış). Aynı videoda ikisi aynı yerleşimde olmaz. Konum ayarı altyazı sayfasındaki
"📍 Kart konumu" bölümünden yapılır (`/api/card-layout`), Studio sürüklemesi kullanılmaz.
Takip: 1006 → klasik 4 kart (bu kuraldan ÖNCE paketlendi). 1007: dikey = `mk-vert-stat` (CONFIG: accent,badge,heading,headingValue,rows[],footnote,posX,posY — dar sütun, varsayılan sağ kenar x700,y430), akan = `mk-flow-ticker` (CONFIG: accent,label,entries[{label,value}],posY — sağdan sola akan şerit, varsayılan y1330). Yeni video: bir öncekiyle aynı yerleşimi kullanma (dikey için posX sol/sağ, y değiştir).

## Kural (show)

1. Video başına **standart 4 normal kart + 2 pro kart** (bkz. aşağıdaki Kural — toplam
   sayı/denge; istisnai durumda 1–3 pro karta kadar esner ama varsayılan 2).
2. Kalan beat’ler klasik glass (hook / chips / stats / punch).
3. Metin **transcript’ten**; İngilizce demo metin bırakma.
4. 9:16 üst bant (~y 120–600); altyazı bandına binme.
5. IG / b-roll exclusive pencerelerine koyma.
6. Liquid Glass / iOS Home / full-screen VFX **yasak** (yüz + Anton bozulur).
7. **Zaman çakışması yasak** (KİLİT — 2026-10): pro kart TAM EKRAN olduğu için (`mk-scene-break`
   vb.) o pencere içinde çalışan hiçbir normal kart / b-roll / IG banner olmamalı — hepsi görünmez
   şekilde pro kartın altında kalır ve boşa gider. Pro kartları zaman çizelgesine yerleştirirken
   önce `timeline.json`'daki `broll[]` ve `igBanner[]` pencereleriyle, sonra `cards.html`'deki
   normal kart `data-start`/`data-duration` aralıklarıyla çakışmadığını kontrol et. (Normal kart +
   b-roll aynı anda olması sorun değil — o zaten standart kombinasyon; yasak olan pro-kart'ın
   başka bir şeyle çakışması.)

## Kural — her videoda `mk-scene-break` (ZORUNLU, KİLİT — 2026-09, sayı güncellendi 2026-10, varyasyon havuzu eklendi 2026-10)

Rakip hesaptaki (@eemrebayirrr) "konuşmacı kaybolup tam ekran adım-adım tablo" sahnesi
kanıtlanmış işleyen mekanizmayla eklendi. **Standart paket: her videoda konuya özel içerikle
2 tane sahne kesme kartı** (önceki kural "en az 1" idi — 2026-10'da 2'ye çıkarıldı, videonun
iki güçlü karşılaştırma/istatistik anına yerleştirilir, ör. biri ortada bir senaryo karşılaştırması
— "rapor güçlü/zayıf gelirse" — biri videonun ana eşik/karar anında — "X seviyesi üstünde/altında").

**Varyasyon havuzu (KİLİT, 2026-10 — "her videoda farklı izlenim" talebi):** 5 görsel stil var —
`mk-scene-break` (classic), `mk-scene-break-split`, `mk-scene-break-ticker`, `mk-scene-break-grid`,
`mk-scene-break-pulse`. Her 5'i de **birebir aynı kritik mekanizmayı** taşır (aşağıdaki
"Mekanizma" bölümü, visibility-gating + epsilon-timing fix) — sadece iç görsel düzen farklı.
Kural: **bir videodaki 2 pro kart birbirinden FARKLI varyasyon olmalı** (asla aynı videoda 2x
aynı stil), ve ardışık videolar da mümkünse farklı çift kullansın (ör. video A: classic+grid,
video B: split+ticker, video C: pulse+classic, ...) — amaç izleyiciye her videoda farklı bir
görsel izlenim vermek. Hangi varyasyon hangi içerik şekline uyuyor (kaba rehber):
- **classic** → tek başlık + dikey 2 satır karşılaştırma (genel amaçlı, varsayılan)
- **split** → "2 koz / 2 avantaj" gibi sol=özet-sağ=liste ayrımı olan içerik
- **ticker** → tek büyük rakam/fiyat vurgusu + altında 2 kutu sonuç (eşik/hedef fiyat anları)
- **grid** → 2 seçeneği yan yana kart olarak göstermek (örnek vaka / senaryo karşılaştırması)
- **pulse** → dramatik/"dikkat" anı, tek ikon merkezde, altında liste (risk/alarm temalı)

Her varyasyon zaten ekranda FARKLI bir **alanı** kaplıyor (sadece renk değil, yerleşim de
değişsin istendi — 2026-10): classic içerik üstte-ortada (y~220-800) dikey akar, split
tam-boy sol/sağ ikiye böler, ticker ortada-üstte (y~200-950) büyük rakamla ortalar, grid
üstte-ortada (y~250-950) yan yana kartlar, pulse ortada (y~420-1250) halka+liste. Çift
seçerken bu yüzden sadece "stil" değil "alan" da değişsin — ör. split (tam-boy) ile pulse
(orta-blok) aynı videoda yan yana güzel kontrast olur.


**Havuz 8 varyasyona genişletti (2026-10-05, "en az 7 farklı tasarım" isteği):** önceki 5'e (classic/split/ticker/grid/pulse) ek olarak 3 yeni — aynı `CONFIG` alanları (`accent,icon,heading,headingValue,badge,rows[],footnote`), aynı visibility-hidden mekanizması, sadece iç tasarım farklı:
- `mk-scene-break-vs` → iki dev dikey sütun + ortada VS dairesi (tam boy y~300-1300). Gerçek KARŞILAŞTIRMA için (A vs B, önce/sonra).
- `mk-scene-break-stack` → içerik ALT yarıda (y~700-1500): dev değer + yatay çubuk satırlar. "Şartlar / maddeler" için.
- `mk-scene-break-steps` → sol dikey çizgi + numaralı adımlar (1 → 2), sol hizalı. Senaryo / sebep-sonuç akışı için.
Seçim kuralı aynı: videodaki 2 pro kart FARKLI varyasyon, bir önceki videonun çiftini tekrarlama.

**Hangi video hangi çifti kullandı (tekrar etmeyelim diye takip listesi):**
- 1002: grid + ticker
- 1003: split + pulse
- 1004: özel rank-board videosu (pro-card çifti yok)
- 1005: steps + stack (yeni havuz)
- 1006: vs + classic
- 1007: grid + split (sahne geçişi) · normal kart pro-tarz: `mk-vert-stat` (dikey, sağ kenar) + `mk-flow-ticker` (akan şerit)
- (yeni video paketlerken buraya eklenecek satır — bir önceki videonun çiftiyle AYNI ikiliyi
  kullanma, mümkünse hiç kesişmeyen bir çift seç, ör. 1004 → classic + split değil de
  classic + ticker gibi en az biri önceki çiftte olmayan bir kombinasyon.)

`timeline.json` → `proCards[]` içine iki ayrı girdi olarak eklenir, her birinin `"block"` alanı
yukarıdaki 5'ten FARKLI ikisi seçilir (aşağıdaki JSON örneğine bak, `id` her biri için de farklı
olmalı). Her video için `heading` / `headingValue` / `badge` / `rows[]` / `footnote` o videonun
KENDİ konusuna göre yeniden yazılır — asla önceki videodan kopya bırakılmaz. İki pro kart
birbiriyle de çakışmamalı, aralarında en az birkaç saniye boşluk bırak.

**Mekanizma (KANITLANMIŞ, 2026-09 — ekranda doğrulandı):**
- Registry dosyası (`shared/registry/compositions/mk-scene-break.html`) kendi kök
  elemanında `data-width="1080" data-height="1920"` bildiriyor (gerçek dikey video
  kanvasıyla birebir — eski 1920×1080 "iç sahne" yaklaşımı Stüdyo'da sadece sol-üst
  1080×1080 karesini gösteriyordu, tam ekran olmuyordu).
- `build_engine.py → pro_cards_html()` bu bildirimi otomatik algılayıp `mk-app-mockup`
  gibi 1920×1080 kartların kullandığı `pro-card` yerine, "Takip Et" rozetinde kanıtlanmış
  `ig-follow-host` mekanizmasıyla monte ediyor.
- Registry dosyasının içinde, asıl görünür içerik `class="clip"` ile işaretli bir sarmalayıcı
  içinde olmalı (bkz. `instagram-follow.html` `#card` deseni) — bu işaret olmadan Stüdyo
  canlı önizlemede içerik hiç boyanmıyor (2026-09'da tespit edilen kök sebep).
- `rows[]` gibi dizi/nesne `copy` alanları `_patch_pro_config()` tarafından artık doğru
  patch'leniyor (eskiden sessizce atlanıp bir önceki videonun sabit verisi kalıyordu —
  düzeltildi, 2026-09).
- **KİLİT (2026-10, KÖK SEBEP — "görselim yok, scene kartından sonra düzeliyor" hatası):**
  `#mk-sb-root` opak bir arkaplan taşıyan tam-ekran bir div; eskiden varsayılan olarak
  `visibility:visible`'dı. Sayfa yüklenir yüklenmez bu div DOM'da duruyordu ve Stüdyo onu
  kendi `[data-start, data-duration]` penceresinde henüz sürmemiş (play/seek etmemiş)
  olsa bile ekranı — ve altındaki `#video-wrap`'ı (konuşmacı videosu) — **videonun BAŞINDAN
  İTİBAREN kaplıyordu**. Sadece kompozisyonun KENDİ iç GSAP timeline'ı bir kere oynatılıp
  sonuna gelince (`tl.set(root,{visibility:"hidden"}, DUR-0.02)`) gizleniyordu — yani
  "scene kartı bir kere girip çıktıktan sonra görselim geri geliyor" davranışı tam olarak
  buradan kaynaklanıyordu. **Düzeltme:** `#mk-sb-root` artık CSS'te `visibility:hidden` ile
  başlıyor, kendi timeline'ının en başında (`tl.set(root,{visibility:"visible"}, 0)`)
  görünür oluyor, sonunda yine gizleniyor — yani sadece kendi aktif penceresinde görünür.
  IG takip banner'ında (`instagram-follow-*.html`) bu sorun hiç yoktu çünkü onun kökü
  şeffaf (`background:transparent`), sadece küçük bir rozet taşıyor — opak tam-ekran
  arkaplanı olan YENİ bir `ig-follow-host` bloğu yazılırsa aynı `visibility:hidden` /
  `tl.set(...,0)` deseni mutlaka uygulanmalı.

## Agent nasıl kullanır

`timeline.json`:

```json
"proCards": [
  {
    "id": "kap-stat",
    "block": "mk-progress-stat",
    "start": 64.6,
    "dur": 7.0,
    "copy": {"value": 2.18, "suffix": "", "label": "MİLYAR TL", "caption": "KAP · 31 AĞUSTOS 2026", "max": 3}
  },
  {
    "id": "scene-ornek",
    "block": "mk-scene-break",
    "start": 40.5,
    "dur": 8.0,
    "copy": {
      "accent": "#f0b429",
      "icon": "📈",
      "heading": "KONU BAŞLIĞI",
      "headingValue": "ANA RAKAM",
      "badge": "KISA VURGU",
      "rows": [
        {"label": "Satır 1 etiketi", "value": "Satır 1 değeri"},
        {"label": "Satır 2 etiketi", "value": "Satır 2 değeri"}
      ],
      "footnote": "ÖRNEK VERİDİR. YATIRIM TAVSİYESİ DEĞİLDİR."
    }
  }
]
```

Build: `build_composition.py` registry bloğunu `compositions/` altına bağlar.

## `mk-rank-board` — Özel format: "10'lu sıralama" videoları (KİLİT, 2026-10)

Standart 4+2 kart akışına uymayan, "N hisseyi/ürünü sıralıyoruz" tipi tek seferlik liste
videoları için. Kök şeffaf (`background:transparent`) — `mk-scene-break` gibi tam-ekran
opak DEĞİL, konuşan kişi hiç kapanmaz, visibility-gating fix'ine gerek yok.

**Konum:** ÜST alanda, proje banner'ının (y:220-340) ALTINDA küçük/kompakt tek sıra 10 halka
(y~368-538) — alt-bant 5x2 ızgara DEĞİL, "üst alanda küçük bir sıralama".

**Bu format videosunda BROLL KULLANILMAZ (KİLİT, 2026-10):** konuşan kişi baştan sona
sürekli ekranda kalıyor (b-roll ile kesilmiyor) — `timeline.json` → `broll: []` boş
bırakılır, `brollPending` da yazılmaz.

**V5 — 3 AŞAMALI AKIŞ: GÖĞÜS AÇILIŞ → KENARA KAYMA → DOCK (KİLİT, 2026-10):** Büyük açılış
üst sıradaki slotun kendi üstünde DEĞİL, ayrı bir "hero" katmanında olur, 3 aşamalı:
(1) **`at` anında** hero GÖĞÜS HİZASINDA (`#mk-rb-hero`, merkez `CONFIG.heroX/heroY`, varsayılan
540/1120) büyük belirir — logo (`logo` varsa) veya rank numarası + tam isim (`fullName`, ör.
"TOFAŞ"); konuşmacı bu anda hareketsiz bekler. (2) **`at + CONFIG.introHold` saniye sonra**
(varsayılan 0.9sn, konuşmacı anlatmaya başlayınca) hero KENARA kayıp küçülür (`CONFIG.sideX/
sideY`, varsayılan 150/1120 — sol kenar, aynı yükseklik), isim etiketi kaybolur — konuşmacının
yüzünü/vücudunu kapatmaz, sadece küçük bir hatırlatıcı olarak kenarda bekler. (3) **`dockAt`
anında** ("...X numara" diyerek bitince) hero kenardan üst sıradaki kendi slotuna uçar (slotların
ekran koordinatı sayfa yüklenirken bir kere ölçülüp hedef alınıyor — layout statik olduğu için
güvenli), slot `revealed` class alır (rank 1 ekstra nabız atışıyla). Kenar bekleme ölçeği slotun
kendi ölçeğiyle AYNI (94/220) tutuluyor — son uçuşta ek büyüklük sıçraması olmasın diye.
`heroX/heroY/sideX/sideY/introHold` görsel konum/zamanlama tutmazsa SADECE bu sayılar
güncellenir, kod değişmez. Video süresince `proCards[]`'a `"block":"mk-rank-board"` olarak
eklenir, `start:0`, `dur:<videonun süresi>`. `copy`:
```json
{
  "accent": "#f0b429",
  "title": "SIRALAMA BAŞLIĞI",
  "fadeOutAt": 999,
  "heroX": 540,
  "heroY": 1120,
  "sideX": 150,
  "sideY": 1120,
  "introHold": 0.9,
  "entries": [
    {"rank": 9, "ticker": "TOASO", "fullName": "TOFAŞ", "logo": "public/logos/TOASO.png", "at": 0.0, "dockAt": 7.26},
    {"rank": 1, "ticker": "PAGYO", "fullName": "PANORA GYO", "logo": "public/logos/PAGYO.png", "at": 108.44, "dockAt": 123.62}
  ]
}
```
`entries[].at` = BÜYÜK açılışın başladığı GERÇEK video saniyesi (transkript segment-başı —
konuşmacı o hisseden bahsetmeye başladığı an). `entries[].dockAt` = konuşmanın "...X numara"
diyerek BİTTİĞİ an (halka küçülüp slotuna akar) — eski V1'in tek `at` alanı artık `dockAt`'a
denk gelir. Board `start:0` ile monte edildiği için local time = global video time, direkt
transkript saniyesi yazılır. Halkalar ekranda sabit 10→1 sırayla (soldan sağa) dizilir (1
numara en sağda, "final" hissi için).
**Logo dosya kuralı (KİLİT):** `entries[].logo` = KÖK-GÖRELİ yol `public/logos/<TICKER>.png`
(ASLA `../public/...` — Stüdyo `../` ile proje kökünün DIŞINA çıkıp 404 verir). Kullanıcı
logoları broll gibi kendisi sağlayacak — dosya adı ticker ile eşleşmeli (ör. `TOASO.png`).
Logo dosyası henüz yoksa/yüklenemezse `<img onerror>` otomatik rank numarasına düşer, akış
bozulmaz — logo dosyaları eklenmeden de timeline.json'da yol önceden yazılabilir.
`fadeOutAt`: disclaimer bannerından biraz önce (board kaybolsun, banner çakışmasın); yoksa 999.
**UYARI:** CONFIG alan adı `entries` (eski ad `items` CSS `align-items` ile çakışıp
patch'lenmiyordu — KİLİT, bu yüzden yeni registry bileşenlerinde CSS property'leriyle
çakışabilecek kısa/genel kelimeler CONFIG alan adı olarak seçilmemeli).

Yeni video paketlerken skill: **4 normal klasik kart** (bu listeden konuya uyan çeşitler) +
**2 adet sahne kesme kartı, 5'li varyasyon havuzundan FARKLI iki `block` seçilerek** (zorunlu,
konuya özel, birbirleriyle ve broll/IG banner/normal kartlarla zaman çakışması olmadan).

## KİLİT DOĞRU AKIŞ (2026-10-06, 1007'de ekranda doğrulandı — Nihat: "her şey güzel")

Bu akış standarttır, bozma:
- 4 normal kartın 2'si klasik cam, 2'si pro-tarz (`mk-vert-stat` dikey boş alan, `mk-flow-ticker` çapraz akan kartlar — haber şeridi DEĞİL, Nihat beğenmedi).
- 2 zorunlu sahne kartı (`mk-scene-break-*`) tam ekran; konuşmacıyı kaplar.
- Tüm pro kök elemanları `position:absolute; left:0; top:0` (relative olursa Stüdyo'da alta kayar), her pro/sahne dosyasında `mk-sb` önekleri `build_engine` tarafından benzersiz yapılır (aynı id çakışması sahneleri bozuyordu).
- **Her videoda farklı tasarım döngüsü (10'lu):** `shared/pro_rotation.json` — video no % 10 → renk (accent) + dikey kart konumu + akan kart konumu. `build_engine._apply_rotation` bunu otomatik uygular; `timeline.json` `proCards[].copy` içinde elle verilen accent/posX/posY HER ZAMAN önceliklidir.
- Yeni videoda: sahne çiftini önceki videodakinden farklı seç, normal pro-tarz kartların konumunu rotasyondan al, ayrıca boş alana göre (yüz/altyazı üstü) gerekirse copy ile ez.
- Konum ince ayarı: altyazı sayfası "📍 Kart konumu" (pro kartlar `pro:<id>`).

## Katalogdan ilhamla yeni pro kartlar (2026-10-06, motorda render doğrulandı)
Üçü de şeffaf kök, `position:absolute`, `posX/posY/accent` alır; `timeline.json` `proCards[]` içinde `block` adıyla çağrılır:
- `mk-ring-stat` — sayarak gelen yüzde halkası. copy: `label, value(0-100), suffix, caption, posX, posY, accent`.
- `mk-line-graph` — çizilerek gelen fiyat çizgisi. copy: `label, last, points[], caption, posX, posY, accent`.
- `mk-hand-circle` — elle çizilmiş daire + ok + not (grafik/sayıyı işaretler). copy: `note, posX, posY (daire merkezi), boxW, boxH, accent`.
Normal 4 kartın pro-tarz olan 2'si için `mk-vert-stat`, `mk-flow-ticker` ile birlikte bu üçü de havuzdadır; videoda farklı olanı seç.

## KİLİT — kartlar transkripte göre yerleştirilir (2026-10-06, Nihat onayı)
Pro kart / sahne / halka / çizgi grafik / el çizimi daire eklenirken zaman ve içerik RASTGELE seçilmez:
- `transcripts/input-video.json` kelime zamanlarına bakılır; kart, konuşmacı o konuyu söylerken başlar (örn. "%30" denirken halka, seviyeler sayılırken çizgi grafik, vurgulanan kelimede el çizimi daire).
- Kartın metni/sayıları o anda konuşulanla birebir aynı olur; yeni videoda önceki videonun metni asla kalmaz.
- El çizimi daire altyazının vurgulanan kelimesini çevreler (posY ≈ altyazı bandı); kenarda taşmamalı.
- Konumlar: yüz ve altyazıyı kapatmayan boş alan; sahne kartları arası ve diğer kartlarla en az birkaç sn boşluk.

## Alt bant `mk-strip` (2026-10-06, adım 1) — haber şeridinin yerine
copy: `variant (neon|dark|pill), tag, entries[{label,value}], accent, posX, posY, barW`. Maddeler sırayla yer değiştirir (kayan şerit değil). Rotasyon: video no % 3 → variant, renk ve posY döngüden gelir. `mk-flow-ticker` ile birlikte "akış/bant" havuzudur.

## Sayı tabelası `mk-flap-board` (2026-10-06, adım 2)
Rakamlar tabela gibi dönerek yerine oturur. copy: `label, rows[{label,value(rakam string)}], unit, accent, posX, posY`. Seviye/destek/direnç sayıları konuşulurken kullanılır (transkripte göre).

## Parçalanma çıkışı + çarpma sesi (2026-10-06, Nihat isteği)
`mk-vert-stat, mk-flow-ticker, mk-ring-stat, mk-line-graph, mk-flap-board, mk-strip` kartları bitişte `shatter()` ile parçalanıp düşer (kart içinden klonlanan parçalar). Ses: `shared/sfx/shatter.mp3` — motor (`SHATTER_BLOCKS`) kartın bitişine (start+dur-0.95) otomatik ekler; kapatmak için copy'ye `"noShatter": true`. Kartın iç süresi `dur` ile eşitlenir (motor `var DUR`'u dur'a göre yazar), bu yüzden `dur` kısa olsa bile parçalanma görünür. Sahne kartları ve el çizimi daire parçalanmaz.

## KİLİT — kart anlatırken altyazı yok (2026-10-06, Nihat isteği)
Pro kart / sahne / halka / grafik / tabela / bant ekrandayken o saniyelerin altyazısı gösterilmez; kart bitince altyazı devam eder (`card_windows()` pro kartları da kapsar). Muaf: `mk-hand-circle` (altyazıyı işaretler) ve `copy.noCaptionPause: true`. Bu yüzden kartı konuşmanın o konuyu anlattığı kısa kesite yerleştir ve süresini gereksiz uzatma (genelde 4–6 sn).

## DÜZELTME (2026-10-06): `mk-hand-circle` (el çizimi daire) KULLANMA — Nihat beğenmedi, havuzdan çıkarıldı. Altyazı durdurma kuralında artık muaf kart yok (sadece copy.noCaptionPause:true ile tek tek).

## Karşılaştırma kartı `mk-compare` (2026-10-06, adım 3)
İki panel kenarlardan kayıp buluşur, ortada fark rozeti; bitişte parçalanır (ses otomatik). copy: `title, leftLabel, leftValue, rightLabel, rightValue, delta, posY, accent`. "Beklenti → açıklanan", "önceki → şimdi" gibi iki sayı konuşulurken, transkripte göre. Geniş (920px) olduğu için yüzü kapatmayan üst/alt boşluğa koy (posY ≈ 330 veya ≈ 1250).

## B-roll geçişleri döngüsü (2026-10-06, 1007'de onaylandı)
`build_engine._trans_js`: giriş {flash, whip, zoom, glitch} × çıkış {glitch, flash, whip, zoom}; seçim (video no + b-roll sırası) ile döner, aynı videoda b-roll'lar farklı çift alır. Parlama geçişleri `#trans-fx` beyaz katmanını ve kısık `sub-hit` sesini kullanır (sfx otomatik).

## YENİ (hepsi): hook, sahne varyantları, planlayıcı
- `mk-hook`: video açılış başlığı (0.1s, 3sn). Altyazıyı durdurmaz. copy: accent/kicker/title/hot/sub/posY.
- Yeni tam ekran sahneler: `mk-scene-break-bigstat` (dev sayı), `mk-scene-break-trio` (kademeli kartlar). Mevcut grid ile dönüşümlü kullan.
- Panel taşınabilir bloklar: vert-stat, flow-ticker, ring-stat, line-graph, flap-board, strip, compare, hook (dashboard_server PRO_MOVABLE).
- Planlayıcı: `python scripts/plan_cards.py <id>` → `videos/<id>/CARD_PLAN.json` (taslak öneri; etiketler paketlemede düzeltilir).
- OpenAI: anahtar varsa ve transcript'te `.openai` işareti yoksa eski transcript `input-video.eski-whisper.json` olur, OpenAI ile yeniden yapılır.

## YÜZ BÖLGESİ KURALI (2026-10-07, 1008 geri bildirimi)
Konuşmacının başı x≈400–790, y≈650–1100. Yan paneller (vert-stat, ring-stat, flap-board) SOLDA x=40 olmalı (en fazla x≈370'e kadar) ya da ÜST bantta (y+yükseklik ≤ ~640). Sağda x=700 sadece posY ≤ 240. Aynı video içinde paneller farklı yerlerde çıksın. Açılışta proje banner'ı (y220-340) zaten var → mk-hook KULLANMA (üst üste biniyor).
