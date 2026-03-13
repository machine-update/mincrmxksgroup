from __future__ import annotations

import unittest
from datetime import date

from app import app
from crm.extensions import db
from crm.models import Invoice, Project, Quote, User
from crm.services.seed_service import seed_data


class AppSmokeTests(unittest.TestCase):
    def setUp(self):
        with app.app_context():
            seed_data()
            user = User.query.filter_by(email="admin@xks.local").first()
            if user is None:
                user = User(nom="Admin Test", email="admin@xks.local", role="responsable")
                db.session.add(user)
            user.set_password("admin123")
            db.session.commit()
        self.client = app.test_client()

    def test_login_page_loads(self):
        response = self.client.get("/login")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Connexion", response.data)

    def test_admin_can_login_and_open_dashboard(self):
        response = self.client.post(
            "/login",
            data={"email": "admin@xks.local", "password": "admin123"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Tableau de bord", response.data)

    def test_project_effective_status_uses_dates(self):
        with app.app_context():
            project = Project(
                titre="Projet test",
                type="Clip",
                statut="En attente",
                date_debut=date(2026, 3, 7),
                date_fin=date(2026, 3, 20),
                client_id=1,
                user_id=1,
            )
            self.assertEqual(project.effective_status, "En cours")

    def test_quote_can_be_converted_to_invoice(self):
        with app.app_context():
            quote = Quote.query.first()
            self.assertIsNotNone(quote)
            quote_id = quote.id

        self.client.post(
            "/login",
            data={"email": "admin@xks.local", "password": "admin123"},
            follow_redirects=True,
        )
        response = self.client.post(f"/quotes/{quote_id}/invoice", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Facture", response.data)

    def test_invoice_print_view_loads(self):
        self.client.post(
            "/login",
            data={"email": "admin@xks.local", "password": "admin123"},
            follow_redirects=True,
        )
        self.client.post("/quotes/1/invoice", follow_redirects=True)
        with app.app_context():
            invoice = Invoice.query.order_by(Invoice.id.asc()).first()
            self.assertIsNotNone(invoice)
            invoice_id = invoice.id

        response = self.client.get(f"/invoices/{invoice_id}/print")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Imprimer / Sauver en PDF", response.data)


if __name__ == "__main__":
    unittest.main()
