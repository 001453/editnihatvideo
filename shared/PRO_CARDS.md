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
| `mk-scene-break` | **Tam ekran (1080×1920) sahne kesme** — konuşan kişi tamamen kaybolur, adım-adım tablo (başlık kartı + rozet + noktalı bağlantı çizgisi + 2 veri satırı + dipnot) | Videonun en güçlü/karşılaştırmalı istatistik anları — **her videoda ZORUNLU 2 tane** (bkz. aşağıdaki Kural) |

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

## Kural — her videoda `mk-scene-break` (ZORUNLU, KİLİT — 2026-09, sayı güncellendi 2026-10)

Rakip hesaptaki (@eemrebayirrr) "konuşmacı kaybolup tam ekran adım-adım tablo" sahnesi
kanıtlanmış işleyen mekanizmayla eklendi. **Standart paket: her videoda konuya özel içerikle
2 tane `mk-scene-break`** (önceki kural "en az 1" idi — 2026-10'da 2'ye çıkarıldı, videonun
iki güçlü karşılaştırma/istatistik anına yerleştirilir, ör. biri ortada bir senaryo karşılaştırması
— "rapor güçlü/zayıf gelirse" — biri videonun ana eşik/karar anında — "X seviyesi üstünde/altında").
`timeline.json` → `proCards[]` içine iki ayrı `"block":"mk-scene-break"` girdisi olarak eklenir
(aşağıdaki JSON örneğine bak, `id` her biri için farklı olmalı). Her video için `heading` /
`headingValue` / `badge` / `rows[]` / `footnote` o videonun KENDİ konusuna göre yeniden yazılır —
asla önceki videodan kopya bırakılmaz. İki pro kart birbiriyle de çakışmamalı, aralarında en az
birkaç saniye boşluk bırak.

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

Yeni video paketlerken skill: **4 normal klasik kart** (bu listeden konuya uyan çeşitler) +
**2 adet `mk-scene-break`** (zorunlu, konuya özel, birbirleriyle ve broll/IG banner/normal
kartlarla zaman çakışması olmadan).
