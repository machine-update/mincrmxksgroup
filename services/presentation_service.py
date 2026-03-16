from __future__ import annotations

from decimal import Decimal

from flask import url_for
from flask_login import current_user

from models import Project, Quote


def inject_notification_items():
    if not current_user.is_authenticated:
        return {"notification_items": [], "notification_count": 0}

    recent_projects = Project.query.order_by(Project.updated_at.desc()).limit(4).all()
    recent_quotes = Quote.query.order_by(Quote.updated_at.desc()).limit(4).all()

    items = []
    for project in recent_projects:
        items.append(
            {
                "title": f"Projet: {project.titre}",
                "detail": f"{project.client.nom} - {project.effective_status}",
                "at": project.updated_at,
                "icon": "bi-diagram-3",
                "href": url_for("projects.edit", project_id=project.id),
            }
        )
    for quote in recent_quotes:
        items.append(
            {
                "title": f"Devis: {quote.reference}",
                "detail": f"{quote.client.nom} - {quote.statut}",
                "at": quote.updated_at,
                "icon": "bi-receipt",
                "href": url_for("devis.edit", quote_id=quote.id),
            }
        )

    items.sort(key=lambda item: item["at"], reverse=True)
    items = items[:6]
    return {"notification_items": items, "notification_count": len(items)}


def money_filter(value):
    amount = Decimal(value or 0)
    formatted = f"{amount:,.2f}".replace(",", " ").replace(".", ",")
    return f"{formatted} EUR"


def status_badge_class(status: str) -> str:
    mapping = {
        "En attente": "wait",
        "En cours": "progress",
        "Termine": "done",
        "Annule": "other",
        "Brouillon": "wait",
        "Envoye": "progress",
        "Accepte": "done",
        "Refuse": "other",
        "Payee": "done",
        "Annulee": "other",
        "Emise": "progress",
    }
    return mapping.get(status, "other")


def pagination_url(endpoint: str, page: int, args: dict | None = None) -> str:
    payload = {key: value for key, value in (args or {}).items() if value not in (None, "")}
    payload["page"] = page
    return url_for(endpoint, **payload)


def register_template_helpers(app) -> None:
    app.context_processor(inject_notification_items)
    app.template_filter("money")(money_filter)
    app.template_filter("status_badge_class")(status_badge_class)
    app.jinja_env.globals["pagination_url"] = pagination_url
