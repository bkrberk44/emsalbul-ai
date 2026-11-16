import sys
import os

# Windows konsolunda UTF-8 çıktısı sağlamak
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

import uvicorn

if __name__ == "__main__":
    print("=" * 65)
    print("EmsalBul.AI - Turkiye Emsal Karar Arama ve AI Analiz Motoru")
    print("Web Arayuzu:        http://127.0.0.1:8000")
    print("Swagger API Docs:   http://127.0.0.1:8000/docs")
    print("=" * 65)
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)
