from __future__ import annotations

from datetime import date, datetime

from ..extensions import db


class Quote(db.Model):
    __tablename__ = "devis"

    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(40), unique=True, nullable=False)
    date_devis = db.Column(db.Date, default=date.today, nullable=False)
    montant_total = db.Column(db.Numeric(12, 2), default=0, nullable=False)
    statut = db.Column(db.String(50), nullable=False, default="Envoye")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    client = db.relationship("Client", back_populates="devis")
    utilisateur = db.relationship("User", back_populates="devis")
    lignes = db.relationship("QuoteItem", back_populates="devis", cascade="all, delete-orphan")
    facture = db.relationship("Invoice", back_populates="devis", uselist=False)


class QuoteItem(db.Model):
    __tablename__ = "devis_items"

    id = db.Column(db.Integer, primary_key=True)
    designation = db.Column(db.String(255), nullable=False)
    quantite = db.Column(db.Integer, nullable=False)
    prix_unitaire = db.Column(db.Numeric(12, 2), nullable=False)
    total = db.Column(db.Numeric(12, 2), nullable=False)

    devis_id = db.Column(db.Integer, db.ForeignKey("devis.id"), nullable=False)
    devis = db.relationship("Quote", back_populates="lignes")
