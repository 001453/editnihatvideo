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

### Bu 5'i nereden geldi

Emre Bayır (@eemrebayirrr) stil incelemesinden uyarlandı: bronz 3D numaralı rozet kartları,
yüzen 3D ikon objeleri (broll yoksa), sahte UI/app widget kartları, glow alt çizgili hero
kartı ve veri sahnelerinde duran küçük italik not. Onun kırmızı-parlama başlık + arkaplan
vignette/blur stili **alınmadı** — kilitli `videoGrade.legibilityOverlay:false` / no-blur
kuralıyla çakışıyor, ayrı onay gerekir. Bunların hepsi sadece kart gövdesi/rozet/ikon dili;
yüzü örtmüyor, glow tamamen kart içinde (küçük bir çizgi/obje üstünde), sayfa geneli
karartma yok.

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
  }
]
```

Build: `build_composition.py` registry bloğunu `compositions/` altına bağlar.

Yeni video paketlerken skill: klasik kartlar + bu listeden **konuya uyan 1–3** çeşit.
