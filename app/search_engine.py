import re
import json
from typing import List, Dict, Any, Optional
from .database import get_connection

def tr_lower(text: str) -> str:
    """Türkçe karakterlere duyarlı küçük harfe dönüştürme."""
    if not text:
        return ""
    translation_table = str.maketrans({
        "İ": "i", "I": "ı", "Ş": "ş", "Ğ": "ğ", "Ü": "ü", "Ö": "ö", "Ç": "ç"
    })
    return text.translate(translation_table).lower()

def highlight_keywords(text: str, keywords: List[str], max_length: int = 240) -> str:
    """Metin içinde anahtar kelimelerin geçtiği yeri bulur, bağlamını keser ve vurgular."""
    if not text:
        return ""
    if not keywords:
        clean = " ".join(text.split())
        return clean[:max_length] + ("..." if len(clean) > max_length else "")

    text_lower = tr_lower(text)
    first_match_idx = -1

    for kw in keywords:
        kw_clean = tr_lower(kw.strip('"*+'))
        if len(kw_clean) >= 2:
            idx = text_lower.find(kw_clean)
            if idx != -1 and (first_match_idx == -1 or idx < first_match_idx):
                first_match_idx = idx

    if first_match_idx == -1:
        first_match_idx = 0

    # Bağlam aralığı belirleme
    start = max(0, first_match_idx - 60)
    end = min(len(text), start + max_length)
    snippet = text[start:end]

    # Baş ve sona üç nokta
    if start > 0:
        snippet = "..." + snippet
    if end < len(text):
        snippet = snippet + "..."

    # Vurgulama (<mark>)
    for kw in sorted(keywords, key=len, reverse=True):
        kw_clean = kw.strip('"*+').strip()
        if len(kw_clean) >= 2:
            pattern = re.compile(re.escape(kw_clean), re.IGNORECASE)
            snippet = pattern.sub(r'<mark class="bg-amber-200 text-amber-900 font-semibold px-1 rounded">\g<0></mark>', snippet)

    return snippet

