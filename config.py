from __future__ import annotations

import os
from pathlib import Path


def build_database_uri() -> str:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        base_dir = Path(__file__).resolve().parent
        return f"sqlite:///{base_dir / 'database' / 'crm.sqlite3'}"

    # Some hosting providers still expose postgres:// URLs.
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql+psycopg://", 1)

    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)

    return database_url


class Config:
    BASE_DIR = Path(__file__).resolve().parent
    DATABASE_DIR = BASE_DIR / "database"
    DATABASE_DIR.mkdir(exist_ok=True)

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_DATABASE_URI = build_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TEMPLATES_AUTO_RELOAD = True
    QUOTES_BASE_URL = os.getenv("QUOTES_BASE_URL", "http://localhost:5000")
    QR_CODES_DIR = BASE_DIR / "static" / "images" / "qrcodes"
    PDF_EXPORT_FALLBACK_HTML = True
    AUTO_CREATE_SCHEMA = os.getenv("AUTO_CREATE_SCHEMA", "1") == "1"
