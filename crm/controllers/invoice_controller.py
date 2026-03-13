from __future__ import annotations

from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy import or_

from ..decorators import role_required
from ..extensions import db
from ..models import Client, Invoice, Quote
from ..services.invoice_service import create_invoice_from_quote


def register_invoice_routes(app) -> None:
    @app.route("/invoices")
    @login_required
    def invoices_list():
        q = request.args.get("q", "").strip()
        query = Invoice.query.join(Client)
        if q:
            like_q = f"%{q}%"
            query = query.filter(or_(Invoice.reference.ilike(like_q), Client.nom.ilike(like_q)))
        invoices = query.order_by(Invoice.created_at.desc()).all()
        return render_template("invoices.html", invoices=invoices, q=q)

    @app.route("/invoices/<int:invoice_id>")
    @login_required
    def invoices_show(invoice_id: int):
        invoice = db.session.get(Invoice, invoice_id)
        if not invoice:
            flash("Facture introuvable.", "danger")
            return redirect(url_for("invoices_list"))
        return render_template("invoice_show.html", invoice=invoice)

    @app.route("/invoices/<int:invoice_id>/print")
    @login_required
    def invoices_print(invoice_id: int):
        invoice = db.session.get(Invoice, invoice_id)
        if not invoice:
            flash("Facture introuvable.", "danger")
            return redirect(url_for("invoices_list"))
        return render_template("invoice_print.html", invoice=invoice)

    @app.route("/quotes/<int:quote_id>/invoice", methods=["POST"])
    @login_required
    @role_required("responsable")
    def quotes_generate_invoice(quote_id: int):
        quote = db.session.get(Quote, quote_id)
        if not quote:
            flash("Devis introuvable.", "danger")
            return redirect(url_for("quotes_list"))

        invoice = create_invoice_from_quote(quote)
        db.session.commit()
        flash("Facture generee a partir du devis.", "success")
        return redirect(url_for("invoices_show", invoice_id=invoice.id))

    @app.route("/invoices/<int:invoice_id>/status", methods=["POST"])
    @login_required
    @role_required("responsable")
    def invoices_update_status(invoice_id: int):
        invoice = db.session.get(Invoice, invoice_id)
        if not invoice:
            flash("Facture introuvable.", "danger")
            return redirect(url_for("invoices_list"))

        status = request.form.get("statut", "Emise").strip()
        if status not in {"Brouillon", "Emise", "Payee", "Annulee"}:
            flash("Statut de facture invalide.", "danger")
            return redirect(url_for("invoices_show", invoice_id=invoice.id))

        invoice.statut = status
        db.session.commit()
        flash("Statut facture mis a jour.", "success")
        return redirect(url_for("invoices_show", invoice_id=invoice.id))
