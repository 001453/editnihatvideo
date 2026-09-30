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
| `mk-scene-break` | **Tam ekran (1080×1920) sahne kesme** — konuşan kişi tamamen kaybolur, adım-adım tablo (başlık kartı + rozet + noktalı bağlantı çizgisi + 2 veri satırı + dipnot) | Videonun en güçlü/karşılaştırmalı istatistik anı — **her videoda ZORUNLU en az 1 tane** (bkz. aşağıdaki Kural) |

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

1. Video başına **1–3** pro kart (fazlası kalabalık).
2. Kalan beat’ler klasik glass (hook / chips / stats / punch).
3. Metin **transcript’ten**; İngilizce demo metin bırakma.
4. 9:16 üst bant (~y 120–600); altyazı bandına binme.
5. IG / b-roll exclusive pencerelerine koyma.
6. Liquid Glass / iOS Home / full-screen VFX **yasak** (yüz + Anton bozulur).

## Kural — her videoda `mk-scene-break` (ZORUNLU, KİLİT — 2026-09)

Rakip hesaptaki (@eemrebayirrr) "konuşmacı kaybolup tam ekran adım-adım tablo" sahnesi
kanıtlanmış işleyen mekanizmayla eklendi: **her videoda konuya özel içerikle en az 1 tane**,
videonun en güçlü karşılaştırma/istatistik anına yerleştirilir (ör. "zirveden kayıp",
"950 milyar dolarlık yeni pazar", "1.400+ kurum girdi"). `timeline.json` → `proCards[]`
içine `"block":"mk-scene-break"` girdisi olarak eklenir (aşağıdaki JSON örneğine bak).
Her video için `heading` / `headingValue` / `badge` / `rows[]` / `footnote` o videonun
KENDİ konusuna göre yeniden yazılır — asla önceki videodan kopya bırakılmaz.

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

Yeni video paketlerken skill: klasik kartlar + bu listeden **konuya uyan 1–3** çeşit +
**1 adet `mk-scene-break`** (zorunlu, konuya özel).
