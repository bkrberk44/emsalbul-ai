# 🚀 EmsalBul.AI Canlıya Yayınlama Kılavuzu (Production Deployment Guide)

Bu kılavuz, **EmsalBul.AI** uygulamasını internette kendi alan adınızla (`alanadiniz.com`) 7/24 kesintisiz ve güvenli şekilde yayınlamanız için hazırlanmıştır.

---

## 📌 Adım 1: Sunucu (VPS) ve Alan Adı Hazırlığı

1. **Sunucu Kiralama:**
   * Tavsiye edilen sağlayıcılar: **Hetzner** (aylık ~4€), **DigitalOcean** (aylık 6$), **AWS** veya yerel Türk hosting firmaları (Turhost, Güzel Hosting vb.).
   * İşletim Sistemi: **Ubuntu 22.04 LTS** veya **Ubuntu 24.04 LTS**.
   * Özellikler: En az 1 GB RAM, 1 vCPU, 20 GB SSD (Başlangıç için fazlasıyla yeterlidir).

2. **Alan Adı (Domain) Yönlendirmesi:**
   * Alan adınızın DNS yönetim paneline girin.
   * `A` kaydı olarak sunucunuzun IP adresini ekleyin:
     * `alanadiniz.com` ➔ `SUNUCU_IP_ADRESINIZ`
     * `www.alanadiniz.com` ➔ `SUNUCU_IP_ADRESINIZ`

---

## 📌 Adım 2: Sunucuya Projeyi Yükleme

Sunucunuza SSH ile bağlanın:
```bash
ssh root@SUNUCU_IP_ADRESINIZ
```

Proje klasörünü sunucuya yükleyin veya kopyalayın:
```bash
mkdir -p /app/emsal_karar_arama
cd /app/emsal_karar_arama
# Dosyalarınızı buraya kopyalayın veya git clone yapın
```

---

## 📌 Adım 3: İki Farklı Yayınlama Yolu

### Yöntem A: Docker ile Tek Komutta Yayınlama (Önerilen & En Kolayı)

Sunucunuzda Docker kurulu ise:
```bash
# Arka planda konteyneri ayağa kaldırır
docker compose up -d --build
```
Uygulamanız doğrudan `http://SUNUCU_IP_ADRESINIZ:8000` portunda çalışmaya başlar.

---

### Yöntem B: Otomatik Kurulum Betiği (`deploy.sh`)

Sistemde Nginx, Gunicorn ve Systemd servisini otomatik kuran betiğimizi çalıştırın:
```bash
chmod +x deploy.sh
./deploy.sh
```
Bu betik:
1. Python sanal ortamını (`venv`) ve tüm kütüphaneleri kurar.
2. `systemd` servisi (`emsalkarar.service`) oluşturarak sunucu yeniden başlasa bile sitenizin 7/24 otomatik açılmasını sağlar.
3. Nginx ters vekilini (Reverse Proxy) bağlar.

---

## 📌 Adım 4: Ücretsiz SSL (HTTPS) Sertifikası Kurma

Alan adınızın adres çubuğunda güvenli kilit simgesi (`https://`) ile açılması için Let's Encrypt SSL sertifikasını tek komutla kurun:

```bash
sudo certbot --nginx -d alanadiniz.com -d www.alanadiniz.com
```
* Certbot sizden bir e-posta adresi isteyecek ve yönlendirmeyi otomatik yapacaktır.
* Artık siteniz `https://alanadiniz.com` olarak dünyadaki herkese açıktır!

---

## ⚖️ Yasal ve KVKK Takibi

1. **Yasal Uyarı ve Sorumluluk Reddi:**  
   Sitenin alt kısmına Yasal Uyarı, KVKK Politikası ve FSEK m. 31 telifsizlik maddeleri entegre edilmiştir.
2. **Karar Kaldırma Talepleri:**  
   Bir şahıs kişisel verisinin silinmesi için sitedeki formu doldurduğunda bildirim doğrudan sunucunuzdaki `takedown_requests.log` dosyasına saat ve tarih bilgisiyle birlikte kaydedilir:
   ```bash
   cat takedown_requests.log
   ```
   Gelen talebi inceleyip ilgili kararı veritabanından tek tıkla silebilir veya isimleri maskeleyebilirsiniz.
3. **UYAP Hız Koruması (Rate Limiting):**  
   `app/main.py` içinde istemci başına 3 saniyelik sorgu bekleme koruması aktiftir; böylece kamu sunucularına aşırı yük gitmez ve sunucu IP'niz banlanmaz.
