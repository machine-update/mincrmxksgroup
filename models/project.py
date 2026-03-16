from __future__ import annotations

from datetime import date, datetime

from extensions import db


class Project(db.Model):
    __tablename__ = "projets"

    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(180), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    statut = db.Column(db.String(50), nullable=False, default="En attente")
    budget = db.Column(db.Numeric(12, 2), nullable=True)
    date_debut = db.Column(db.Date, nullable=True)
    date_fin = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    client = db.relationship("Client", back_populates="projets")
    utilisateur = db.relationship("User", back_populates="projets")

    @property
    def effective_status(self) -> str:
        today = date.today()

        if self.statut == "Annule":
            return "Annule"

        if self.date_debut and today < self.date_debut:
            return "En attente"

        if self.date_fin and today > self.date_fin:
            return "Termine"

        if self.date_debut and today >= self.date_debut:
            return "En cours"

        return self.statut