def execute_search(
    query: str = "",
    mahkeme: Optional[str] = None,
    daire: Optional[str] = None,
    hukuk_alani: Optional[str] = None,
    karar_sonucu: Optional[str] = None,
    yil_baslangic: Optional[int] = None,
    yil_bitis: Optional[int] = None,
    limit: int = 20,
    offset: int = 0
) -> Dict[str, Any]:
    """Tam metin ve filtreli akıllı emsal karar arama motoru."""
    conn = get_connection()
    cursor = conn.cursor()

    q_clean = query.strip()
    keywords = [k for k in re.split(r'\s+', q_clean) if len(k) > 1] if q_clean else []

    base_sql = "SELECT id, mahkeme, daire, esas_no, karar_no, karar_tarihi, hukuk_alani, karar_sonucu, ilgili_kanunlar, baslik, tam_metin, kaynak_url"
    where_clauses = []
    params = []

    # 1. Tam Metin Arama (FTS5 veya LIKE fallback)
    if q_clean:
        # FTS5 match query hazırlığı
        sanitized_terms = []
        for word in q_clean.replace("'", " ").replace('"', ' ').split():
            clean_word = re.sub(r'[^\w\d]', '', word)
            if clean_word:
                sanitized_terms.append(f"{clean_word}*")

        fts_query = " ".join(sanitized_terms)

        try:
            # FTS5 eşleşmesi dene
            fts_check = "SELECT rowid, rank FROM decisions_fts WHERE decisions_fts MATCH ? ORDER BY rank"
            cursor.execute(fts_check, (fts_query,))
            fts_rows = cursor.fetchall()
            matched_ids = [r[0] for r in fts_rows]

            if matched_ids:
                placeholders = ",".join("?" for _ in matched_ids)
                where_clauses.append(f"id IN ({placeholders})")
                params.extend(matched_ids)
            else:
                # FTS ile bulunamadıysa LIKE fallback
                like_conditions = []
                for kw in keywords:
                    like_conditions.append("(baslik LIKE ? OR tam_metin LIKE ? OR esas_no LIKE ? OR karar_no LIKE ? OR ilgili_kanunlar LIKE ?)")
                    kw_wildcard = f"%{kw}%"
                    params.extend([kw_wildcard, kw_wildcard, kw_wildcard, kw_wildcard, kw_wildcard])
                if like_conditions:
                    where_clauses.append(f"({' AND '.join(like_conditions)})")
        except Exception:
            # Herhangi bir FTS sözdizim hatasında güvenli LIKE
            like_conditions = []
            for kw in keywords:
                like_conditions.append("(baslik LIKE ? OR tam_metin LIKE ? OR esas_no LIKE ? OR karar_no LIKE ? OR ilgili_kanunlar LIKE ?)")
                kw_wildcard = f"%{kw}%"
                params.extend([kw_wildcard, kw_wildcard, kw_wildcard, kw_wildcard, kw_wildcard])
            if like_conditions:
                where_clauses.append(f"({' AND '.join(like_conditions)})")

    # 2. Mahkeme Filtresi
    if mahkeme and mahkeme.lower() != "tümü":
        where_clauses.append("mahkeme = ?")
        params.append(mahkeme)

    # 3. Daire Filtresi
    if daire and daire.lower() != "tümü":
        where_clauses.append("daire = ?")
        params.append(daire)

    # 4. Hukuk Alanı Filtresi
    if hukuk_alani and hukuk_alani.lower() != "tümü":
        where_clauses.append("hukuk_alani = ?")
        params.append(hukuk_alani)

    # 5. Karar Sonucu Filtresi
    if karar_sonucu and karar_sonucu.lower() != "tümü":
        where_clauses.append("karar_sonucu = ?")
        params.append(karar_sonucu)

    # 6. Yıl Filtresi
    if yil_baslangic:
        where_clauses.append("CAST(SUBSTR(karar_tarihi, -4) AS INTEGER) >= ?")
        params.append(yil_baslangic)
    if yil_bitis:
        where_clauses.append("CAST(SUBSTR(karar_tarihi, -4) AS INTEGER) <= ?")
        params.append(yil_bitis)

    where_sql = f" WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    # Toplam sayı
    count_sql = f"SELECT COUNT(*) FROM decisions{where_sql}"
    cursor.execute(count_sql, tuple(params))
    total_count = cursor.fetchone()[0]

    # Sonuçları çek
    final_sql = f"{base_sql} FROM decisions{where_sql} ORDER BY id DESC LIMIT ? OFFSET ?"
    query_params = list(params)
    query_params.extend([limit, offset])

    cursor.execute(final_sql, tuple(query_params))
    rows = cursor.fetchall()

    results = []
    for r in rows:
        row_dict = dict(r)
        try:
            kanunlar = json.loads(row_dict["ilgili_kanunlar"])
        except Exception:
            kanunlar = [row_dict["ilgili_kanunlar"]] if row_dict["ilgili_kanunlar"] else []

        snippet = highlight_keywords(row_dict["tam_metin"], keywords, max_length=240)

        # Basit alaka skoru hesaplama
        score = 1.0
        if q_clean:
            q_low = tr_lower(q_clean)
            if q_low in tr_lower(row_dict["esas_no"]) or q_low in tr_lower(row_dict["karar_no"]):
                score += 50.0
            if q_low in tr_lower(row_dict["baslik"]):
                score += 25.0
            for k in kanunlar:
                if q_low in tr_lower(k):
                    score += 15.0

        results.append({
            "id": row_dict["id"],
            "mahkeme": row_dict["mahkeme"],
            "daire": row_dict["daire"],
            "esas_no": row_dict["esas_no"],
            "karar_no": row_dict["karar_no"],
            "karar_tarihi": row_dict["karar_tarihi"],
            "hukuk_alani": row_dict["hukuk_alani"],
            "karar_sonucu": row_dict["karar_sonucu"],
            "baslik": row_dict["baslik"],
            "snippet": snippet,
            "ilgili_kanunlar": kanunlar,
            "kaynak_url": row_dict.get("kaynak_url"),
            "score": score
        })

    # Eğer arama yapılmışsa skora göre sırala
    if q_clean:
        results.sort(key=lambda x: x["score"], reverse=True)

    conn.close()

    return {
        "total": total_count,
        "results": results,
        "query": query,
        "filters_applied": {
            "mahkeme": mahkeme,
            "daire": daire,
            "hukuk_alani": hukuk_alani,
            "karar_sonucu": karar_sonucu,
            "yil_baslangic": yil_baslangic,
            "yil_bitis": yil_bitis
        }
    }
