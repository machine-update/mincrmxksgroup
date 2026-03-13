from __future__ import annotations

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_

from ..decorators import role_required
from ..extensions import db
from ..models import Client, Quote
from ..services.invoice_service import create_invoice_from_quote
from ..services.quote_service import build_quote_from_form


def register_quote_routes(app) -> None:
    @app.route("/quotes")
    @login_required
    def quotes_list():
        q = request.args.get("q", "").strip()
        query = Quote.query.join(Client)
        if q:
            like_q = f"%{q}%"
            query = query.filter(or_(Quote.reference.ilike(like_q), Client.nom.ilike(like_q)))
        return render_template("quotes.html", quotes=query.order_by(Quote.created_at.desc()).all(), q=q)

    @app.route("/quotes/new", methods=["GET", "POST"])
    @login_required
    @role_required("responsable", "employe")
    def quotes_new():
        clients = Client.query.order_by(Client.nom.asc()).all()
        if request.method == "POST":
            quote = build_quote_from_form()
            if not quote:
                flash("Client et lignes de devis sont obligatoires.", "danger")
                return render_template("quote_form.html", quote=None, clients=clients)

            action = request.form.get("submit_action", "save_quote")
            db.session.commit()

            if action == "save_and_invoice":
                if quote.facture:
                    flash("La facture existante a ete ouverte.", "info")
                    return redirect(url_for("invoices_show", invoice_id=quote.facture.id))

                if current_user.role != "responsable":
                    flash("Seul un responsable peut generer une facture.", "danger")
                    return redirect(url_for("quotes_list"))

                invoice = create_invoice_from_quote(quote)
                db.session.commit()
                flash("Devis cree et facture generee.", "success")
                return redirect(url_for("invoices_show", invoice_id=invoice.id))

            flash("Devis cree.", "success")
            return redirect(url_for("quotes_list"))

        return render_template("quote_form.html", quote=None, clients=clients)

    @app.route("/quotes/<int:quote_id>/edit", methods=["GET", "POST"])
    @login_required
    @role_required("responsable", "employe")
    def quotes_edit(quote_id: int):
        quote = db.session.get(Quote, quote_id)
        if not quote:
            flash("Devis introuvable.", "danger")
            return redirect(url_for("quotes_list"))

        clients = Client.query.order_by(Client.nom.asc()).all()
        if request.method == "POST":
            updated_quote = build_quote_from_form(quote)
            if not updated_quote:
                flash("Client et lignes de devis sont obligatoires.", "danger")
                return render_template("quote_form.html", quote=quote, clients=clients)

            action = request.form.get("submit_action", "save_quote")
            db.session.commit()

            if action == "save_and_invoice":
                if quote.facture:
                    flash("La facture existante a ete ouverte.", "info")
                    return redirect(url_for("invoices_show", invoice_id=quote.facture.id))

                invoice = create_invoice_from_quote(quote)
                db.session.commit()
                flash("Facture generee a partir du devis.", "success")
                return redirect(url_for("invoices_show", invoice_id=invoice.id))

            flash("Devis mis a jour.", "success")
            return redirect(url_for("quotes_list"))

        return render_template("quote_form.html", quote=quote, clients=clients)

    @app.route("/quotes/<int:quote_id>/delete", methods=["POST"])
    @login_required
    @role_required("responsable")
    def quotes_delete(quote_id: int):
        quote = db.session.get(Quote, quote_id)
        if not quote:
            flash("Devis introuvable.", "danger")
            return redirect(url_for("quotes_list"))

        db.session.delete(quote)
        db.session.commit()
        flash("Devis supprime.", "info")
        return redirect(url_for("quotes_list"))
