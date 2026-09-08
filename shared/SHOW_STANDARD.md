# Nihat show standard (KİLİTLİ)

Her yeni video: **aynı motor** (look / anim / SFX / geçiş) + **sadece bu konunun** yazıları, kart kopyası, b-roll, punch zamanı.

Format: **9:16 · 1080×1920 · yüz önde · üstte kart boşluğu · altyazı · ses**.

---

## A) Her videoda zorunlu

### Çerçeve
- Talking-head full-bleed, sesli, tek VO.
- Üst bant kartlar (~y 120–600); orta yüz/punch; alt Anton altyazı (~y 1208).
- **Full-frame karartma yok.** Sağ ~120px IG rail boş. PIP **sol**. Kart max ~920px.

### Altyazı
- Anton 3D; üst beyaz, alt ton (Nihat sarı/kırmızı/yeşil).
- **Keyword pop** (`.cap-kw`): sayı / faiz / altın / risk vb. scale+brightness.
- Metin sadece editor transcript’inden.

### Kartlar (şeffaf cam — siyah kutu yok)
- `rgba` cam + text-shadow; punch kartlarda hafif kırmızı tint.
- **Her kart farklı enter** (havuzdan unique):  
  `slam | soft | glitch | tilt | wipe | pop | rise | flip | snap | drift | zoom | fold`
- Exit: fade / scale / slide (enter’a göre).
- Hold’da **progress** (hafif drift / tilt / scale).
- Video başına **1 hero 3D** (`timeline.hero`).
- Disclaimer: şeffaf, ortalı **YATIRIM TAVSİYESİ DEĞİL**, alt (~y 1580), NİHAT yok.
- Kopya: **sadece bu transcript**; 0907 faiz/CDS metni kopyalanmaz.

### Punch / B-roll / IG / SFX
- Punch 3–5, hold 6–10s, scale 1.10–1.16, click+sub-hit.
- B-roll **max 2×8s**, whip + whoosh, PIP sol. Labs prompt dosyası.
- IG PNG 2.3s, exclusive, swoosh-up.
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
