import requests
import json
import re
import time
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
from urllib.parse import quote
from .database import decision_exists, get_connection

class UyapClient:
    """T.C. Adalet Bakanlığı UYAP Emsal Karar Portalı Canlı Karar Çekici."""

    BASE_URL = "https://emsal.uyap.gov.tr"
    
    @staticmethod
    def clean_html(html_text: str) -> str:
        """UYAP HTML karar belgesini temiz ve biçimli metne dönüştürür."""
        if not html_text:
            return ""
        clean = re.sub(r'<\s*br\s*/?>', '\n', html_text, flags=re.I)
        clean = re.sub(r'<\s*/p\s*>', '\n\n', clean, flags=re.I)
        soup = BeautifulSoup(clean, 'html.parser')
        text = soup.get_text()
        lines = [line.strip() for line in text.split('\n')]
        return '\n'.join([l for l in lines if l])

    @classmethod
    def normalize_query(cls, q: str) -> str:
        """Kullanıcının yazdığı sorguyu UYAP araması için optimize eder."""
        q_clean = q.strip()
        
        # Gereksiz arama dolgu kelimelerini temizle
        noise_words = ["emsal", "karar", "kararları", "karari", "hakkında", "nelerdir", "nasıl", "nedir", "ilgili", "davası", "davasi"]
        words = q_clean.split()
        filtered = [w for w in words if w.lower() not in noise_words]
        if filtered:
            q_clean = " ".join(filtered)

        # Yaygın yazım düzeltmeleri
        replacements = {
            "mudafa": "meşru müdafaa",
            "mudafaa": "müdafaa",
            "mesru": "meşru",
            "kidem": "kıdem",
            "ise iade": "işe iade",
            "tazminati": "tazminatı",
            "taahhut": "tahliye taahhüdü",
            "taahhudu": "taahhüdü",
            "bosanma": "boşanma",
            "nafaka": "nafaka",
            "kamulastirma": "kamulaştırma",
            "dolandiricilik": "dolandırıcılık",
            "hirsizlik": "hırsızlık"
        }
        for k, v in replacements.items():
            pattern = re.compile(rf'\b{k}\b', re.IGNORECASE)
            q_clean = pattern.sub(v, q_clean)
        return q_clean

    @classmethod
    def fetch_live_decisions(cls, query: str, limit: int = 10, page_number: int = 1) -> Dict[str, Any]:
        """
        UYAP Emsal Karar portalına canlı istek atarak gerçek emsal kararları çeker.
        UYAP'taki toplam karar sayısını (recordsTotal) ve çekilen kararları döner.
        """
        session = requests.Session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Referer': f"{cls.BASE_URL}/",
            'Origin': cls.BASE_URL,
            'Content-Type': 'application/json; charset=utf-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json, text/javascript, */*; q=0.01'
        }

        query_optimized = cls.normalize_query(query)
        decisions = []
        total_in_uyap = 0

        try:
            # 1. Oturum başlat ve çerezleri al
            session.get(cls.BASE_URL, headers=headers, timeout=12)

            # 2. Arama bağlamını kur
            session.post(
                f"{cls.BASE_URL}/detayliArama",
                json={"aranan": query_optimized},
                headers=headers,
                timeout=15
            )

            # 3. Sonuç listesini sorgula
            payload = {
                "data": {
                    "arananKelime": query_optimized,
                    "pageSize": min(limit, 15),
                    "pageNumber": page_number
                }
            }
            resp = session.post(f"{cls.BASE_URL}/aramalist", json=payload, headers=headers, timeout=20)
            
            # Rate limit (429) durumunda bir kez 1.5 sn bekleyip tekrar dene
            if resp.status_code == 429:
                time.sleep(1.5)
                resp = session.post(f"{cls.BASE_URL}/aramalist", json=payload, headers=headers, timeout=20)

            if resp.status_code != 200:
                print(f"[UYAP] Hata kodu: {resp.status_code}")
                return {"total_in_uyap": 0, "decisions": [], "error": f"HTTP {resp.status_code}"}

            res_json = resp.json()
            data_node = res_json.get("data")
            if not data_node or "data" not in data_node:
                return {"total_in_uyap": 0, "decisions": []}

            total_in_uyap = data_node.get("recordsTotal", 0)
            raw_items = data_node.get("data", [])

            for item in raw_items:
                doc_id = item.get("id")
                daire = item.get("daire", "Bilinmeyen Daire")
                esas_no = item.get("esasNo", "")
                karar_no = item.get("kararNo", "")
                karar_tarihi = item.get("kararTarihi", "")
                karar_durumu = item.get("kararDurumu", "")

                # 4. Karar zaten yerel veritabanımızda varsa tekrar UYAP'tan indirme (ağ ve hız tasarrufu)
                if decision_exists(daire, esas_no, karar_no):
                    conn = get_connection()
                    c = conn.cursor()
                    c.execute(
                        "SELECT id, mahkeme, daire, esas_no, karar_no, karar_tarihi, hukuk_alani, karar_sonucu, ilgili_kanunlar, baslik, tam_metin, kaynak_url FROM decisions WHERE daire = ? AND esas_no = ? AND karar_no = ? LIMIT 1",
                        (daire, esas_no, karar_no)
                    )
                    existing_row = c.fetchone()
                    conn.close()
                    if existing_row:
                        decisions.append(dict(existing_row))
                        continue

                # 5. Yeni kararın tam metnini UYAP'tan çek (Rate limit korumalı)
                tam_metin = ""
                if doc_id:
                    try:
                        time.sleep(0.35)  # UYAP 429 engeli yememek için nazik bekleme
                        doc_resp = session.get(f"{cls.BASE_URL}/getDokuman?id={doc_id}", headers=headers, timeout=12)
                        if doc_resp.status_code == 429:
                            time.sleep(1.5)
                            doc_resp = session.get(f"{cls.BASE_URL}/getDokuman?id={doc_id}", headers=headers, timeout=12)
                            
                        if doc_resp.status_code == 200:
                            doc_data = doc_resp.json().get("data", "")
                            tam_metin = cls.clean_html(doc_data)
                    except Exception as e:
                        print(f"[UYAP] Doküman çekme hatası (ID: {doc_id}): {e}")

                if not tam_metin:
                    continue

                # Mahkeme türü ve hukuk alanı tespiti
                mahkeme = "BAM (İstinaf)"
                if "Yargıtay" in daire:
                    mahkeme = "Yargıtay"
                elif "Danıştay" in daire:
                    mahkeme = "Danıştay"
                elif "Bölge İdare" in daire or "İdare" in daire:
                    mahkeme = "BİM (İdare İstinaf)"

                # Hukuk alanı tahmini
                hukuk_alani = "Hukuk"
                low_text = (daire + " " + tam_metin).lower()
                if any(k in low_text for k in ["iş", "işe iade", "kıdem", "ihbar"]):
                    hukuk_alani = "İş Hukuku"
                elif any(k in low_text for k in ["kira", "tahliye", "kira tespiti"]):
                    hukuk_alani = "Kira Hukuku"
                elif any(k in low_text for k in ["ceza", "sanık", "tck", "meşru müdafaa", "yaralama", "katılan"]):
                    hukuk_alani = "Ceza Hukuku"
                elif any(k in low_text for k in ["tazminat", "trafik kazası", "destekten yoksun"]):
                    hukuk_alani = "Tazminat Hukuku"
                elif any(k in low_text for k in ["icra", "haciz", "kambiyo", "iik"]):
                    hukuk_alani = "İcra ve İflas Hukuku"
                elif any(k in low_text for k in ["ticaret", "rücu", "poliçe", "bono"]):
                    hukuk_alani = "Ticaret Hukuku"
                elif any(k in low_text for k in ["boşanma", "nafaka", "velayet"]):
                    hukuk_alani = "Aile Hukuku"

                # Karar sonucu
                sonuc = karar_durumu or "Karar Verildi"
                if not karar_durumu:
                    if "esastan reddine" in tam_metin.lower():
                        sonuc = "Esastan Ret (Onama)"
                    elif "kabulüne" in tam_metin.lower():
                        sonuc = "Kabul"
                    elif "bozulmasına" in tam_metin.lower():
                        sonuc = "Bozma"
                    elif "kaldırılmasına" in tam_metin.lower():
                        sonuc = "Kararın Kaldırılması"

                # Başlık oluşturma (Dava türü veya ilk cümle)
                dava_turu_match = re.search(r'DAVA\s*:\s*([^\n\r]+)', tam_metin)
                if dava_turu_match:
                    dava_adi = dava_turu_match.group(1).strip()
                    baslik = f"{daire} - {dava_adi} Davası Emsal Kararı"
                else:
                    baslik = f"{daire} Emsal Kararı - E. {esas_no} K. {karar_no}"

                # İlgili kanun maddelerini ayıkla
                kanun_matches = re.findall(r'(\b\d+\s+sayılı[^\n\.\,]+m\.\s*\d+)', tam_metin, re.IGNORECASE)
                kanunlar = list(set([k.strip() for k in kanun_matches[:3]]))

                decisions.append({
                    "mahkeme": mahkeme,
                    "daire": daire,
                    "esas_no": esas_no,
                    "karar_no": karar_no,
                    "karar_tarihi": karar_tarihi,
                    "hukuk_alani": hukuk_alani,
                    "karar_sonucu": sonuc,
                    "ilgili_kanunlar": kanunlar,
                    "baslik": baslik,
                    "tam_metin": tam_metin,
                    "kaynak_url": f"https://emsal.uyap.gov.tr/getDokuman?id={doc_id}"
                })

        except Exception as e:
            print(f"[UYAP] Canlı sorgulama genel hatası: {e}")

        return {
            "total_in_uyap": total_in_uyap,
            "page_number": page_number,
            "decisions": decisions
        }


