# -*- coding: utf-8 -*-
"""Turkish caption text: proper uppercase (i→İ) + common ASR undotted fixes."""
from __future__ import annotations

import re

# ALL-CAPS ASR that lost Turkish diacritics (longer keys first via sort).
_ASR_FIXES = [
    ("MATEMATIKSEL", "MATEMATİKSEL"),
    ("YUKSELMESINDEN", "YÜKSELMESİNDEN"),
    ("DEGERLENDIRMIS", "DEĞERLENDİRMİŞ"),
    ("DEGERLENDIRMIŞ", "DEĞERLENDİRMİŞ"),
    ("SPEKULATIF", "SPEKÜLATİF"),
    ("HISSESENEDI", "HİSSE SENEDİ"),
    ("GETIRINCISI", "GETİRİCİSİ"),
    ("ITIBARIYLE", "İTİBARİYLE"),
    ("ITIBAREN", "İTİBAREN"),
    ("DOLASINDAKI", "DOLAŞIMDAKİ"),
    ("DOLAŞINDAKI", "DOLAŞIMDAKİ"),
    ("AGIRLIGININ", "AĞIRLIĞININ"),
    ("DUSMESIYLE", "DÜŞMESİYLE"),
    ("GOSTERIYOR", "GÖSTERİYOR"),
    ("GORUNUYOR", "GÖRÜNÜYOR"),
    ("HEDEFLIYOR", "HEDEFLİYOR"),
    ("YENITILIYOR", "YÖNETİLİYOR"),
    ("GOREBILIR", "GÖREBİLİR"),
    ("GETIRESINE", "GETİRİSİNE"),
    ("BAGISLARLA", "BAĞIŞLARLA"),
    ("PRENSIPLERINE", "PRENSİPLERİNE"),
    ("CIVARINDAYDI", "CİVARINDAYDI"),
    ("HASSASIYETI", "HASSASİYETİ"),
    ("ASASIYETI", "HASSASİYETİ"),
    ("YURTDISI", "YURTDIŞI"),
    ("YAKLASIK", "YAKLAŞIK"),
    ("SATTIGINA", "SATTIĞINA"),
    ("ACIKLAMA", "AÇIKLAMA"),
    ("KALDIGI", "KALDIĞI"),
    ("SAHIPLERINI", "SAHİPLERİNİ"),
    ("SAHİPLERINI", "SAHİPLERİNİ"),
    ("ICERIDE", "İÇERİDE"),
    ("ICERMEZ", "İÇERMEZ"),
    ("ICERIM", "İÇERMEZ"),
    ("URETMESINI", "ÜRETMESİNİ"),
    ("BASINDAN", "BAŞINDAN"),
    ("BUYUYOR", "BÜYÜYOR"),
    ("TURKIYE", "TÜRKİYE"),
    ("TÜRKIYE", "TÜRKİYE"),
    ("DIYANET", "DİYANET"),
    ("PORTWAY", "PORTFÖY"),
    ("PORTFOY", "PORTFÖY"),
    ("MILYONDAN", "MİLYONDAN"),
    ("MILYAR", "MİLYAR"),
    ("FIYATINI", "FİYATINI"),
    ("FIYATI", "FİYATI"),
    ("FIYAT", "FİYAT"),
    ("PIYASASI", "PİYASASI"),
    ("PIYASADA", "PİYASADA"),
    ("PIYASA", "PİYASA"),
    ("BENZERI", "BENZERİ"),
    ("TARIHLI", "TARİHLİ"),
    ("VERISINE", "VERİSİNE"),
    ("ONCEKI", "ÖNCEKİ"),
    ("ÖNCEKI", "ÖNCEKİ"),
    ("DONEMDE", "DÖNEMDE"),
    ("YENIDEN", "YENİDEN"),
    ("RISKLI", "RİSKLİ"),
    ("FAIZSIZ", "FAİZSİZ"),
    ("FAIZ", "FAİZ"),
    ("GETIRIR", "GETİRİ"),
    ("GETIRI", "GETİRİ"),
    ("LIKIT", "LİKİT"),
    ("BIRIM", "BİRİM"),
    ("ARTIS", "ARTIŞ"),
    ("DEGIL", "DEĞİL"),
    ("DEĞIL", "DEĞİL"),
    ("GIRINCE", "GİRİNCE"),
    ("AGUSTOS", "AĞUSTOS"),
    ("NAKTI", "NAKDİ"),
    ("BAGIS", "BAĞIŞ"),
    ("BAĞIS", "BAĞIŞ"),
    ("CAMII", "CAMİİ"),
    ("CAMİI", "CAMİİ"),
    ("MALI", "MALİ"),
    ("YERI", "YERİ"),
    ("HENUZ", "HENÜZ"),
    ("CIKAN", "ÇIKAN"),
    ("SURECE", "SÜRECE"),
    ("ALMIS", "ALMIŞ"),
    ("GIBI", "GİBİ"),
    ("GİBI", "GİBİ"),
    ("ICIN", "İÇİN"),
    ("IÇİN", "İÇİN"),
    ("TAKIP", "TAKİP"),
    ("LISTEM", "LİSTEM"),
    ("YUKSELDI", "YÜKSELDİ"),
    ("YÜKSELDI", "YÜKSELDİ"),
    ("ASMIŞTI", "AŞMIŞTI"),
]


def tr_upper(text: str) -> str:
    """Locale-correct Turkish uppercase (i→İ, ı→I)."""
    if not text:
        return ""
    out = []
    for ch in text:
        if ch == "i":
            out.append("İ")
        elif ch == "ı":
            out.append("I")
        else:
            out.append(ch.upper())
    return "".join(out)


def fix_tr_caps(text: str) -> str:
    """Fix undotted ALL-CAPS ASR fragments."""
    if not text:
        return ""
    s = text
    for wrong, right in sorted(_ASR_FIXES, key=lambda x: len(x[0]), reverse=True):
        if wrong == right or wrong.startswith("\\"):
            continue
        s = re.sub(re.escape(wrong), right, s, flags=re.IGNORECASE)
    # short words with boundaries
    for wrong, right in (
        (r"\bIC\b", "İÇ"),
        (r"\bBIR\b", "BİR"),
        (r"\bYENI\b", "YENİ"),
        (r"\bRESMI\b", "RESMİ"),
        (r"\bKI\b", "Kİ"),
    ):
        s = re.sub(wrong, right, s)
    return s


def caption_display(text: str) -> str:
    """Normalize one caption line for on-screen display."""
    s = " ".join((text or "").split())
    if not s:
        return ""
    s = tr_upper(s)
    s = fix_tr_caps(s)
    s = re.sub(r"\s*'\s*", "'", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s
