from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from extensions import db
from models import Client, Project, Quote, QuoteItem, User


def normalize_client_timestamps() -> None:
    rows = db.session.execute(db.text("SELECT id, created_at, updated_at FROM clients")).mappings().all()

    for row in rows:
        updates: dict[str, str] = {}
        for field in ("created_at", "updated_at"):
            value = row[field]
            if isinstance(value, str) and "/" in value:
                try:
                    normalized = datetime.strptime(value, "%d/%m/%Y").strftime("%Y-%m-%d 00:00:00")
                except ValueError:
                    normalized = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                updates[field] = normalized

        if updates:
            db.session.execute(
                db.text(
                    """
                    UPDATE clients
                    SET created_at = :created_at, updated_at = :updated_at
                    WHERE id = :client_id
                    """
                ),
                {
                    "client_id": row["id"],
                    "created_at": updates.get("created_at", row["created_at"]),
                    "updated_at": updates.get("updated_at", row["updated_at"]),
                },
            )

    db.session.commit()


def seed_data() -> None:
    normalize_client_timestamps()

    if User.query.count() == 0:
        admin = User(nom="Responsable XKSGROUP", email="admin@xks.local", role="responsable")
        admin.set_password("admin123")
        employee = User(nom="Employe XKSGROUP", email="employe@xks.local", role="employe")
        employee.set_password("employe123")
        db.session.add_all([admin, employee])
        db.session.commit()

    if Client.query.count() == 0:
        db.session.add_all(
            [
                Client(
                    nom="Jean Dupont",
                    entreprise="Studio Alpha",
                    email="jean@alpha.com",
                    telephone="0123456789",
                    adresse="Paris",
                ),
                Client(
                    nom="Marie Curie",
                    entreprise="Science Prod",
                    email="marie@science.com",
                    telephone="0987654321",
                    adresse="Lyon",
                ),
            ]
        )
        db.session.commit()

    if Project.query.count() == 0:
        admin_user = User.query.filter_by(role="responsable").first()
        first_client = Client.query.first()
        if admin_user and first_client:
            db.session.add(
                Project(
                    titre="Clip Musical - Summer",
                    type="Clip",
                    statut="En cours",
                    budget=Decimal("4500.00"),
                    date_debut=date(2026, 3, 1),
                    date_fin=date(2026, 3, 15),
                    client_id=first_client.id,
                    user_id=admin_user.id,
                )
            )
            db.session.commit()

    if Quote.query.count() == 0:
        admin_user = User.query.filter_by(role="responsable").first()
        first_client = Client.query.first()
        if admin_user and first_client:
            quote = Quote(
                reference="DEV-DEMO-001",
                montant_total=Decimal("8500.00"),
                statut="Accepte",
                client_id=first_client.id,
                user_id=admin_user.id,
            )
            quote.lignes.extend(
                [
                    QuoteItem(
                        designation="Captation multicamera",
                        quantite=1,
                        prix_unitaire=Decimal("5000.00"),
                        total=Decimal("5000.00"),
                    ),
                    QuoteItem(
                        designation="Montage et etalonnage",
                        quantite=1,
                        prix_unitaire=Decimal("3500.00"),
                        total=Decimal("3500.00"),
                    ),
                ]
            )
            db.session.add(quote)
            db.session.commit()
