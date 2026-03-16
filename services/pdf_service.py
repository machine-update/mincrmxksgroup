from __future__ import annotations

from io import BytesIO

from flask import current_app, render_template, url_for

try:
    from weasyprint import HTML
except ImportError:  # pragma: no cover
    HTML = None


def build_quote_pdf(quote) -> bytes | None:
    if HTML is None:
        return None

    html = render_template(
        "quote_pdf.html",
        quote=quote,
        logo_url=url_for("static", filename="images/logo-xksgroup-original.webp", _external=True),
        qr_code_url=url_for("static", filename=f"images/qrcodes/{quote.qr_code_filename}", _external=True) if quote.qr_code_filename else None,
    )
    buffer = BytesIO()
    try:
        HTML(string=html, base_url=current_app.root_path).write_pdf(buffer)
    except Exception:  # pragma: no cover
        return None
    return buffer.getvalue()
