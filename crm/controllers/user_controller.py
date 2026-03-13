from __future__ import annotations

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ..decorators import role_required
from ..extensions import db
from ..models import User


def register_user_routes(app) -> None:
    @app.route("/users")
    @login_required
    @role_required("responsable")
    def users_list():
        return render_template("users.html", users=User.query.order_by(User.created_at.asc()).all())

    @app.route("/users/new", methods=["GET", "POST"])
    @login_required
    @role_required("responsable")
    def users_new():
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
            return redirect(url_for("users_list"))

        return render_template("user_form.html", user=None)

    @app.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
    @login_required
    @role_required("responsable")
    def users_edit(user_id: int):
        user = db.session.get(User, user_id)
        if not user:
            flash("Utilisateur introuvable.", "danger")
            return redirect(url_for("users_list"))

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
            return redirect(url_for("users_list"))

        return render_template("user_form.html", user=user)

    @app.route("/users/<int:user_id>/delete", methods=["POST"])
    @login_required
    @role_required("responsable")
    def users_delete(user_id: int):
        if current_user.id == user_id:
            flash("Suppression de ton propre compte interdite.", "danger")
            return redirect(url_for("users_list"))

        user = db.session.get(User, user_id)
        if not user:
            flash("Utilisateur introuvable.", "danger")
            return redirect(url_for("users_list"))

        db.session.delete(user)
        db.session.commit()
        flash("Utilisateur supprime.", "info")
        return redirect(url_for("users_list"))
