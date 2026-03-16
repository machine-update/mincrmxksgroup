from __future__ import annotations

from datetime import datetime

from extensions import db


class Client(db.Model):
    __tablename__ = "clients"

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(120), nullable=False)
    entreprise = db.Column(db.String(180), nullable=True)
    email = db.Column(db.String(180), nullable=False)
    telephone = db.Column(db.String(60), nullable=True)
    adresse = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    projets = db.relationship("Project", back_populates="client", cascade="all, delete-orphan")
    devis = db.relationship("Quote", back_populates="client", cascade="all, delete-orphan")
    factures = db.relationship("Invoice", back_populates="client", cascade="all, delete-orphan")
