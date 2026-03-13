from __future__ import annotations

from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required

from ..decorators import role_required
from ..extensions import db
from ..models import Client
from ..services.client_service import build_client_query, export_clients_csv


def register_client_routes(app) -> None:
    @app.route("/clients")
    @login_required
    def clients_list():
        q = request.args.get("q", "").strip()
        entreprise = request.args.get("entreprise", "").strip()
        with_phone = request.args.get("with_phone", "").strip() == "1"
        order = request.args.get("order", "recent").strip()

        query = build_client_query(q, entreprise, with_phone)
        if order == "name":
            query = query.order_by(Client.nom.asc())
        else:
            order = "recent"
            query = query.order_by(Client.created_at.desc())

        return render_template(
            "clients.html",
            clients=query.all(),
            q=q,
            entreprise=entreprise,
            with_phone=with_phone,
            order=order,
        )

    @app.route("/clients/export")
    @login_required
    def clients_export():
        q = request.args.get("q", "").strip()
        entreprise = request.args.get("entreprise", "").strip()
        with_phone = request.args.get("with_phone", "").strip() == "1"
        order = request.args.get("order", "recent").strip()

        query = build_client_query(q, entreprise, with_phone)
        clients = query.order_by(Client.nom.asc()).all() if order == "name" else query.order_by(Client.created_at.desc()).all()
        return export_clients_csv(clients)

    @app.route("/clients/new", methods=["GET", "POST"])
    @login_required
    @role_required("responsable")
    def clients_new():
        if request.method == "POST":
            client = Client(
                nom=request.form.get("nom", "").strip(),
                entreprise=request.form.get("entreprise", "").strip() or None,
                email=request.form.get("email", "").strip(),
                telephone=request.form.get("telephone", "").strip() or None,
                adresse=request.form.get("adresse", "").strip() or None,
            )
            if not client.nom or not client.email:
                flash("Nom et email sont obligatoires.", "danger")
                return render_template("client_form.html", client=None)

            db.session.add(client)
            db.session.commit()
            flash("Client cree.", "success")
            return redirect(url_for("clients_list"))

        return render_template("client_form.html", client=None)

    @app.route("/clients/<int:client_id>/edit", methods=["GET", "POST"])
    @login_required
    @role_required("responsable")
    def clients_edit(client_id: int):
        client = db.session.get(Client, client_id)
        if not client:
            flash("Client introuvable.", "danger")
            return redirect(url_for("clients_list"))

        if request.method == "POST":
            client.nom = request.form.get("nom", "").strip()
            client.entreprise = request.form.get("entreprise", "").strip() or None
            client.email = request.form.get("email", "").strip()
            client.telephone = request.form.get("telephone", "").strip() or None
            client.adresse = request.form.get("adresse", "").strip() or None

            if not client.nom or not client.email:
                flash("Nom et email sont obligatoires.", "danger")
                return render_template("client_form.html", client=client)

            db.session.commit()
            flash("Client mis a jour.", "success")
            return redirect(url_for("clients_list"))

        return render_template("client_form.html", client=client)

    @app.route("/clients/<int:client_id>/delete", methods=["POST"])
    @login_required
    @role_required("responsable")
    def clients_delete(client_id: int):
        client = db.session.get(Client, client_id)
        if not client:
            flash("Client introuvable.", "danger")
            return redirect(url_for("clients_list"))

        db.session.delete(client)
        db.session.commit()
        flash("Client supprime.", "info")
        return redirect(url_for("clients_list"))
