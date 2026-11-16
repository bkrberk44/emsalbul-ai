import re
import os
from typing import Dict, Any, List
from .database import get_decision_by_id

def extract_section(text: str, start_pattern: str, end_patterns: List[str]) -> str:
    """Metin içindeki belirli bir hukuki bölümü ayıklar."""
    start_match = re.search(start_pattern, text, re.IGNORECASE)
    if not start_match:
        return ""
    start_pos = start_match.end()

    end_pos = len(text)
    for ep in end_patterns:
        end_match = re.search(ep, text[start_pos:], re.IGNORECASE)
        if end_match:
            candidate_end = start_pos + end_match.start()
            if candidate_end < end_pos:
                end_pos = candidate_end

    section_text = text[start_pos:end_pos].strip()
    return " ".join(section_text.split())

def summarize_decision_ai(decision_id: int) -> Dict[str, Any]:
    """Bir emsal kararı analiz edip hukuki özet kartı oluşturur."""
    decision = get_decision_by_id(decision_id)
    if not decision:
        return {"error": "Karar bulunamadı"}

    tam_metin = decision["tam_metin"]
    baslik = decision["baslik"]
    kanunlar = decision.get("ilgili_kanunlar", [])
    sonuc = decision["karar_sonucu"]

    # 1. Dava Konusu Çıkarma
    dava_konusu = extract_section(
        tam_metin,
        r"(?:DAVA VE UYUŞMAZLIK|DAVA VE DİRENME|DAVA|I\.\s*BAŞVURUNUN KONUSU|İSTEMİN ÖZETİ)\s*:",
        [r"DAVALI CEVABI", r"İLK DERECE", r"GEREKÇE", r"II\.\s*DEĞERLENDİRME", r"HÜKÜM", r"DANIŞTAY GEREKÇESİ"]
    )
    if not dava_konusu:
        # Fallback: İlk 2 paragraftan çıkar
        lines = [line.strip() for line in tam_metin.split("\n") if len(line.strip()) > 30]
        dava_konusu = lines[0] if lines else baslik

    # 2. Uyuşmazlık Çıkarma
    uyusmazlik_match = re.search(r"(?:uyuşmazlık|uyuşmazlığın konusu|temel sorun)[^\.\n]+(?:\.|\n)", tam_metin, re.IGNORECASE)
    if uyusmazlik_match:
        uyusmazlik = uyusmazlik_match.group(0).strip()
    else:
        uyusmazlik = f"{decision['hukuk_alani']} kapsamında {baslik.split('-')[0].strip()} talebinin hukuka uygunluğunun tespiti."

    # 3. Gerekçe Çıkarma
    gerekce = extract_section(
        tam_metin,
        r"(?:GEREKÇE|YARGITAY CEZA GENEL KURULU GEREKÇESİ|DANIŞTAY GEREKÇESİ|HUKUK GENEL KURULU GEREKÇESİ|II\.\s*DEĞERLENDİRME)\s*:",
        [r"HÜKÜM", r"III\.\s*HÜKÜM", r"SONUÇ"]
    )
    if not gerekce:
        gerekce = "Mahkemenin ilgili mevzuat ve yerleşik içtihatlar ışığında yaptığı hukuki değerlendirme."

    # 4. Hüküm ve Sonuç Çıkarma
    hukum = extract_section(
        tam_metin,
        r"(?:HÜKÜM|III\.\s*HÜKÜM|SONUÇ)\s*:",
        [r"Dairemiz", r"Başkan"]
    )
    if not hukum:
        hukum = f"Davanın {sonuc} yönünde karara bağlanmasına karar verilmiştir."

    # 5. Önemli Hukuki İlkeler (Maddeler halinde)
    onemli_ilkeler = []
    # Numaralı veya tireli ilkeleri ara
    bullet_matches = re.findall(r"(?:^\s*[\d\-•]\s*[\-\)]?\s*)([A-ZÇĞİÖŞÜ][^\.\n]+\.)", tam_metin, re.MULTILINE)
    if bullet_matches:
        onemli_ilkeler.extend([b.strip() for b in bullet_matches[:4]])

    if not onemli_ilkeler:
        # Cümle bazlı ilke tespiti
        sentences = [s.strip() for s in gerekce.split(".") if len(s.strip()) > 40]
        for s in sentences:
            if any(term in s.lower() for term in ["zorunludur", "şarttır", "hükmündedir", "kuraldır", "esas alınmalıdır", "karinedir"]):
                onemli_ilkeler.append(s + ".")
                if len(onemli_ilkeler) >= 3:
                    break

    if not onemli_ilkeler:
        onemli_ilkeler.append(baslik)

    # 6. Kanun Maddeleri Tespiti
    found_articles = list(kanunlar)
    regex_articles = re.findall(r"(?:[A-ZÇĞİÖŞÜa-zçğıöşü\s]+Kanun[^\d]*m\.\s*\d+(?:/\d+)?)", tam_metin)
    for a in regex_articles[:3]:
        clean_a = " ".join(a.split())
        if clean_a not in found_articles:
            found_articles.append(clean_a)

    return {
        "decision_id": decision_id,
        "baslik": baslik,
        "dava_konusu": dava_konusu,
        "uyusmazlik": uyusmazlik,
        "hukuki_gerekce": gerekce[:650] + ("..." if len(gerekce) > 650 else ""),
        "hukum_ve_sonuc": hukum[:400] + ("..." if len(hukum) > 400 else ""),
        "onemli_ilkeler": onemli_ilkeler,
        "ilgili_maddeler": found_articles[:5]
    }
