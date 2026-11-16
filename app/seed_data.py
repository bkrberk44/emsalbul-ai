from typing import List, Dict, Any
from .database import get_connection, insert_decision, init_db

PRESET_DECISIONS: List[Dict[str, Any]] = [
    {
        "mahkeme": "Yargıtay",
        "daire": "9. Hukuk Dairesi",
        "esas_no": "2023/11425",
        "karar_no": "2023/18920",
        "karar_tarihi": "14.11.2023",
        "hukuk_alani": "İş Hukuku",
        "karar_sonucu": "Bozma",
        "ilgili_kanunlar": ["4857 Sayılı İş Kanunu m. 18", "4857 Sayılı İş Kanunu m. 20", "4857 Sayılı İş Kanunu m. 21"],
        "baslik": "İşe İade Davası - Performans Düşüklüğü Sebebiyle Fesih - İşçinin Savunmasının Alınması ve Eğitime Tabi Tutulması Zorunluluğu",
        "kaynak_url": "https://karararama.yargitay.gov.tr",
        "tam_metin": """T.C.
YARGITAY
9. HUKUK DAİRESİ
ESAS NO: 2023/11425
KARAR NO: 2023/18920
KARAR TARİHİ: 14.11.2023

DAVA: Davacı vekili, davacının davalı işyerinde 01.03.2018 tarihinden itibaren satış danışmanı olarak çalıştığını, iş sözleşmesinin performans yetersizliği gerekçe gösterilerek 15.02.2023 tarihinde haksız ve geçerli bir sebep olmaksızın feshedildiğini ileri sürerek, feshin geçersizliğinin tespiti ile davacının işe iadesine, işe başlatılmama tazminatı ile boşta geçen süre ücretine karar verilmesini talep etmiştir.

DAVALI CEVABI: Davalı vekili, davacının son 6 aylık performans hedeflerini tutturamadığını, performans değerlendirme raporlarının objektif kriterlere dayandığını, feshin geçerli nedene dayandığını savunarak davanın reddini istemiştir.

İLK DERECE MAHKEMESİ KARARI: İlk Derece Mahkemesince, şirketin performans değerlendirme sisteminin mevcut olduğu ve hedeflerin gerçekleşmediği gerekçesiyle davanın reddine karar verilmiştir.

BÖLGE ADLİYE MAHKEMESİ KARARI: Bölge Adliye Mahkemesi istinaf başvurusunu esastan reddetmiştir. Karar davacı vekili tarafından temyiz edilmiştir.

GEREKÇE:
4857 sayılı İş Kanunu'nun 18. maddesi uyarınca iş sözleşmesinin geçerli sebeple feshedilebilmesi için işçinin yeterliliğinden veya davranışlarından kaynaklanan geçerli bir sebebin bulunması şarttır. İş Kanunu'nun 19. maddesine göre ise hakkındaki iddialara karşı savunmasını alma imkânı verilmeden bir işçinin belirsiz süreli iş sözleşmesi o işçinin davranışı veya verimi ile ilgili nedenlerle feshedilemez.

Performans düşüklüğü iddiasıyla yapılan fesihlerde şu ilkeler aranır:
1- İşyerinde objektif ve ölçülebilir performans kriterlerinin belirlenmiş olması ve işçiye önceden bildirilmiş bulunması,
2- İşçinin performansındaki düşüklüğün süreklilik arz etmesi,
3- İşçiye performansını artırması için gerekli eğitim ve imkânların sunulmuş olması,
4- Fesihten önce işçiden performans yetersizliğine dair yazılı savunmasının alınması zorunludur.

Somut uyuşmazlıkta; davalı işverenin davacı işçiyi hedefler doğrultusunda eksik kaldığı konularda herhangi bir mesleki eğitime tabi tutmadığı, performans düşüklüğünün nedenleri araştırılmadan doğrudan fesih yoluna gidildiği ve 'feshin son çare olması' (ultima ratio) ilkesine aykırı davranıldığı anlaşılmıştır. Bu nedenlerle feshin geçersizliğine ve davacının işe iadesine karar verilmesi gerekirken davanın reddi hatalıdır.

HÜKÜM:
Bölge Adliye Mahkemesi kararının BOZULMASINA, İlk Derece Mahkemesi kararının ortadan kaldırılarak davanın KABULÜNE, feshin GEÇERSİZLİĞİNE ve davacının İŞE İADESİNE, işe başlatmama tazminatının 4 aylık ücreti tutarında belirlenmesine oybirliğiyle karar verildi."""
    },
    {
        "mahkeme": "Yargıtay",
        "daire": "3. Hukuk Dairesi",
        "esas_no": "2023/5891",
        "karar_no": "2023/7412",
        "karar_tarihi": "22.09.2023",
        "hukuk_alani": "Kira Hukuku",
        "karar_sonucu": "Onama",
        "ilgili_kanunlar": ["6098 Sayılı Türk Borçlar Kanunu m. 350", "6098 Sayılı Türk Borçlar Kanunu m. 351"],
        "baslik": "İhtiyaç Sebebiyle Tahliye Davası - Kiraya Verenin Samimi, Gerçek ve Zorunlu Konut İhtiyacı - Kirada Oturan Ev Sahibinin Durumu",
        "kaynak_url": "https://karararama.yargitay.gov.tr",
        "tam_metin": """T.C.
YARGITAY
3. HUKUK DAİRESİ
ESAS NO: 2023/5891
KARAR NO: 2023/7412
KARAR TARİHİ: 22.09.2023

DAVA: Davacı vekili, davalının müvekkiline ait taşınmazda 01.01.2019 başlangıç tarihli kira sözleşmesi ile kiracı olduğunu, davacının ise kendisinin de kiracı olarak başka bir konutta ikamet ettiğini ve kendi ev sahibinin kendisini tahliye etmek üzere ihtarname gönderdiğini, dava konusu meşrutan başka bir taşınmazının bulunmadığını belirterek, TBK 350. maddesi uyarınca kiralananın ihtiyaç sebebiyle tahliyesini talep etmiştir.

DAVALI CEVABI: Davalı kiracı, ihtiyacın gerçek ve samimi olmadığını, davacının asıl amacının kira bedelini fahiş oranda artırmak olduğunu ileri sürerek davanın reddini savunmuştur.

İLK DERECE MAHKEMESİ KARARI: Mahkemece toplanan delillere göre; davacının halen başka bir taşınmazda kiracı olarak oturduğu, ev sahibinin tahliye baskısı altında olduğu, dinlenen tanık beyanları ve sunulan kira kontratları ile ihtiyacın gerçek, samimi ve zorunlu olduğu gerekçesiyle davanın kabulüne ve kiralananın tahliyesine karar verilmiştir.

GEREKÇE:
6098 sayılı Türk Borçlar Kanunu'nun 350/1. maddesi uyarınca, kiraya veren kira sözleşmesini; kiralananı kendisi, eşi, altsoyu, üstsoyu veya kanun gereği bakmakla yükümlü olduğu diğer kişiler için konut ya da işyeri gereksinimi sebebiyle kullanma zorunluluğu varsa, belirli süreli sözleşmelerde sürenin sonunda dava açarak sona erdirebilir.

Yerleşik Yargıtay içtihatlarına göre; kiraya verenin kendisinin de kirada oturuyor olması tek başına konut ihtiyacının varlığına karine teşkil eder. Kirada oturan malikin kendi mülkünde oturma isteği en doğal hak olup, bu ihtiyacın gerçek ve samimi olduğu kabul edilir. Davalının kira artışı baskısı yapıldığına dair soyut iddiaları dosya kapsamındaki somut belgeler karşısında ispatsız kalmıştır. Mahkemenin delilleri takdirinde ve kararında usul ve yasaya aykırı bir yön bulunmamaktadır.

HÜKÜM:
Dosyadaki yazılara, kararın dayandığı delillerle kanuni gerektirici sebeplere göre, yerinde bulunmayan temyiz itirazlarının reddi ile usul ve kanuna uygun olan hükmün ONANMASINA, oybirliğiyle karar verildi."""
    },
    {
        "mahkeme": "Yargıtay",
        "daire": "3. Hukuk Dairesi",
        "esas_no": "2023/8210",
        "karar_no": "2023/9540",
        "karar_tarihi": "05.10.2023",
        "hukuk_alani": "Kira Hukuku",
        "karar_sonucu": "Bozma",
        "ilgili_kanunlar": ["6098 Sayılı Türk Borçlar Kanunu m. 344"],
        "baslik": "Kira Tespit Davası - 5 Yıllık Sürenin Dolması - Emsal Rayiç Bedel Tespiti ve Hakkaniyet İndirimi Uygulanması Zorunluluğu",
        "kaynak_url": "https://karararama.yargitay.gov.tr",
        "tam_metin": """T.C.
YARGITAY
3. HUKUK DAİRESİ
ESAS NO: 2023/8210
KARAR NO: 2023/9540
KARAR TARİHİ: 05.10.2023

DAVA: Davacı kiralayan vekili, 01.07.2017 başlangıç tarihli sözleşmeyle aylık 3.000 TL bedelle kiralanan taşınmazın kira bedelinin, 5 yıllık sürenin dolması ve çevredeki rayiçlerin çok altında kalması sebebiyle 01.07.2022 tarihinden itibaren aylık net 25.000 TL olarak tespitini talep etmiştir.

İLK DERECE MAHKEMESİ KARARI: Mahkemece alınan bilirkişi raporuna göre taşınmazın boş olarak kiralanması halinde getirebileceği rayiç kira bedeli 22.000 TL olarak hesaplanmış, mahkeme de hakkaniyet indirimi yapmaksızın kira bedelini 22.000 TL olarak tespit etmiştir.

GEREKÇE:
TBK'nın 344/3. maddesi gereğince, taraflarca bu konuda bir anlaşma yapılıp yapılmadığına bakılmaksızın, beş yıldan uzun süreli veya beş yıldan sonra yenilenen kira sözleşmelerinde hakim; tüketici fiyat endeksindeki oniki aylık ortalamalara göre değişim oranını, kiralananın durumunu ve emsal kira bedellerini göz önünde tutarak hakkaniyete uygun bir kira bedeli belirler.

Bilirkişi tarafından belirlenen emsal kira bedeli 'boş olarak yeni bir kiracıya kiraya verilmesi' halindeki rayici gösterir. Ancak davalı, eski ve düzenli ödeme yapan bir kiracıdır (eski kiracı). Hâkimin, belirlenen rayiç bedelden davalının eski kiracı olması ve hakkaniyet ilkeleri gereği uygun bir oranda (%10 ila %20 arasında) hakkaniyet indirimi yapması kanuni bir zorunluluktur. Mahkemece hakkaniyet indirimi yapılmaksızın salt bilirkişi raporundaki çıplak rayiç üzerinden hüküm kurulması isabetsiz olup bozmayı gerektirmiştir.

HÜKÜM:
Temyiz olunan kararın yukarıda açıklanan nedenlerle BOZULMASINA oybirliğiyle karar verildi."""
    },
    {
        "mahkeme": "Yargıtay",
        "daire": "Ceza Genel Kurulu",
        "esas_no": "2022/1-450",
        "karar_no": "2023/312",
        "karar_tarihi": "18.05.2023",
        "hukuk_alani": "Ceza Hukuku",
        "karar_sonucu": "Bozma",
        "ilgili_kanunlar": ["5237 Sayılı Türk Ceza Kanunu m. 25/1", "5237 Sayılı Türk Ceza Kanunu m. 27/2"],
        "baslik": "Meşru Müdafaada Sınırın Aşılması - Mazur Görülebilecek Heyecan, Korku ve Telaş - Ceza Verilmesine Yer Olmadığı Kararı Verilmesi Gereği",
        "kaynak_url": "https://karararama.yargitay.gov.tr",
        "tam_metin": """T.C.
YARGITAY
CEZA GENEL KURULU
ESAS NO: 2022/1-450
KARAR NO: 2023/312
KARAR TARİHİ: 18.05.2023

DAVA VE UYUŞMAZLIK: Sanık hakkında kasten öldürmeye teşebbüs suçundan açılan kamu davasında; sanığın gece vakti evine zorla giren ve bıçakla üzerine saldıran maktul/katılana karşı eline geçirdiği sopa ile vurması sonucu hayati tehlikeye neden olacak şekilde yaralaması olayında, TCK'nın 27/2. maddesindeki meşru müdafaada sınırın heyecan, korku ve telaşla aşılması halinin uygulanıp uygulanamayacağı hususundadır.

İLK DERECE MAHKEMESİ KARARI: Sanık hakkında TCK m. 86/1, 87/1-d ve haksız tahrik hükümleri uygulanarak 3 yıl 9 ay hapis cezası verilmiştir.

YARGITAY CEZA GENEL KURULU GEREKÇESİ:
TCK'nın 25/1. maddesinde meşru savunma bir hukuka uygunluk nedeni olarak düzenlenmiştir. TCK'nın 27/2. maddesinde ise 'Meşru savunmada sınırın aşılması mazur görülebilecek bir heyecan, korku veya telaştan ileri gelmiş ise faile ceza verilmez' hükmü yer almaktadır.

Olay gecesi maktulün sanığın ikametgâh kapısını zorlayarak içeri girdiği, elinde bıçak olduğu ve sanığa ve ailesine yönelik fiili saldırıya geçtiği sabittir. Saldırının ağırlığı, gece vakti olması, sanığın ailesini koruma saiki ve aniden gelişen olay karşısında sanığın ruhsal durumunun mazur görülebilecek yoğun bir korku, dehşet ve telaş etkisi altında olduğu açıktır. Bu şartlar altında failden saldırı ile savunma arasındaki dengeyi hassas bir terazi gibi tartması beklenemez. Sanığın eylemi TCK 27/2 kapsamında kaldığından hakkında CEZA VERİLMESİNE YER OLMADIĞI kararı verilmesi gerekirken hapis cezasına hükmedilmesi yasaya aykırıdır.

HÜKÜM:
Direnme kararının BOZULMASINA, sanık hakkında TCK'nın 27/2 ve CMK'nın 223/3-c maddesi uyarınca CEZA VERİLMESİNE YER OLMADIĞINA karar verilmesi gerektiğinin gözetilmemesi sebebiyle bozulmasına karar verilmiştir."""
    },
    {
        "mahkeme": "Yargıtay",
        "daire": "4. Hukuk Dairesi",
        "esas_no": "2023/3201",
        "karar_no": "2023/6110",
        "karar_tarihi": "08.06.2023",
        "hukuk_alani": "Tazminat Hukuku",
        "karar_sonucu": "Bozma",
        "ilgili_kanunlar": ["6098 Sayılı Türk Borçlar Kanunu m. 53", "6098 Sayılı Türk Borçlar Kanunu m. 56", "2918 Sayılı KTK m. 90"],
        "baslik": "Trafik Kazası - Destekten Yoksun Kalma Tazminatı - TRH 2010 Yaşam Tablosu ve Progresif Rant Yöntemi Uygulanması Zorunluluğu",
        "kaynak_url": "https://karararama.yargitay.gov.tr",
        "tam_metin": """T.C.
YARGITAY
4. HUKUK DAİRESİ
ESAS NO: 2023/3201
KARAR NO: 2023/6110
KARAR TARİHİ: 08.06.2023

DAVA: Davacılar vekili, davalıların maliki, sürücüsü ve ZMMS sigortacısı olduğu aracın müvekkillerinin murisine çarparak ölümüne sebep olduğunu belirterek TBK 53 ve 56 maddeleri gereğince destekten yoksun kalma ve manevi tazminat talebinde bulunmuştur.

GEREKÇE:
Destekten yoksun kalma tazminatının hesabında usul ve yasaya uygun aktüeryal hesaplama yapılması zorunludur. Yargıtay Hukuk Genel Kurulu ve Dairemizin yerleşik içtihatlarına göre; bakiye ömür tespitinde Population (PMF 1931) Yaşam Tablosu yerine, Türkiye verilerine uygun olan ve güncelliğini koruyan TRH 2010 Yaşam Tablosu'nun esas alınması gerekmektedir. Tazminat hesabı ise 'Progresif Rant' (1/Kn katsayılı) yöntemine göre yapılmalıdır.

Bilirkişi raporunda PMF 1931 tablosu kullanılarak hesaplama yapılmış ve mahkemece bu hatalı rapora itibar edilerek hüküm tesis edilmiştir. Hükme esas alınan rapor güncel Yargıtay içtihatlarına aykırı olduğundan kararın bozulması gerekmiştir.

HÜKÜM:
Hükmün açıklanan nedenlerle BOZULMASINA oybirliğiyle karar verildi."""
    },
    {
        "mahkeme": "Anayasa Mahkemesi",
        "daire": "Genel Kurul",
        "esas_no": "2021/48901",
        "karar_no": "2023/88",
        "karar_tarihi": "15.02.2023",
        "hukuk_alani": "Anayasa ve İnsan Hakları",
        "karar_sonucu": "Hak İhlali",
        "ilgili_kanunlar": ["Türkiye Cumhuriyeti Anayasası m. 36", "Avrupa İnsan Hakları Sözleşmesi m. 6"],
        "baslik": "Bireysel Başvuru - Makul Sürede Yargılanma Hakkının İhlali - 11 Yıl Süren Kamulaştırmasız El Atma Davası - Manevi Tazminat",
        "kaynak_url": "https://kararlarbilgibankasi.anayasa.gov.tr",
        "tam_metin": """T.C.
ANAYASA MAHKEMESİ
GENEL KURUL
BAŞVURU NUMARASI: 2021/48901
KARAR TARİHİ: 15.02.2023

I. BAŞVURUNUN KONUSU
Başvuru; kamulaştırmasız el atma nedeniyle açılan tazminat davasının 11 yıl 2 ay sürmesi nedeniyle makul sürede yargılanma hakkının ihlal edildiği iddiasına ilişkindir.

II. DEĞERLENDİRME
Anayasa'nın 36. maddesinin birinci fıkrasında herkesin meşru vasıta ve yollardan faydalanmak suretiyle yargı mercileri önünde davacı veya davalı olarak iddia ve savunma ile adil yargılanma hakkına sahip olduğu belirtilmiştir. Yargılamanın makul sürede sonuçlandırılması adil yargılanma hakkının temel unsurlarındandır.

Davanın karmaşıklığı, tarafların ve yargı makamlarının tutumu dikkate alındığında; iki dereceli yargılamada 11 yılı aşan sürenin kabul edilebilir bir gerekçesi bulunmamaktadır. Yargılamadaki gecikme başvurucunun tutumundan kaynaklanmamış olup adli sistemin işleyişinden kaynaklanmaktadır. Bu durum Anayasa'nın 36. maddesinde güvence altına alınan makul sürede yargılanma hakkının ihlali sonucunu doğurmuştur.

III. HÜKÜM
1. Makul sürede yargılanma hakkının İHLAL EDİLDİĞİNE,
2. Başvurucuya net 45.000 TL manevi tazminat ÖDENMESİNE,
3. Kararın bir örneğinin Adalet Bakanlığına gönderilmesine oybirliğiyle karar verildi."""
    },
    {
        "mahkeme": "Yargıtay",
        "daire": "12. Hukuk Dairesi",
        "esas_no": "2023/4512",
        "karar_no": "2023/7890",
        "karar_tarihi": "11.10.2023",
        "hukuk_alani": "İcra ve İflas Hukuku",
        "karar_sonucu": "Bozma",
        "ilgili_kanunlar": ["2004 Sayılı İcra ve İflas Kanunu m. 170", "2004 Sayılı İcra ve İflas Kanunu m. 67"],
        "baslik": "Kambiyo Senetlerine Mahsus Haciz Yolu - İmzaya İtiraz - İmza İncelemesinde Adli Tıp Kurumu Fizik İhtisas Dairesi Raporunun Üstünlüğü",
        "kaynak_url": "https://karararama.yargitay.gov.tr",
        "tam_metin": """T.C.
YARGITAY
12. HUKUK DAİRESİ
ESAS NO: 2023/4512
KARAR NO: 2023/7890
KARAR TARİHİ: 11.10.2023

DAVA: Borçlu vekili icra mahkemesine başvurusunda; aleyhine başlatılan bonoya dayalı icra takibinde, takip dayanağı bonodaki keşideci imzasının müvekkiline ait olmadığını belirterek takibin iptalini ve alacaklı aleyhine %20 tazminata hükmedilmesini istemiştir.

GEREKÇE:
İtiraz konusu imzanın borçluya ait olup olmadığı hususunda mahkemece tek bir grafoloji uzmanı bilirkişiden rapor alınmış ve imzanın borçluya ait olduğu yönündeki rapora göre itiraz reddedilmiştir. Oysa ki borçlu vekilince rapora gerekçeli itirazlar sunulmuş ve dosyadaki imza örneklerinin yeterli olmadığı bildirilmiştir.

Yerleşik Yargıtay uygulamasına göre, imza inkarında borçlunun borç tarihinden önceki ve sonraki resmi kurumlarda (noter, tapu, banka vb.) bulunan samimi imza asılları celbedilerek karşılaştırma yapılmalı, raporlar arasında çelişki bulunması halinde Adli Tıp Kurumu Fizik İhtisas Dairesi'nden nihai kurul raporu alınmalıdır. Eksik incelemeyle karar verilmesi usul ve kanuna aykırıdır.

HÜKÜM:
Mahkeme kararının yukarıda yazılı nedenlerle BOZULMASINA oybirliğiyle karar verildi."""
    },
    {
        "mahkeme": "Danıştay",
        "daire": "6. Daire",
        "esas_no": "2022/6710",
        "karar_no": "2023/4102",
        "karar_tarihi": "12.04.2023",
        "hukuk_alani": "İdare ve İmar Hukuku",
        "karar_sonucu": "İptal / Bozma",
        "ilgili_kanunlar": ["3194 Sayılı İmar Kanunu m. 8", "Mekânsal Planlar Yapım Yönetmeliği m. 26"],
        "baslik": "Nazım ve Uygulama İmar Planı Değişikliği - Donatı Alanının Azaltılması - Eşdeğer Alan Ayrılmaması Nedeniyle Hukuka Aykırılık",
        "kaynak_url": "https://karararama.danistay.gov.tr",
        "tam_metin": """T.C.
DANIŞTAY
ALTINCI DAİRE
ESAS NO: 2022/6710
KARAR NO: 2023/4102
KARAR TARİHİ: 12.04.2023

İSTEMİN ÖZETİ: Davacı, mülkiyeti kendisine ait komşu parselin bulunduğu bölgedeki 1/1000 ölçekli Uygulama İmar Planı değişikliğinin iptalini talep etmiştir. Dava konusu plan değişikliği ile daha önce 'Park ve Çocuk Oyun Alanı' olan kamuya açık alanın 'Ticaret + Konut Alanı'na çevrildiği belirlenmiştir.

DANIŞTAY GEREKÇESİ:
Mekânsal Planlar Yapım Yönetmeliği'nin 26. maddesi uyarınca imar planında yer alan bir sosyal ve teknik altyapı alanının (park, okul, sağlık tesisi vb.) kaldırılabilmesi veya küçültülebilmesi ancak bu alanın hizmet edeceği etki alanı içinde eşdeğer bir alanın ayrılması şartına bağlıdır.

Dava konusu işlem incelendiğinde; kaldırılan park alanı yerine aynı hizmet etki alanı içinde büyüklük ve konum olarak eşdeğer yeni bir yeşil alan ayrılmadığı, plan değişikliğinin kamu yararını değil rant artışını öncelediği, donatı dengesini bozduğu ve planlama ilkelerine açıkça aykırı olduğu sabittir. İdare Mahkemesince davanın reddine karar verilmesi hukuken isabetsizdir.

HÜKÜM:
İdare Mahkemesi kararının BOZULMASINA, dava konusu plan değişikliği işleminin İPTALİNE oybirliğiyle karar verildi."""
    },
    {
        "mahkeme": "Yargıtay",
        "daire": "Hukuk Genel Kurulu",
        "esas_no": "2022/3-890",
        "karar_no": "2023/514",
        "karar_tarihi": "24.05.2023",
        "hukuk_alani": "Kira Hukuku",
        "karar_sonucu": "Onama",
        "ilgili_kanunlar": ["6098 Sayılı Türk Borçlar Kanunu m. 352/1"],
        "baslik": "Tahliye Taahhütnamesi - Beyaza İmza (Açığa İmza) İddiası - Kiracının Boş Kağıda İmza Atmanın Hukuki Sonuçlarına Katlanma Yükümlülüğü",
        "kaynak_url": "https://karararama.yargitay.gov.tr",
        "tam_metin": """T.C.
YARGITAY
HUKUK GENEL KURULU
ESAS NO: 2022/3-890
KARAR NO: 2023/514
KARAR TARİHİ: 24.05.2023

DAVA VE DİRENME: Davacı kiraya veren, davalı kiracının vermiş olduğu yazılı tahliye taahhüdüne dayanarak icra takibi başlatmış, itiraz üzerine tahliye davası açmıştır. Davalı kiracı ise tahliye taahhütnamesinin kira sözleşmesi yapılırken boş olarak imzalatıldığını, tanzim ve tahliye tarihlerinin sonradan kiralayan tarafından doldurulduğunu ileri sürerek davanın reddini savunmuştur.

HUKUK GENEL KURULU GEREKÇESİ:
Yerleşik Yargıtay içtihatları ve Hukuk Genel Kurulu'nun kararlılık kazanmış uygulamalarına göre; atılan imza ile metin arasında bir bağ kurulmuş olur. İmza sahibi, üzerine imza attığı belgenin sonradan doldurulmuş olmasının doğuracağı hukuki sonuçlara katlanmak zorundadır (beyaza imza kuralı). Kiracı, tahliye taahhütnamesini açığa imzalayıp vermekle kiralayana bu belgeyi anlaşmaya uygun doldurma yetkisini vermiş sayılır.

Taahhütnamenin anlaşmaya aykırı olarak doldurulduğu iddiası ancak HMK hükümleri dairesinde yazılı delille ispatlanabilir. Davalı kiracı tarafından taahhütnamenin anlaşmaya aykırı doldurulduğuna dair yazılı bir delil sunulamadığından, geçerli tahliye taahhüdüne dayalı tahliye davasının kabulü gerekir.

HÜKÜM:
Direnme kararının ONANMASINA oyçokluğu ile karar verildi."""
    },
    {
        "mahkeme": "Yargıtay",
        "daire": "2. Hukuk Dairesi",
        "esas_no": "2023/2140",
        "karar_no": "2023/5612",
        "karar_tarihi": "19.09.2023",
        "hukuk_alani": "Aile Hukuku",
        "karar_sonucu": "Düzelterek Onama",
        "ilgili_kanunlar": ["4721 Sayılı Türk Medeni Kanunu m. 166", "4721 Sayılı Türk Medeni Kanunu m. 174"],
        "baslik": "Boşanma Davası - Güven Sarsıcı Davranışlar ve Sadakat Yükümlülüğünün İhlali - Ağır Kusurlu Eş Aleyhine Maddi ve Manevi Tazminat",
        "kaynak_url": "https://karararama.yargitay.gov.tr",
        "tam_metin": """T.C.
YARGITAY
2. HUKUK DAİRESİ
ESAS NO: 2023/2140
KARAR NO: 2023/5612
KARAR TARİHİ: 19.09.2023

DAVA: Taraflar arasındaki karşılıklı evlilik birliğinin temelinden sarsılması hukuki sebebine dayalı boşanma davasında; ilk derece mahkemesince kadının davasının kabulüne, erkeğin karşı davasının reddine, kadın lehine maddi-manevi tazminata ve yoksulluk nafakasına hükmedilmiştir.

GEREKÇE:
Yapılan yargılama ve toplanan delillerden; davalı-karşı davacı erkeğin başka bir kadınla sürekli ve olağan hayatın gerektirdiğinin ötesinde duygusal içerikli telefon görüşmeleri yaptığı, eşine karşı ilgisiz davrandığı ve sadakat yükümlülüğünü ağır biçimde ihlal ettiği anlaşılmaktadır. Erkeğin bu eylemleri evlilik birliğini temelinden sarsmış olup olayda tam kusurludur. Kadına yüklenebilecek herhangi bir kusur ispatlanamamıştır.

TMK m. 174/1 uyarınca mevcut veya beklenen menfaatleri boşanma yüzünden zedelenen kusursuz eş yararına uygun bir maddi tazminata; TMK m. 174/2 uyarınca kişilik hakları saldırıya uğrayan eş lehine manevi tazminata hükmedilmesi yasaya uygundur. Ancak takdir edilen manevi tazminat miktarı tarafların sosyal ve ekonomik durumu karşısında az bulunmuş olup düzeltilerek onanması uygun görülmüştür.

HÜKÜM:
Hükmün manevi tazminat miktarı yönünden DÜZELTİLEREK ONANMASINA oybirliğiyle karar verildi."""
    }
]

def seed_database():
    """Örnek emsal kararları veritabanına ekler."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM decisions")
    count = cursor.fetchone()[0]
    conn.close()

    if count == 0:
        for decision in PRESET_DECISIONS:
            insert_decision(decision)
        print(f"[Seed] {len(PRESET_DECISIONS)} adet emsal karar başarıyla veritabanına yüklendi.")
    else:
        print(f"[Seed] Veritabanında zaten {count} adet karar mevcut.")

if __name__ == "__main__":
    seed_database()
