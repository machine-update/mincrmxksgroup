from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from flask import request
from flask_login import current_user

from ..extensions import db
from ..models import Quote, QuoteItem
from .common_service import parse_date, parse_decimal


def generate_quote_reference() -> str:
    return f"DEV-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"


def build_quote_from_form(quote: Quote | None = None) -> Quote | None:
    client_id = int(request.form.get("client_id", "0") or 0)
    requested_status = request.form.get("statut", "Envoye").strip() or "Envoye"

    if current_user.role == "employe" and requested_status != "Envoye":
        requested_status = "Envoye"

    designations = request.form.getlist("designation[]")
    quantities = request.form.getlist("quantite[]")
    unit_prices = request.form.getlist("prix_unitaire[]")

    rows = []
    for designation_raw, quantity_raw, unit_price_raw in zip(designations, quantities, unit_prices):
        designation = designation_raw.strip()
        quantite = int(quantity_raw or "0")
        prix_unitaire = parse_decimal(unit_price_raw) or Decimal(0)
        if not designation:
            continue
        rows.append(
            {
                "designation": designation,
                "quantite": quantite,
                "prix_unitaire": prix_unitaire,
                "total": Decimal(quantite) * prix_unitaire,
            }
        )

    if client_id <= 0 or not rows:
        return None

    montant_total = sum((row["total"] for row in rows), Decimal(0))

    if quote is None:
        quote = Quote(
            reference=generate_quote_reference(),
            date_devis=parse_date(request.form.get("date_devis")) or date.today(),
            statut=requested_status,
            montant_total=montant_total,
            client_id=client_id,
            user_id=current_user.id,
        )
        db.session.add(quote)
    else:
        quote.date_devis = parse_date(request.form.get("date_devis")) or quote.date_devis
        quote.statut = requested_status
        quote.client_id = client_id
        quote.montant_total = montant_total
        quote.lignes.clear()

    for row in rows:
        quote.lignes.append(
            QuoteItem(
                designation=row["designation"],
                quantite=row["quantite"],
                prix_unitaire=row["prix_unitaire"],
                total=row["total"],
            )
        )

    return quote
