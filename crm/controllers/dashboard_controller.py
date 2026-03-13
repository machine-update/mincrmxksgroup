from __future__ import annotations

from flask import render_template, request
from flask_login import current_user, login_required

from ..decorators import role_required
from ..models import Client, Project, Quote
from ..services.analytics_service import build_analytics_payload
from ..services.search_service import build_search_results


def register_dashboard_routes(app) -> None:
    @app.route("/dashboard")
    @login_required
    def dashboard():
        stats = None
        all_projects = Project.query.all()
        if current_user.is_responsable:
            stats = {
                "clients": Client.query.count(),
                "projets_en_cours": sum(1 for project in all_projects if project.effective_status == "En cours"),
                "devis_total": Quote.query.count(),
                "devis_envoyes": Quote.query.filter_by(statut="Envoye").count(),
            }

        return render_template(
            "dashboard.html",
            stats=stats,
            recent_projects=Project.query.order_by(Project.created_at.desc()).limit(6).all(),
            recent_quotes=Quote.query.order_by(Quote.created_at.desc()).limit(6).all(),
            analytics=build_analytics_payload(),
        )

    @app.route("/analytics")
    @login_required
    @role_required("responsable", "employe")
    def analytics_view():
        return render_template("analytics.html", analytics=build_analytics_payload())

    @app.route("/search")
    @login_required
    def global_search():
        return render_template("search_results.html", **build_search_results(request.args.get("q", "").strip()))
