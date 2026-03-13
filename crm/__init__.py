from __future__ import annotations

import os
from pathlib import Path

from flask import Flask

from .controllers.auth_controller import register_auth_routes
from .controllers.client_controller import register_client_routes
from .controllers.dashboard_controller import register_dashboard_routes
from .controllers.invoice_controller import register_invoice_routes
from .controllers.project_controller import register_project_routes
from .controllers.quote_controller import register_quote_routes
from .controllers.user_controller import register_user_routes
from .extensions import db, login_manager
from .models import User
from .services.presentation_service import register_template_helpers
from .services.seed_service import seed_data


def create_app() -> Flask:
    project_root = Path(__file__).resolve().parent.parent
    app = Flask(
        __name__,
        template_folder=str(project_root / "templates"),
        static_folder=str(project_root / "static"),
    )
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///crm.sqlite3")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["TEMPLATES_AUTO_RELOAD"] = True

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "login"
    login_manager.login_message = "Connecte-toi pour acceder a cette page."

    @login_manager.user_loader
    def load_user(user_id: str):
        return db.session.get(User, int(user_id))

    register_template_helpers(app)
    register_auth_routes(app)
    register_dashboard_routes(app)
    register_invoice_routes(app)
    register_client_routes(app)
    register_project_routes(app)
    register_quote_routes(app)
    register_user_routes(app)

    with app.app_context():
        db.create_all()
        seed_data()

    return app
