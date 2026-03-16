from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from controllers.decorators import role_required
from extensions import db
from models import User


users_bp = Blueprint("users", __name__)


@users_bp.route("/users")
@login_required
@role_required("responsable")
def list():
    page = request.args.get("page", 1, type=int)
    pagination = User.query.order_by(User.created_at.asc()).paginate(page=page, per_page=10, error_out=False)
    return render_template("users.html", users=pagination.items, pagination=pagination, pagination_args={})


@users_bp.route("/users/new", methods=["GET", "POST"])
@login_required
@role_required("responsable")
def create():
    if request.method == "POST":
        nom = request.form.get("nom", "").strip()
        email = request.form.get("email", "").strip().lower()
        role = request.form.get("role", "employe")
        password = request.form.get("password", "").strip()

        if not nom or not email or not password:
            flash("Nom, email et mot de passe sont obligatoires.", "danger")
            return render_template("user_form.html", user=None)

        if User.query.filter_by(email=email).first():
            flash("Un utilisateur existe deja avec cet email.", "danger")
            return render_template("user_form.html", user=None)

        user = User(nom=nom, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("Utilisateur cree.", "success")
        return redirect(url_for("users.list"))

    return render_template("user_form.html", user=None)


@users_bp.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("responsable")
def edit(user_id: int):
    user = db.session.get(User, user_id)
    if not user:
        flash("Utilisateur introuvable.", "danger")
        return redirect(url_for("users.list"))

    if request.method == "POST":
        user.nom = request.form.get("nom", "").strip()
        requested_email = request.form.get("email", "").strip().lower()
        user.role = request.form.get("role", "employe")

        new_password = request.form.get("password", "").strip()
        if new_password:
            user.set_password(new_password)

        if not user.nom or not requested_email:
            flash("Nom et email sont obligatoires.", "danger")
            return render_template("user_form.html", user=user)

        existing_user = User.query.filter(User.email == requested_email, User.id != user.id).first()
        if existing_user:
            flash("Un utilisateur existe deja avec cet email.", "danger")
            return render_template("user_form.html", user=user)

        user.email = requested_email

        db.session.commit()
        flash("Utilisateur mis a jour.", "success")
        return redirect(url_for("users.list"))

    return render_template("user_form.html", user=user)


@users_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@login_required
@role_required("responsable")
def delete(user_id: int):
    if current_user.id == user_id:
        flash("Suppression de ton propre compte interdite.", "danger")
        return redirect(url_for("users.list"))

    user = db.session.get(User, user_id)
    if not user:
        flash("Utilisateur introuvable.", "danger")
        return redirect(url_for("users.list"))

    db.session.delete(user)
    db.session.commit()
    flash("Utilisateur supprime.", "info")
    return redirect(url_for("users.list"))
