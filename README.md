# ⚖️ EmsalBul.AI - Türkiye Emsal Karar Arama & AI Analiz Platformu

Türkiye'deki yüksek mahkemelerin (**Yargıtay, Danıştay, Anayasa Mahkemesi ve UYAP**) emsal kararlarını Google sadeliğinde tek tıkla arayan, tam metinlerini gösteren ve **Yapay Zekâ ile Karar Özeti / Hukuki İlke Analizi** çıkaran yeni nesil Hukuk Teknolojisi (LegalTech) uygulaması.

---

## 🌟 Temel Özellikler

1. **Tek Tıkla Akıllı Arama (FTS5 + NLP):**
   - Kelime, kavram veya kanun maddesi (örn: *TBK 344*, *işe iade*, *tahliye*, *meşru müdafaa*) yazarak anında sonuç getirme.
   - Eşleşen kelimelerin karar metni içinde dinamik olarak vurgulanması (`<mark>`).

2. **Yapay Zekâ ile Karar Analitiği (AI Hukuk Özeti):**
   - **📌 Davanın Konusu ve Olay**
   - **⚖️ Temel Hukuki Uyuşmazlık**
   - **💡 Mahkemenin Hukuki Gerekçesi**
   - **🎯 Hüküm ve Karar Sonucu (Bozma, Onama vb.)**
   - **🌟 Önemli Hukuki İlkeler** (Maddeler halinde veciz ilkeler)
   - **📜 Dayanılan Kanun Maddeleri**

3. **Gelişmiş Çok Kriterli Filtreleme:**
   - Mahkeme Sekmeleri (Tümü, Yargıtay, Danıştay, Anayasa Mahkemesi)
   - Hukuk Alanı (İş Hukuku, Kira Hukuku, Ceza Hukuku, Tazminat, İcra vb.)
   - Karar Sonucu (Bozma, Onama, Düzelterek Onama, Hak İhlali, İptal)
   - Karar Yılı Aralığı

4. **Avukat ve Hukukçular İçin Pratik Araçlar:**
   - **Tek Tıkla Resmi Atıf Kopyalama:** (örn: *Yargıtay 9. HD, E. 2023/11425, K. 2023/18920, T. 14.11.2023*)
   - **Tam Metin İnceleme Modalı & Yazdırma:** Kararı rahatça okuma ve doğrudan yazdırma/PDF kaydetme.
   - **Resmi Portallar Köprüsü:** Arama yapılan ifadeyi tek tıkla doğrudan Yargıtay, UYAP, Danıştay veya AYM resmi arama sistemlerinde açabilme.

---

## 🚀 Kurulum ve Çalıştırma

### 1. Gereksinimleri Yükleme
```bash
python -m pip install -r requirements.txt
```

### 2. Uygulamayı Başlatma
```bash
python run.py
```

Tarayıcınızda şu adresi açın:
👉 **http://127.0.0.1:8000**

Otomatik API Dokümantasyonu (Swagger):
👉 **http://127.0.0.1:8000/docs**

---

## 📁 Proje Dizin Yapısı

```
emsal_karar_arama/
├── app/
│   ├── main.py              # FastAPI Web & API Endpoints
│   ├── models.py            # Veri şemaları ve Pydantic modelleri
│   ├── database.py          # SQLite FTS5 veritabanı ve arama dizini
│   ├── search_engine.py     # Türkçe karakter duyarlı akıllı arama ve highlight motoru
│   ├── ai_service.py        # Yapay zekâ karar özetleme ve ilke çıkarım servisi
│   ├── live_scraper.py      # Resmi portallara bağlantı ve canlı link köprüsü
│   ├── seed_data.py         # Yargıtay, Danıştay, AYM zengin örnek emsal kararlar
│   ├── static/
│   │   ├── css/style.css    # Özel stiller, animasyonlar ve print desteği
│   │   └── js/app.js        # Reaktif arama, filtreler, modal ve atıf kopyalama
│   └── templates/
│       └── index.html       # Modern, responsive arayüz (Tailwind CSS + Lucide Icons)
├── emsal_kararlar.db        # SQLite FTS5 veritabanı (otomatik oluşturulur)
├── run.py                   # Sunucuyu başlatan çalıştırma dosyası
├── requirements.txt         # Python bağımlılıkları
└── README.md                # Proje dokümantasyonu
```