class OfficialPortalBridge:
    """Resmi mahkeme portalları doğrudan arama bağlantıları köprüsü."""

    YARGITAY_SEARCH_URL = "https://karararama.yargitay.gov.tr"
    UYAP_EMSAL_URL = "https://emsal.uyap.gov.tr"
    DANISTAY_SEARCH_URL = "https://karararama.danistay.gov.tr"
    AYM_SEARCH_URL = "https://kararlarbilgibankasi.anayasa.gov.tr"

    @classmethod
    def generate_portal_links(cls, query: str) -> Dict[str, str]:
        q_encoded = quote(query.strip())
        return {
            "yargitay": f"{cls.YARGITAY_SEARCH_URL}/?q={q_encoded}",
            "uyap": f"{cls.UYAP_EMSAL_URL}/?arama={q_encoded}",
            "danistay": f"{cls.DANISTAY_SEARCH_URL}/?kelime={q_encoded}",
            "aym": f"{cls.AYM_SEARCH_URL}/bireysel?q={q_encoded}"
        }

    @classmethod
    def test_portal_connection(cls, portal: str = "uyap") -> Dict[str, Any]:
        url_map = {
            "yargitay": cls.YARGITAY_SEARCH_URL,
            "uyap": cls.UYAP_EMSAL_URL,
            "danistay": cls.DANISTAY_SEARCH_URL,
            "aym": cls.AYM_SEARCH_URL
        }
        target_url = url_map.get(portal.lower(), cls.UYAP_EMSAL_URL)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        try:
            resp = requests.get(target_url, headers=headers, timeout=5)
            return {
                "portal": portal,
                "url": target_url,
                "status_code": resp.status_code,
                "online": resp.status_code == 200,
                "message": "Bağlantı başarılı" if resp.status_code == 200 else f"HTTP {resp.status_code}"
            }
        except Exception as e:
            return {
                "portal": portal,
                "url": target_url,
                "status_code": None,
                "online": False,
                "message": f"Bağlantı kurulamadı: {str(e)}"
            }
