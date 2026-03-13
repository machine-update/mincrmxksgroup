from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import func

from ..extensions import db
from ..models import Client, Project, Quote


def _month_back(year: int, month: int) -> tuple[int, int]:
    if month == 1:
        return year - 1, 12
    return year, month - 1


def build_analytics_payload() -> dict:
    month_labels = ["Jan", "Fev", "Mar", "Avr", "Mai", "Jun", "Jul", "Aou", "Sep", "Oct", "Nov", "Dec"]
    now = date.today()
    buckets: list[tuple[int, int]] = []
    year, month = now.year, now.month
    for _ in range(6):
        buckets.append((year, month))
        year, month = _month_back(year, month)
    buckets.reverse()

    by_month: dict[str, float] = {f"{year:04d}-{month:02d}": 0.0 for year, month in buckets}
    start_year, start_month = buckets[0]
    window_start = datetime(start_year, start_month, 1)

    recent_quotes = Quote.query.filter(Quote.created_at >= window_start).all()
    for quote in recent_quotes:
        key = quote.created_at.strftime("%Y-%m")
        if key in by_month:
            by_month[key] += float(quote.montant_total or 0)

    trend_labels = [f"{month_labels[month - 1]} {str(year)[2:]}" for year, month in buckets]
    trend_values = [round(by_month[f"{year:04d}-{month:02d}"], 2) for year, month in buckets]

    all_projects = Project.query.all()
    all_quotes = Quote.query.all()
    project_status_labels = ["En attente", "En cours", "Termine"]
    project_status_values = [sum(1 for project in all_projects if project.effective_status == status) for status in project_status_labels]

    quote_status_labels = ["Envoye", "Accepte", "Refuse"]
    quote_status_values = [Quote.query.filter_by(statut=status).count() for status in quote_status_labels]

    top_clients_raw = (
        db.session.query(
            Client.nom.label("nom"),
            func.coalesce(func.sum(Quote.montant_total), 0).label("montant"),
        )
        .join(Quote, Quote.client_id == Client.id)
        .group_by(Client.id)
        .order_by(func.sum(Quote.montant_total).desc())
        .limit(5)
        .all()
    )

    ca_total = float(db.session.query(func.coalesce(func.sum(Quote.montant_total), 0)).scalar() or 0)
    budget_total = float(db.session.query(func.coalesce(func.sum(Project.budget), 0)).scalar() or 0)
    clients_actifs = db.session.query(func.count(func.distinct(Client.id))).join(Project).scalar() or 0
    projets_termines = sum(1 for project in all_projects if project.effective_status == "Termine")
    projets_en_cours = sum(1 for project in all_projects if project.effective_status == "En cours")
    projets_en_attente = sum(1 for project in all_projects if project.effective_status == "En attente")

    devis_total = len(all_quotes)
    devis_acceptes = sum(1 for quote in all_quotes if quote.statut == "Accepte")
    acceptance_rate = round((devis_acceptes / devis_total) * 100, 1) if devis_total else 0.0
    average_quote_value = round(ca_total / devis_total, 2) if devis_total else 0.0
    delivery_rate = round((projets_termines / len(all_projects)) * 100, 1) if all_projects else 0.0
    production_load = round((projets_en_cours / len(all_projects)) * 100, 1) if all_projects else 0.0
    top_client_share = round(((float(top_clients_raw[0].montant) if top_clients_raw else 0.0) / ca_total) * 100, 1) if ca_total else 0.0

    current_month_value = trend_values[-1] if trend_values else 0.0
    previous_month_value = trend_values[-2] if len(trend_values) > 1 else 0.0
    if previous_month_value:
        revenue_growth = round(((current_month_value - previous_month_value) / previous_month_value) * 100, 1)
    else:
        revenue_growth = 100.0 if current_month_value else 0.0

    upcoming_deadlines = [
        {
            "title": project.titre,
            "client": project.client.nom,
            "date_fin": project.date_fin.strftime("%d/%m/%Y") if project.date_fin else "-",
            "status": project.effective_status,
            "budget": float(project.budget or 0),
        }
        for project in sorted(
            [project for project in all_projects if project.date_fin and project.effective_status != "Termine"],
            key=lambda project: project.date_fin,
        )[:4]
    ]

    top_clients = [
        {
            "name": row.nom,
            "amount": float(row.montant or 0),
            "share": round(((float(row.montant or 0) / ca_total) * 100), 1) if ca_total else 0.0,
        }
        for row in top_clients_raw
    ]

    return {
        "trend_labels": trend_labels,
        "trend_values": trend_values,
        "project_status_labels": project_status_labels,
        "project_status_values": project_status_values,
        "quote_status_labels": quote_status_labels,
        "quote_status_values": quote_status_values,
        "top_clients_labels": [row["name"] for row in top_clients],
        "top_clients_values": [row["amount"] for row in top_clients],
        "top_clients": top_clients,
        "upcoming_deadlines": upcoming_deadlines,
        "insights": {
            "revenue_growth": revenue_growth,
            "average_quote_value": average_quote_value,
            "acceptance_rate": acceptance_rate,
            "production_load": production_load,
            "top_client_share": top_client_share,
            "delivery_rate": delivery_rate,
        },
        "kpi_extra": {
            "ca_total": ca_total,
            "budget_total": budget_total,
            "clients_actifs": clients_actifs,
            "projets_termines": projets_termines,
            "projets_total": len(all_projects),
            "devis_total": devis_total,
            "projets_en_cours": projets_en_cours,
            "projets_en_attente": projets_en_attente,
        },
        "generated_at": datetime.now().strftime("%d/%m/%Y a %H:%M"),
    }
