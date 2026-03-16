from __future__ import annotations

from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(180), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="employe")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    projets = db.relationship("Project", back_populates="utilisateur")
    devis = db.relationship("Quote", back_populates="utilisateur")
    factures = db.relationship("Invoice", back_populates="utilisateur")

    def set_password(self, raw_password: str) -> None:
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password_hash, raw_password)

    @property
    def is_responsable(self) -> bool:
        return self.role == "responsable"
