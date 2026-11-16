import sqlite3
import json
import os
from typing import List, Optional, Dict, Any
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "emsal_kararlar.db"

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Veritabanını ve FTS5 tam metin arama dizinini oluşturur."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS decisions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mahkeme TEXT NOT NULL,
        daire TEXT NOT NULL,
        esas_no TEXT NOT NULL,
        karar_no TEXT NOT NULL,
        karar_tarihi TEXT NOT NULL,
        hukuk_alani TEXT NOT NULL,
        karar_sonucu TEXT NOT NULL,
        ilgili_kanunlar TEXT,
        baslik TEXT NOT NULL,
        tam_metin TEXT NOT NULL,
        kaynak_url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Varsa eski mükerrer kayıtları temizle (her benzersiz daire-esas-karar için sadece birini tut)
    try:
        cursor.execute("""
        DELETE FROM decisions
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM decisions
            GROUP BY daire, esas_no, karar_no
        );
        """)
        conn.commit()
    except Exception:
        pass

    # Tekillik İndeksi (Aynı Daire, Esas No ve Karar No'ya sahip mükerrer kayıtları engeller)
    try:
        cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_decisions_unique ON decisions(daire, esas_no, karar_no);
        """)
        conn.commit()
    except Exception:
        pass

    # FTS5 Sanal Tablosu (Full-Text Search)
    cursor.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS decisions_fts USING fts5(
        baslik,
        tam_metin,
        ilgili_kanunlar,
        daire,
        esas_no,
        karar_no,
        content='decisions',
        content_rowid='id',
        tokenize='unicode61 remove_diacritics 2'
    );
    """)

    # FTS5 Senkronizasyon Tetikleyicileri (Triggers)
    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS decisions_ai AFTER INSERT ON decisions BEGIN
        INSERT INTO decisions_fts(rowid, baslik, tam_metin, ilgili_kanunlar, daire, esas_no, karar_no)
        VALUES (new.id, new.baslik, new.tam_metin, new.ilgili_kanunlar, new.daire, new.esas_no, new.karar_no);
    END;
    """)

    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS decisions_ad AFTER DELETE ON decisions BEGIN
        INSERT INTO decisions_fts(decisions_fts, rowid, baslik, tam_metin, ilgili_kanunlar, daire, esas_no, karar_no)
        VALUES ('delete', old.id, old.baslik, old.tam_metin, old.ilgili_kanunlar, old.daire, old.esas_no, old.karar_no);
    END;
    """)

    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS decisions_au AFTER UPDATE ON decisions BEGIN
        INSERT INTO decisions_fts(decisions_fts, rowid, baslik, tam_metin, ilgili_kanunlar, daire, esas_no, karar_no)
        VALUES ('delete', old.id, old.baslik, old.tam_metin, old.ilgili_kanunlar, old.daire, old.esas_no, old.karar_no);
        INSERT INTO decisions_fts(rowid, baslik, tam_metin, ilgili_kanunlar, daire, esas_no, karar_no)
        VALUES (new.id, new.baslik, new.tam_metin, new.ilgili_kanunlar, new.daire, new.esas_no, new.karar_no);
    END;
    """)

    conn.commit()
    conn.close()

def insert_decision(decision_data: Dict[str, Any], return_is_new: bool = False):
    conn = get_connection()
    cursor = conn.cursor()

    daire = str(decision_data.get("daire", "")).strip()
    esas_no = str(decision_data.get("esas_no", "")).strip()
    karar_no = str(decision_data.get("karar_no", "")).strip()

    # 1. Mükerrer Karar Kontrolü (Daire, Esas No ve Karar No aynıysa tekrar ekleme)
    if daire and esas_no and karar_no:
        cursor.execute(
            "SELECT id FROM decisions WHERE daire = ? AND esas_no = ? AND karar_no = ?",
            (daire, esas_no, karar_no)
        )
        existing = cursor.fetchone()
        if existing:
            conn.close()
            existing_id = existing["id"]
            return (existing_id, False) if return_is_new else existing_id

    kanunlar = decision_data.get("ilgili_kanunlar", [])
    if isinstance(kanunlar, list):
        kanunlar_str = json.dumps(kanunlar, ensure_ascii=False)
    else:
        kanunlar_str = str(kanunlar)

    cursor.execute("""
    INSERT INTO decisions (
        mahkeme, daire, esas_no, karar_no, karar_tarihi,
        hukuk_alani, karar_sonucu, ilgili_kanunlar, baslik, tam_metin, kaynak_url
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        decision_data["mahkeme"],
        daire,
        esas_no,
        karar_no,
        decision_data["karar_tarihi"],
        decision_data["hukuk_alani"],
        decision_data["karar_sonucu"],
        kanunlar_str,
        decision_data["baslik"],
        decision_data["tam_metin"],
        decision_data.get("kaynak_url", "")
    ))

    inserted_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return (inserted_id, True) if return_is_new else inserted_id

def decision_exists(daire: str, esas_no: str, karar_no: str) -> bool:
    """Belirtilen daire, esas ve karar numarasına sahip kararın veritabanında olup olmadığını kontrol eder."""
    if not (daire and esas_no and karar_no):
        return False
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM decisions WHERE daire = ? AND esas_no = ? AND karar_no = ? LIMIT 1",
        (daire.strip(), esas_no.strip(), karar_no.strip())
    )
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def get_decision_by_id(decision_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM decisions WHERE id = ?", (decision_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None

    data = dict(row)
    try:
        data["ilgili_kanunlar"] = json.loads(data["ilgili_kanunlar"])
    except Exception:
        data["ilgili_kanunlar"] = [data["ilgili_kanunlar"]] if data["ilgili_kanunlar"] else []
    return data

def get_db_stats() -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM decisions")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT mahkeme, COUNT(*) FROM decisions GROUP BY mahkeme")
    by_mahkeme = {row[0]: row[1] for row in cursor.fetchall()}

    cursor.execute("SELECT hukuk_alani, COUNT(*) FROM decisions GROUP BY hukuk_alani")
    by_alan = {row[0]: row[1] for row in cursor.fetchall()}

    cursor.execute("SELECT DISTINCT daire FROM decisions ORDER BY daire")
    daireler = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT DISTINCT karar_sonucu FROM decisions ORDER BY karar_sonucu")
    sonuclar = [row[0] for row in cursor.fetchall()]

    conn.close()
    return {
        "total_karar": total,
        "by_mahkeme": by_mahkeme,
        "by_alan": by_alan,
        "daireler": daireler,
        "sonuclar": sonuclar
    }
