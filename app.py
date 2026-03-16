from __future__ import annotations

import os
from pathlib import Path

from flask import Flask

from config import Config
from controllers.auth_controller import auth_bp
from controllers.client_controller import clients_bp
from controllers.dashboard_controller import dashboard_bp
from controllers.invoice_controller import invoices_bp
from controllers.project_controller import projects_bp
from controllers.quote_controller import devis_bp
from controllers.user_controller import users_bp
from extensions import db, login_manager
from models import User
from services.presentation_service import register_template_helpers
from services.seed_service import seed_data


def create_app() -> Flask:
    project_root = Path(__file__).resolve().parent
    app = Flask(
        __name__,
        template_folder=str(project_root / "templates"),
        static_folder=str(project_root / "static"),
    )
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Connecte-toi pour acceder a cette page."

    @login_manager.user_loader
    def load_user(user_id: str):
        return db.session.get(User, int(user_id))

    register_template_helpers(app)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(clients_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(devis_bp)
    app.register_blueprint(invoices_bp)
    app.register_blueprint(users_bp)

    with app.app_context():
        db.create_all()
        seed_data()

    return app


app = create_app()


if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=5000, debug=debug, use_reloader=debug)
