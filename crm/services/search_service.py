from __future__ import annotations

from sqlalchemy import or_

from ..models import Client, Invoice, Project, Quote


def build_search_results(search_term: str) -> dict:
    clients = []
    projects = []
    quotes = []
    invoices = []

    if search_term:
        like_q = f"%{search_term}%"
        clients = (
            Client.query.filter(
                or_(
                    Client.nom.ilike(like_q),
                    Client.entreprise.ilike(like_q),
                    Client.email.ilike(like_q),
                )
            )
            .order_by(Client.updated_at.desc())
            .limit(10)
            .all()
        )
        projects = (
            Project.query.join(Client)
            .filter(
                or_(
                    Project.titre.ilike(like_q),
                    Project.type.ilike(like_q),
                    Client.nom.ilike(like_q),
                )
            )
            .order_by(Project.updated_at.desc())
            .limit(10)
            .all()
        )
        quotes = (
            Quote.query.join(Client)
            .filter(
                or_(
                    Quote.reference.ilike(like_q),
                    Quote.statut.ilike(like_q),
                    Client.nom.ilike(like_q),
                )
            )
            .order_by(Quote.updated_at.desc())
            .limit(10)
            .all()
        )
        invoices = (
            Invoice.query.join(Client)
            .filter(
                or_(
                    Invoice.reference.ilike(like_q),
                    Invoice.statut.ilike(like_q),
                    Client.nom.ilike(like_q),
                )
            )
            .order_by(Invoice.updated_at.desc())
            .limit(10)
            .all()
        )

    return {
        "q": search_term,
        "clients": clients,
        "projects": projects,
        "quotes": quotes,
        "invoices": invoices,
    }
