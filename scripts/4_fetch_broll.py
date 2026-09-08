"""
Konuya uygun ÜCRETSİZ b-roll videosu çeker (Pexels API, yedek olarak Pixabay).

KURULUM (bir kereye mahsus):
1. https://www.pexels.com/api/  -> ücretsiz hesap aç, API key al
2. https://pixabay.com/api/docs/ -> ücretsiz hesap aç, API key al (yedek kaynak)
3. Bu iki key'i ortam değişkeni olarak ayarla (PowerShell):
   setx PEXELS_API_KEY "senin_key_in"
   setx PIXABAY_API_KEY "senin_key_in"
   (setx sonrası yeni bir PowerShell penceresi aç ki değişken görünsün)

KULLANIM:
   python 4_fetch_broll.py "altın külçe" --out broll_altin.mp4 --min-duration 8
   python 4_fetch_broll.py "borsa ekranı" --out broll_borsa.mp4
"""
import os, sys, argparse, requests

PEXELS_KEY = os.environ.get("PEXELS_API_KEY")
PIXABAY_KEY = os.environ.get("PIXABAY_API_KEY")

def search_pexels(query, min_duration=6):
    if not PEXELS_KEY:
        return None
    url = "https://api.pexels.com/videos/search"
    headers = {"Authorization": PEXELS_KEY}
    params = {"query": query, "orientation": "portrait", "per_page": 10}
    r = requests.get(url, headers=headers, params=params, timeout=20)
    r.raise_for_status()
    data = r.json()
    for video in data.get("videos", []):
        if video.get("duration", 0) >= min_duration:
            # pick the highest-resolution portrait file
            files = sorted(video["video_files"], key=lambda f: f.get("width", 0), reverse=True)
            for f in files:
                if f.get("width") and f["width"] <= 1920:
                    return f["link"]
    return None

def search_pixabay(query, min_duration=6):
    if not PIXABAY_KEY:
        return None
    url = "https://pixabay.com/api/videos/"
    params = {"key": PIXABAY_KEY, "q": query, "video_type": "film", "per_page": 10}
    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    data = r.json()
    for hit in data.get("hits", []):
        if hit.get("duration", 0) >= min_duration:
            videos = hit["videos"]
            # prefer 'medium' or 'large' size for reasonable file size
            for size in ["medium", "large", "small"]:
                if size in videos:
                    return videos[size]["url"]
    return None

def download(url, out_path):
    r = requests.get(url, stream=True, timeout=60)
    r.raise_for_status()
    with open(out_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query", help="Konu anahtar kelimesi, örn: 'altın külçe', 'borsa ekranı'")
    ap.add_argument("--out", required=True)
    ap.add_argument("--min-duration", type=int, default=6)
    args = ap.parse_args()

    url = search_pexels(args.query, args.min_duration)
    source = "Pexels"
    if not url:
        url = search_pixabay(args.query, args.min_duration)
        source = "Pixabay"
    if not url:
        print(f"UYARI: '{args.query}' için uygun video bulunamadı (Pexels+Pixabay). "
              f"Farklı bir anahtar kelime dene veya API key'lerini kontrol et.")
        sys.exit(1)

    print(f"{source}'ten indiriliyor: {url}")
    download(url, args.out)
    print(f"Kaydedildi: {args.out}")

if __name__ == "__main__":
    main()
