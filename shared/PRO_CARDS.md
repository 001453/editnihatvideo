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
