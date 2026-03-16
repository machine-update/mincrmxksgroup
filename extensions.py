from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

try:
    from flask_migrate import Migrate
except ImportError:  # pragma: no cover
    class Migrate:  # type: ignore[override]
        def init_app(self, app, db):
            return None

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
