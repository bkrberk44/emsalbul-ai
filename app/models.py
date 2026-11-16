from typing import List, Optional
from pydantic import BaseModel, Field

class DecisionBase(BaseModel):
    mahkeme: str = Field(..., description="Yargı Mercii: Yargıtay, Danıştay, AYM, vb.")
    daire: str = Field(..., description="İlgili Daire: 9. Hukuk Dairesi, 2. Ceza Dairesi, vb.")
    esas_no: str = Field(..., description="Esas Numarası: 2023/1234")
    karar_no: str = Field(..., description="Karar Numarası: 2023/5678")
    karar_tarihi: str = Field(..., description="Karar Tarihi (YYYY-MM-DD veya DD.MM.YYYY)")
    hukuk_alani: str = Field(..., description="İş Hukuku, Kira Hukuku, Ceza Hukuku, vb.")
    karar_sonucu: str = Field(..., description="Bozma, Onama, Düzelterek Onama, İptal, vb.")
    ilgili_kanunlar: List[str] = Field(default_factory=list, description="İlgili Kanun Maddeleri (ör. TBK m. 344)")
    baslik: str = Field(..., description="Emsal Karar Özeti Başlığı / Hukuki İlke")
    tam_metin: str = Field(..., description="Kararın Tam Metni")
    kaynak_url: Optional[str] = Field(None, description="Resmi kaynak veya UYAP/Yargıtay bağlantısı")

class Decision(DecisionBase):
    id: int
    created_at: Optional[str] = None

class SearchFilter(BaseModel):
    q: Optional[str] = ""
    mahkeme: Optional[str] = None
    daire: Optional[str] = None
    hukuk_alani: Optional[str] = None
    karar_sonucu: Optional[str] = None
    yil_baslangic: Optional[int] = None
    yil_bitis: Optional[int] = None
    limit: int = 20
    offset: int = 0

class SearchResultItem(BaseModel):
    id: int
    mahkeme: str
    daire: str
    esas_no: str
    karar_no: str
    karar_tarihi: str
    hukuk_alani: str
    karar_sonucu: str
    baslik: str
    snippet: str
    ilgili_kanunlar: List[str]
    kaynak_url: Optional[str]
    score: float = 0.0

class SearchResponse(BaseModel):
    total: int
    results: List[SearchResultItem]
    query: str
    filters_applied: dict

class AISummaryResponse(BaseModel):
    decision_id: int
    baslik: str
    dava_konusu: str
    uyusmazlik: str
    hukuki_gerekce: str
    hukum_ve_sonuc: str
    onemli_ilkeler: List[str]
    ilgili_maddeler: List[str]
