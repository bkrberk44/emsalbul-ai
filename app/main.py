import os
import json
from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, Request, Query, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .database import init_db, get_decision_by_id, insert_decision, get_db_stats
from .seed_data import seed_database
from .search_engine import execute_search
from .ai_service import summarize_decision_ai
from .live_scraper import OfficialPortalBridge
from .models import DecisionBase

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="Emsal Karar Arama Motoru",
    description="Türkiye Mahkemeleri (Yargıtay, Danıştay, AYM, UYAP) Emsal Karar Arama ve AI Analiz Platformu",
    version="1.0.0"
)

# Statik ve şablon dizinleri
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@app.on_event("startup")
def on_startup():
    """Uygulama başlarken veritabanını kur ve örnek kararları yükle."""
    init_db()
    seed_database()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Ana arama arayüzü sayfası."""
    stats = get_db_stats()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"stats": stats}
    )

@app.get("/api/search")
async def api_search(
    q: Optional[str] = Query("", description="Arama kelimesi veya kavram"),
    mahkeme: Optional[str] = Query(None, description="Mahkeme türü"),
    daire: Optional[str] = Query(None, description="İlgili daire"),
    hukuk_alani: Optional[str] = Query(None, description="Hukuk alanı"),
    karar_sonucu: Optional[str] = Query(None, description="Karar sonucu"),
    yil_baslangic: Optional[int] = Query(None, description="Başlangıç yılı"),
    yil_bitis: Optional[int] = Query(None, description="Bitiş yılı"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Emsal kararlarda tam metin ve filtreli arama yapar."""
    result = execute_search(
        query=q or "",
        mahkeme=mahkeme,
        daire=daire,
        hukuk_alani=hukuk_alani,
        karar_sonucu=karar_sonucu,
        yil_baslangic=yil_baslangic,
        yil_bitis=yil_bitis,
        limit=limit,
        offset=offset
    )
    return result

@app.get("/api/decisions/{decision_id}")
async def api_get_decision(decision_id: int):
    """Tek bir emsal kararın tüm detaylarını getirir."""
    decision = get_decision_by_id(decision_id)
    if not decision:
        raise HTTPException(status_code=404, detail="Karar bulunamadı")
    return decision

@app.get("/api/decisions/{decision_id}/ai-summary")
async def api_get_ai_summary(decision_id: int):
    """Seçilen emsal karar için yapay zekâ destekli özet ve analiz kartı üretir."""
    summary = summarize_decision_ai(decision_id)
    if "error" in summary:
        raise HTTPException(status_code=404, detail=summary["error"])
    return summary

@app.get("/api/stats")
async def api_get_stats():
    """Veritabanı istatistiklerini getirir."""
    return get_db_stats()

@app.post("/api/decisions")
async def api_create_decision(decision: DecisionBase):
    """Yeni bir emsal karar ekler."""
    inserted_id = insert_decision(decision.model_dump())
    return {"id": inserted_id, "message": "Emsal karar başarıyla kaydedildi"}

@app.get("/api/portal-links")
async def api_get_portal_links(q: str = Query(..., description="Aranan kelime")):
    """Kullanıcının sorgusu için resmi portallarda arama bağlantıları üretir."""
    links = OfficialPortalBridge.generate_portal_links(q)
    return {"query": q, "links": links}

@app.get("/api/portal-status")
async def api_portal_status(portal: str = Query("uyap")):
    """Resmi mahkeme portalının erişim durumunu test eder."""
    return OfficialPortalBridge.test_portal_connection(portal)

# Canlı sorgulama için basit bellek içi hız sınırlandırma (Rate Limiting & Cooldown)
import time
from collections import defaultdict
client_requests = defaultdict(float)

@app.get("/api/live/search")
async def api_live_uyap_search(
    request: Request,
    q: str = Query(..., description="UYAP'tan canlı aranacak konu/kelime"),
    limit: int = Query(10, ge=1, le=20, description="Çekilecek karar sayısı"),
    page: int = Query(1, ge=1, description="UYAP sayfa numarası")
):
    """
    Adalet Bakanlığı UYAP Emsal Karar sisteminden canlı olarak gerçek kararları çeker,
    veritabanına ve tam metin FTS5 dizinine kaydeder ve sonuçları döndürür.
    UYAP IP engeli yememek için istemci başına 2 saniyelik bekleme koruması uygulanır.
    """
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    last_req_time = client_requests[client_ip]

    if now - last_req_time < 2.0:
        raise HTTPException(
            status_code=429,
            detail="UYAP sunucularını korumak için lütfen yeni canlı sorgulama yapmadan önce 2 saniye bekleyiniz."
        )
    client_requests[client_ip] = now

    from .live_scraper import UyapClient
    result = UyapClient.fetch_live_decisions(query=q, limit=limit, page_number=page)
    live_decisions = result.get("decisions", [])
    total_in_uyap = result.get("total_in_uyap", 0)

    saved_count = 0
    already_saved_count = 0
    saved_ids = []
    for d in live_decisions:
        try:
            inserted_id, is_new = insert_decision(d, return_is_new=True)
            if is_new:
                saved_count += 1
            else:
                already_saved_count += 1
            saved_ids.append(inserted_id)
        except Exception as e:
            print(f"[Live Ingest] Kayıt hatası: {e}")

    return {
        "status": "success",
        "query": q,
        "total_in_uyap": total_in_uyap,
        "page": page,
        "retrieved_count": len(live_decisions),
        "saved_to_db": saved_count,
        "already_saved": already_saved_count,
        "decisions": live_decisions
    }

class TakedownRequest(DecisionBase.__class__):
    pass

@app.post("/api/takedown-request")
async def api_takedown_request(request: Request):
    """KVKK veya telif gerekçesiyle karar kaldırma/düzeltme bildirimlerini kaydeder."""
    try:
        body = await request.json()
    except Exception:
        body = {}
    
    print(f"[KVKK Kaldırma Talebi] İsim: {body.get('name')}, E-Posta: {body.get('email')}, Karar: {body.get('karar')}")
    print(f"[Gerekçe]: {body.get('reason')}")
    
    # Talepleri dosyaya da loglayalım
    try:
        log_file = BASE_DIR.parent / "takedown_requests.log"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {json.dumps(body, ensure_ascii=False)}\n")
    except Exception as e:
        print(f"Log yazma hatası: {e}")

    return {
        "status": "success",
        "message": "Kaldırma talebiniz başarıyla alınmıştır. İnceleme neticesinde en geç 48 saat içerisinde e-posta ile dönüş yapılacaktır."
    }

@app.post("/api/seed/reset")
async def api_reset_seed():
    """Veritabanını sıfırlayıp fabrika ayarlarına döndürür."""
    seed_database()
    return {"message": "Veritabanı başarıyla yenilendi"}

