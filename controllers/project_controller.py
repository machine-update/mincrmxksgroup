from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_

from controllers.decorators import role_required
from extensions import db
from models import Client, Project
from services.common_service import parse_date, parse_decimal


projects_bp = Blueprint("projects", __name__)


@projects_bp.route("/projects")
@login_required
def list():
    q = request.args.get("q", "").strip()
    page = request.args.get("page", 1, type=int)
    query = Project.query.join(Client)
    if q:
        like_q = f"%{q}%"
        query = query.filter(or_(Project.titre.ilike(like_q), Client.nom.ilike(like_q)))
    pagination = query.order_by(Project.created_at.desc()).paginate(page=page, per_page=9, error_out=False)
    return render_template(
        "projects/list.html",
        projects=pagination.items,
        pagination=pagination,
        pagination_args={"q": q},
        q=q,
    )


@projects_bp.route("/projects/new", methods=["GET", "POST"])
@login_required
@role_required("responsable", "employe")
def create():
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
            return render_template("projects/create.html", project=None, clients=clients)

        if project.statut not in {"En attente", "En cours", "Termine", "Annule"}:
            project.statut = "En attente"

        db.session.add(project)
        db.session.commit()
        flash("Projet cree.", "success")
        return redirect(url_for("projects.list"))

    return render_template("projects/create.html", project=None, clients=clients)


@projects_bp.route("/projects/<int:project_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("responsable", "employe")
def edit(project_id: int):
    project = db.session.get(Project, project_id)
    if not project:
        flash("Projet introuvable.", "danger")
        return redirect(url_for("projects.list"))

    clients = Client.query.order_by(Client.nom.asc()).all()
    if request.method == "POST":
        project.titre = request.form.get("titre", "").strip()
        project.type = request.form.get("type", "Clip").strip()
        project.statut = request.form.get("statut", "En attente").strip()
        project.budget = parse_decimal(request.form.get("budget"))
        project.date_debut = parse_date(request.form.get("date_debut"))
        project.date_fin = parse_date(request.form.get("date_fin"))
        project.client_id = int(request.form.get("client_id", "0") or 0)

        if project.statut not in {"En attente", "En cours", "Termine", "Annule"}:
            project.statut = "En attente"

        if not project.titre or project.client_id <= 0:
            flash("Titre et client sont obligatoires.", "danger")
            return render_template("projects/edit.html", project=project, clients=clients)

        db.session.commit()
        flash("Projet mis a jour.", "success")
        return redirect(url_for("projects.list"))

    return render_template("projects/edit.html", project=project, clients=clients)


@projects_bp.route("/projects/<int:project_id>/delete", methods=["POST"])
@login_required
@role_required("responsable")
def delete(project_id: int):
    project = db.session.get(Project, project_id)
    if not project:
        flash("Projet introuvable.", "danger")
        return redirect(url_for("projects.list"))

    db.session.delete(project)
    db.session.commit()
    flash("Projet supprime.", "info")
    return redirect(url_for("projects.list"))
