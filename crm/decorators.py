from __future__ import annotations

from functools import wraps

from flask import flash, redirect, url_for
from flask_login import current_user


def role_required(*roles: str):
    def decorator(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            if current_user.role not in roles:
                flash("Tu n'as pas les permissions necessaires.", "danger")
                return redirect(url_for("dashboard"))
            return func(*args, **kwargs)

        return wrapped

    return decorator
