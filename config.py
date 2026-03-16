from __future__ import annotations

import os
from pathlib import Path


class Config:
    BASE_DIR = Path(__file__).resolve().parent
    DATABASE_DIR = BASE_DIR / "database"
    DATABASE_DIR.mkdir(exist_ok=True)

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", f"sqlite:///{DATABASE_DIR / 'crm.sqlite3'}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TEMPLATES_AUTO_RELOAD = True
    QUOTES_BASE_URL = os.getenv("QUOTES_BASE_URL", "http://localhost:5000")
    QR_CODES_DIR = BASE_DIR / "static" / "images" / "qrcodes"
    PDF_EXPORT_FALLBACK_HTML = True
