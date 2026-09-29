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

**KİLİT (2026-09, güncellendi: Nano Banana MCP — pexels/pixabay stok siteleri finans/altın
temasına uygun içerik vermiyor, o yoldan vazgeçildi; b-roll yine Labs/manuel kalıyor. Görsel
üretimi için odak **Google Gemini "Nano Banana" MCP** (`.cursor/mcp.json` → `nanobanana`,
ücretsiz Google AI Studio key — günde ~500 görsel, ticari kullanım serbest, kart bilgisi
istemiyor):**

`mk-float-icon` isteğe bağlı `CONFIG.image` alanı destekliyor
(`shared/registry/compositions/mk-float-icon.html`) — set edilince CSS gradyan küre/bar yerine
gerçek üretilmiş bir PNG gösterir (aynı GSAP sway/in/out kalır, daha dar açıyla). Görseller
artık **Nano Banana MCP** (`generate_image` tool) ile agent tarafından **otomatik** üretilir —
elle indirme yok. Nano Banana native şeffaf PNG üretemiyor (RGB only, alpha yok), o yüzden 2
adımlı akış: (1) agent objeyi düz **yeşil (#00FF00) zemin** üzerinde ürettirir — prompt'ta
"transparent" kelimesi GEÇMEZ (Nano Banana bunu checkerboard desenine çeviriyor, işe yaramıyor);
(2) `scripts/prep_icon_bg.py <ham_png> shared/registry/assets/icon-<isim>.png` ile yeşil zemin
chroma-key ile şeffaflaştırılır (basit Pillow renk-anahtarı + kenar yumuşatma, ek model/indirme
gerektirmez). Örnek prompt: *"3D realistic glossy gold/amber [coin | bank vault door | stacked
gold bars | rising stock chart with amber glow], dramatic studio lighting, high detail, centered,
floating in empty space, solid pure green background (#00FF00), no text, no watermark, product
render style"*. Bunlar video-özel değil, show-locked ortak varlıklar: coin/vault/goldbar/chart
için birer kez üretilip `shared/registry/assets/icon-<isim>.png` altına kaydedilir ve her
videoda tekrar kullanılır (`instagram-follow.html`'in `assets/avatar.jpg`'i nasıl kullandığıyla
aynı desen). Yeni bir ikon tipi gerekmedikçe her videoda yeniden üretilmez — önce
`shared/registry/assets/` altında var mı diye bakılır. `timeline.json`'da
`proCards[].copy.image` alanına dosya adını yaz (örn. `"assets/icon-goldbar.png"`); boş
bırakılırsa eski CSS görünümüne düşer.

`mk-mini-disclaimer`: outer `scale:1` ile kullan (iç `x:0,y:0` sabit — metin kendi doğal
boyutunda kalır), outer `x:40,y:1520` civarı önerilir (bitiş bannerinin biraz üstü, altyazı
bandına binmez). Bitiş bannerinin (`YATIRIM TAVSİYESİ DEĞİL`) yerine geçmez, ona ek.

**KİLİT (2026-09, kullanıcı geri bildirimi):** Her videoda zaten zorunlu bir bitiş
disclaimer banner'ı var (`card-disclaimer`, "YATIRIM TAVSİYESİ DEĞİL"). `mk-mini-disclaimer`'ı
video başına seçilen 1-3 pro karttan biri olarak **kullanma** — aynı mesajı tekrarlamış
oluyor, tekrar kalabalık/gereksiz görünüyor. Bunun yerine konuya uygun başka bir çeşit seç
(`mk-float-icon`, `mk-app-mockup`, `mk-badge-stat`, `mk-widget-glow` vb.). `mk-mini-disclaimer`
sadece kullanıcı açıkça özellikle isterse (örn. gerçekten ayrı bir simülasyon/veri sahnesi
için ek uyarı istenirse) kullanılır, varsayılan rotasyonun parçası değildir.

## Kural (show)

1. Video başına **1–3** pro kart (fazlası kalabalık).
2. Kalan beat’ler klasik glass (hook / chips / stats / punch).
3. Metin **transcript’ten**; İngilizce demo metin bırakma.
4. 9:16 üst bant (~y 120–600); altyazı bandına binme.
5. IG / b-roll exclusive pencerelerine koyma.
6. Liquid Glass / iOS Home / full-screen VFX **yasak** (yüz + Anton bozulur).

## KİLİT (2026-09, görünmezlik düzeltmesi — ÖNEMLİ)

Registry blokları kendi içinde sabit **1920x1080 yatay** bir sahne varsayıyor;
kartın/ikonun asıl görünür konumu o sahnede `CONFIG.x`/`CONFIG.y` ile verilir.
Video ise **1080x1920 dikey**. Host artık ölçeksiz, sahnenin native boyutunda
(1920x1080, left:0/top:0) monte ediliyor — bu yüzden **her `proCards[]`
girdisinde `copy.x` ve `copy.y` MUTLAKA verilmeli**, doğrudan 1080 genişlikli
dikey çerçeveye göre (örn. `x:310` kartı yatayda ortalar, `y:120-600` arası üst
bant). Verilmezse registry'nin kendi varsayılanı (`x:~1300`) kullanılır ve kart
1080'lik çerçevenin tamamen dışına düşüp **görünmez** olur — 2026-09'da
0916/0918/0919/0927'de tam olarak bu yüzden kartlar ekranda hiç görünmüyordu
(kod hiç şikayet etmiyordu, Stüdyo dosyayı tanıyordu ama görsel kanvas dışında
kalıyordu). Ayrıca `_patch_pro_config` artık `\b` kelime-sınırı kullanıyor —
eskiden kısa anahtar adları ("x","y") "max:"/"opacity:" gibi başka alanların
içine yanlış eşleşip onları bozuyordu.

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
