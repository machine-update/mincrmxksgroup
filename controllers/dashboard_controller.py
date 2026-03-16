from __future__ import annotations

from flask import Blueprint, render_template, request
from flask_login import current_user, login_required
from sqlalchemy import func

from controllers.decorators import role_required
from extensions import db
from models import Client, Project, Quote
from services.analytics_service import build_analytics_payload
from services.search_service import build_search_results


dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@login_required
def index():
    stats = None
    all_projects = Project.query.all()
    if current_user.is_responsable:
        stats = {
            "clients": Client.query.count(),
            "projets_en_cours": sum(1 for project in all_projects if project.effective_status == "En cours"),
            "devis_total": Quote.query.count(),
            "montant_total_devis": float(db.session.query(func.coalesce(func.sum(Quote.montant_total), 0)).scalar() or 0),
        }

    return render_template(
        "dashboard.html",
        stats=stats,
        recent_projects=Project.query.order_by(Project.created_at.desc()).limit(6).all(),
        recent_quotes=Quote.query.order_by(Quote.created_at.desc()).limit(6).all(),
        analytics=build_analytics_payload(),
    )


@dashboard_bp.route("/analytics")
@login_required
@role_required("responsable", "employe")
def analytics():
    return render_template("analytics.html", analytics=build_analytics_payload())


@dashboard_bp.route("/search")
@login_required
def search():
    return render_template("search_results.html", **build_search_results(request.args.get("q", "").strip()))
