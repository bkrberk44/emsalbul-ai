import requests
import json
import re
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
from urllib.parse import quote

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
    def fetch_live_decisions(cls, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        UYAP Emsal Karar portalına canlı istek atarak gerçek emsal kararları çeker.
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

        decisions = []
        try:
            # 1. Oturum başlat ve çerezleri al
            session.get(cls.BASE_URL, headers=headers, timeout=12)

            # 2. Arama bağlamını kur
            session.post(
                f"{cls.BASE_URL}/detayliArama",
                json={"aranan": query},
                headers=headers,
                timeout=15
            )

            # 3. Sonuç listesini sorgula
            payload = {
                "data": {
                    "arananKelime": query,
                    "pageSize": min(limit, 20),
                    "pageNumber": 1
                }
            }
            resp = session.post(f"{cls.BASE_URL}/aramalist", json=payload, headers=headers, timeout=20)
            
            if resp.status_code != 200:
                print(f"[UYAP] Hata kodu: {resp.status_code}")
                return []

            res_json = resp.json()
            data_node = res_json.get("data")
            if not data_node or "data" not in data_node:
                return []

            raw_items = data_node.get("data", [])

            for item in raw_items:
                doc_id = item.get("id")
                daire = item.get("daire", "Bilinmeyen Daire")
                esas_no = item.get("esasNo", "")
                karar_no = item.get("kararNo", "")
                karar_tarihi = item.get("kararTarihi", "")
                karar_durumu = item.get("kararDurumu", "")

                # 4. Belgenin tam metnini çek
                tam_metin = ""
                if doc_id:
                    try:
                        doc_resp = session.get(f"{cls.BASE_URL}/getDokuman?id={doc_id}", headers=headers, timeout=15)
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
                if any(k in daire.lower() or k in tam_metin.lower() for k in ["iş", "işe iade", "kıdem", "ihbar"]):
                    hukuk_alani = "İş Hukuku"
                elif any(k in daire.lower() or k in tam_metin.lower() for k in ["kira", "tahliye", "kira tespiti"]):
                    hukuk_alani = "Kira Hukuku"
                elif any(k in daire.lower() or k in tam_metin.lower() for k in ["ceza", "sanık", "tck"]):
                    hukuk_alani = "Ceza Hukuku"
                elif any(k in daire.lower() or k in tam_metin.lower() for k in ["tazminat", "trafik kazası", "destekten yoksun"]):
                    hukuk_alani = "Tazminat Hukuku"
                elif any(k in daire.lower() or k in tam_metin.lower() for k in ["icra", "haciz", "kambiyo", "iik"]):
                    hukuk_alani = "İcra ve İflas Hukuku"
                elif any(k in daire.lower() or k in tam_metin.lower() for k in ["ticaret", "rücu", "poliçe", "bono", "ttd"]):
                    hukuk_alani = "Ticaret Hukuku"
                elif any(k in daire.lower() or k in tam_metin.lower() for k in ["boşanma", "nafaka", "velayet"]):
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

        return decisions


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
