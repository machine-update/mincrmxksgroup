from __future__ import annotations

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_

from ..decorators import role_required
from ..extensions import db
from ..models import Client, Project
from ..services.common_service import parse_date, parse_decimal


def register_project_routes(app) -> None:
    @app.route("/projects")
    @login_required
    def projects_list():
        q = request.args.get("q", "").strip()
        query = Project.query.join(Client)
        if q:
            like_q = f"%{q}%"
            query = query.filter(or_(Project.titre.ilike(like_q), Client.nom.ilike(like_q)))
        return render_template("projects.html", projects=query.order_by(Project.created_at.desc()).all(), q=q)

    @app.route("/projects/new", methods=["GET", "POST"])
    @login_required
    @role_required("responsable", "employe")
    def projects_new():
        clients = Client.query.order_by(Client.nom.asc()).all()
        if request.method == "POST":
            project = Project(
                titre=request.form.get("titre", "").strip(),
                type=request.form.get("type", "Clip").strip() or "Clip",
                statut=request.form.get("statut", "En attente").strip() or "En attente",
                budget=parse_decimal(request.form.get("budget")),
                date_debut=parse_date(request.form.get("date_debut")),
                date_fin=parse_date(request.form.get("date_fin")),
                client_id=int(request.form.get("client_id", "0") or 0),
                user_id=current_user.id,
            )
            if not project.titre or project.client_id <= 0:
                flash("Titre et client sont obligatoires.", "danger")
                return render_template("project_form.html", project=None, clients=clients)

            db.session.add(project)
            db.session.commit()
            flash("Projet cree.", "success")
            return redirect(url_for("projects_list"))

        return render_template("project_form.html", project=None, clients=clients)

    @app.route("/projects/<int:project_id>/edit", methods=["GET", "POST"])
    @login_required
    @role_required("responsable", "employe")
    def projects_edit(project_id: int):
        project = db.session.get(Project, project_id)
        if not project:
            flash("Projet introuvable.", "danger")
            return redirect(url_for("projects_list"))

        clients = Client.query.order_by(Client.nom.asc()).all()
        if request.method == "POST":
            project.titre = request.form.get("titre", "").strip()
            project.type = request.form.get("type", "Clip").strip()
            project.statut = request.form.get("statut", "En attente").strip()
            project.budget = parse_decimal(request.form.get("budget"))
            project.date_debut = parse_date(request.form.get("date_debut"))
            project.date_fin = parse_date(request.form.get("date_fin"))
            project.client_id = int(request.form.get("client_id", "0") or 0)

            if not project.titre or project.client_id <= 0:
                flash("Titre et client sont obligatoires.", "danger")
                return render_template("project_form.html", project=project, clients=clients)

            db.session.commit()
            flash("Projet mis a jour.", "success")
            return redirect(url_for("projects_list"))

        return render_template("project_form.html", project=project, clients=clients)

    @app.route("/projects/<int:project_id>/delete", methods=["POST"])
    @login_required
    @role_required("responsable")
    def projects_delete(project_id: int):
        project = db.session.get(Project, project_id)
        if not project:
            flash("Projet introuvable.", "danger")
            return redirect(url_for("projects_list"))

        db.session.delete(project)
        db.session.commit()
        flash("Projet supprime.", "info")
        return redirect(url_for("projects_list"))
