from __future__ import annotations

from io import BytesIO

from flask import Blueprint, flash, redirect, render_template, request, send_file, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_

from controllers.decorators import role_required
from extensions import db
from models import Client, Quote
from services.invoice_service import create_invoice_from_quote
from services.pdf_service import build_quote_pdf
from services.qr_service import ensure_quote_qr
from services.quote_service import build_quote_from_form

devis_bp = Blueprint("devis", __name__)


@devis_bp.route("/devis")
@login_required
def list():
    q = request.args.get("q", "").strip()
    page = request.args.get("page", 1, type=int)
    query = Quote.query.join(Client)
    if q:
        like_q = f"%{q}%"
        query = query.filter(or_(Quote.reference.ilike(like_q), Client.nom.ilike(like_q)))
    pagination = query.order_by(Quote.created_at.desc()).paginate(page=page, per_page=10, error_out=False)
    for quote in pagination.items:
        ensure_quote_qr(quote.reference)
    return render_template(
        "devis/list.html",
        quotes=pagination.items,
        pagination=pagination,
        pagination_args={"q": q},
        q=q,
    )


@devis_bp.route("/devis/new", methods=["GET", "POST"])
@devis_bp.route("/devis/nouveau", methods=["GET", "POST"])
@login_required
@role_required("responsable", "employe")
def create():
    clients = Client.query.order_by(Client.nom.asc()).all()
    if request.method == "POST":
        quote = build_quote_from_form()
        if not quote:
            flash("Client, statut valide et lignes de devis sont obligatoires.", "danger")
            return render_template("devis/create.html", quote=None, clients=clients)

        ensure_quote_qr(quote.reference)
        action = request.form.get("submit_action", "save_quote")
        db.session.commit()

        if action == "save_and_invoice":
            if quote.facture:
                flash("La facture existante a ete ouverte.", "info")
                return redirect(url_for("invoices.show", invoice_id=quote.facture.id))

            if current_user.role != "responsable":
                flash("Seul un responsable peut generer une facture.", "danger")
                return redirect(url_for("devis.list"))

            invoice = create_invoice_from_quote(quote)
            db.session.commit()
            flash("Devis cree et facture generee.", "success")
            return redirect(url_for("invoices.show", invoice_id=invoice.id))

        flash("Devis cree.", "success")
        return redirect(url_for("devis.list"))

    return render_template("devis/create.html", quote=None, clients=clients)


@devis_bp.route("/devis/<int:quote_id>/edit", methods=["GET", "POST"])
@devis_bp.route("/devis/<int:quote_id>/modifier", methods=["GET", "POST"])
@login_required
@role_required("responsable", "employe")
def edit(quote_id: int):
    quote = db.session.get(Quote, quote_id)
    if not quote:
        flash("Devis introuvable.", "danger")
        return redirect(url_for("devis.list"))

    clients = Client.query.order_by(Client.nom.asc()).all()
    if request.method == "POST":
        updated_quote = build_quote_from_form(quote)
        if not updated_quote:
            flash("Client, statut valide et lignes de devis sont obligatoires.", "danger")
            return render_template("devis/edit.html", quote=quote, clients=clients)

        ensure_quote_qr(quote.reference)
        action = request.form.get("submit_action", "save_quote")
        db.session.commit()

        if action == "save_and_invoice":
            if quote.facture:
                flash("La facture existante a ete ouverte.", "info")
                return redirect(url_for("invoices.show", invoice_id=quote.facture.id))

            invoice = create_invoice_from_quote(quote)
            db.session.commit()
            flash("Facture generee a partir du devis.", "success")
            return redirect(url_for("invoices.show", invoice_id=invoice.id))

        flash("Devis mis a jour.", "success")
        return redirect(url_for("devis.list"))

    ensure_quote_qr(quote.reference)
    return render_template("devis/edit.html", quote=quote, clients=clients)


@devis_bp.route("/devis/<int:quote_id>/delete", methods=["POST"])
@devis_bp.route("/devis/<int:quote_id>/supprimer", methods=["POST"])
@login_required
@role_required("responsable")
def delete(quote_id: int):
    quote = db.session.get(Quote, quote_id)
    if not quote:
        flash("Devis introuvable.", "danger")
        return redirect(url_for("devis.list"))

    db.session.delete(quote)
    db.session.commit()
    flash("Devis supprime.", "info")
    return redirect(url_for("devis.list"))


@devis_bp.route("/devis/<int:quote_id>/pdf")
@login_required
def pdf(quote_id: int):
    quote = db.session.get(Quote, quote_id)
    if not quote:
        flash("Devis introuvable.", "danger")
        return redirect(url_for("devis.list"))

    ensure_quote_qr(quote.reference)
    pdf_bytes = build_quote_pdf(quote)
    if pdf_bytes is None:
        return redirect(url_for("devis.print_view", quote_id=quote.id, autoprint=1, fallback=1))

    return send_file(BytesIO(pdf_bytes), mimetype="application/pdf", as_attachment=True, download_name=f"{quote.reference}.pdf")


@devis_bp.route("/devis/<int:quote_id>/print")
@login_required
def print_view(quote_id: int):
    quote = db.session.get(Quote, quote_id)
    if not quote:
        flash("Devis introuvable.", "danger")
        return redirect(url_for("devis.list"))

    ensure_quote_qr(quote.reference)
    return render_template(
        "devis/print.html",
        quote=quote,
        autoprint=request.args.get("autoprint") == "1",
        fallback=request.args.get("fallback") == "1",
    )


@devis_bp.route("/devis/<reference>")
def public(reference: str):
    quote = Quote.query.filter_by(reference=reference).first()
    if not quote:
        flash("Devis introuvable.", "danger")
        return redirect(url_for("devis.list"))

    ensure_quote_qr(quote.reference)
    return render_template("quote_show.html", quote=quote)
