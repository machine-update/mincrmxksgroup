from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy import or_

from controllers.decorators import role_required
from extensions import db
from models import Client, Invoice, Quote
from services.invoice_service import create_invoice_from_quote
from services.qr_service import ensure_quote_qr


invoices_bp = Blueprint("invoices", __name__)


@invoices_bp.route("/invoices")
@login_required
def list():
    q = request.args.get("q", "").strip()
    page = request.args.get("page", 1, type=int)
    query = Invoice.query.join(Client)
    if q:
        like_q = f"%{q}%"
        query = query.filter(or_(Invoice.reference.ilike(like_q), Client.nom.ilike(like_q)))
    pagination = query.order_by(Invoice.created_at.desc()).paginate(page=page, per_page=10, error_out=False)
    return render_template("invoices.html", invoices=pagination.items, pagination=pagination, pagination_args={"q": q}, q=q)


@invoices_bp.route("/invoices/<int:invoice_id>")
@login_required
def show(invoice_id: int):
    invoice = db.session.get(Invoice, invoice_id)
    if not invoice:
        flash("Facture introuvable.", "danger")
        return redirect(url_for("invoices.list"))
    return render_template("invoice_show.html", invoice=invoice)


@invoices_bp.route("/invoices/<int:invoice_id>/print")
@login_required
def print_view(invoice_id: int):
    invoice = db.session.get(Invoice, invoice_id)
    if not invoice:
        flash("Facture introuvable.", "danger")
        return redirect(url_for("invoices.list"))
    if invoice.devis:
        ensure_quote_qr(invoice.devis.reference)
    return render_template("invoice_print.html", invoice=invoice)


@invoices_bp.route("/devis/<int:quote_id>/facture", methods=["POST"])
@login_required
@role_required("responsable")
def create_from_devis(quote_id: int):
    quote = db.session.get(Quote, quote_id)
    if not quote:
        flash("Devis introuvable.", "danger")
        return redirect(url_for("devis.list"))

    invoice = create_invoice_from_quote(quote)
    db.session.commit()
    flash("Facture generee a partir du devis.", "success")
    return redirect(url_for("invoices.show", invoice_id=invoice.id))


@invoices_bp.route("/invoices/<int:invoice_id>/status", methods=["POST"])
@login_required
@role_required("responsable")
def update_status(invoice_id: int):
    invoice = db.session.get(Invoice, invoice_id)
    if not invoice:
        flash("Facture introuvable.", "danger")
        return redirect(url_for("invoices.list"))

    status = request.form.get("statut", "Emise").strip()
    if status not in {"Brouillon", "Emise", "Payee", "Annulee"}:
        flash("Statut de facture invalide.", "danger")
        return redirect(url_for("invoices.show", invoice_id=invoice.id))

    invoice.statut = status
    db.session.commit()
    flash("Statut facture mis a jour.", "success")
    return redirect(url_for("invoices.show", invoice_id=invoice.id))
