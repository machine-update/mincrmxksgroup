from __future__ import annotations

from datetime import date, datetime, timedelta

from extensions import db


class Invoice(db.Model):
    __tablename__ = "factures"

    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(40), unique=True, nullable=False)
    date_facture = db.Column(db.Date, default=date.today, nullable=False)
    date_echeance = db.Column(db.Date, default=lambda: date.today() + timedelta(days=30), nullable=False)
    montant_total = db.Column(db.Numeric(12, 2), default=0, nullable=False)
    statut = db.Column(db.String(50), nullable=False, default="Emise")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    quote_id = db.Column(db.Integer, db.ForeignKey("devis.id"), nullable=True, unique=True)

    client = db.relationship("Client", back_populates="factures")
    utilisateur = db.relationship("User", back_populates="factures")
    devis = db.relationship("Quote", back_populates="facture")
    lignes = db.relationship("InvoiceItem", back_populates="facture", cascade="all, delete-orphan")

    @property
    def tax_rate(self) -> float:
        return 0.2

    @property
    def subtotal_ht(self) -> float:
        return float(self.montant_total or 0)

    @property
    def tax_amount(self) -> float:
        return round(self.subtotal_ht * self.tax_rate, 2)

    @property
    def total_ttc(self) -> float:
        return round(self.subtotal_ht + self.tax_amount, 2)


class InvoiceItem(db.Model):
    __tablename__ = "factures_items"

    id = db.Column(db.Integer, primary_key=True)
    designation = db.Column(db.String(255), nullable=False)
    quantite = db.Column(db.Integer, nullable=False)
    prix_unitaire = db.Column(db.Numeric(12, 2), nullable=False)
    total = db.Column(db.Numeric(12, 2), nullable=False)

    facture_id = db.Column(db.Integer, db.ForeignKey("factures.id"), nullable=False)
    facture = db.relationship("Invoice", back_populates="lignes")
