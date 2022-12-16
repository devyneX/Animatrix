from functools import wraps
from flask import redirect, url_for, abort
from flask_login import current_user


ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def admin_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("admin.login"))
        if current_user.user_type != "admin":
            abort(403)
        return func(*args, **kwargs)

    return wrapper
