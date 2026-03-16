from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy import func

from extensions import db
from models import Invoice, InvoiceItem, Quote


def generate_invoice_reference() -> str:
    year = date.today().year
    prefix = f"FAC-{year}-"
    existing_count = db.session.query(func.count(Invoice.id)).filter(Invoice.reference.like(f"{prefix}%")).scalar() or 0
    return f"{prefix}{existing_count + 1:04d}"


def create_invoice_from_quote(quote: Quote) -> Invoice:
    if quote.facture:
        return quote.facture

    invoice = Invoice(
        reference=generate_invoice_reference(),
        date_facture=date.today(),
        date_echeance=date.today() + timedelta(days=30),
        montant_total=quote.montant_total,
        statut="Emise",
        client_id=quote.client_id,
        user_id=quote.user_id,
        quote_id=quote.id,
    )
    db.session.add(invoice)

    for line in quote.lignes:
        invoice.lignes.append(
            InvoiceItem(
                designation=line.designation,
                quantite=line.quantite,
                prix_unitaire=line.prix_unitaire,
                total=line.total,
            )
        )

    if quote.statut == "Envoye":
        quote.statut = "Accepte"

    return invoice
