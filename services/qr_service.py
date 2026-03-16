from __future__ import annotations

from pathlib import Path

from flask import current_app

try:
    import qrcode
except ImportError:  # pragma: no cover
    qrcode = None


def ensure_quote_qr(reference: str) -> str | None:
    if qrcode is None:
        return None

    qr_dir = Path(current_app.config["QR_CODES_DIR"])
    qr_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{reference}.png"
    output_path = qr_dir / filename
    if output_path.exists():
        return filename

    quote_url = f"{current_app.config['QUOTES_BASE_URL']}/devis/{reference}"
    image = qrcode.make(quote_url)
    image.save(output_path)
    return filename
