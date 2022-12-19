from flask import render_template, redirect, url_for, request
from flask_login import current_user, logout_user, login_required


class AuthController:
    def __init__(self) -> None:
        pass

    def login(self):
        if current_user.is_authenticated:
            return redirect(
                url_for("user.profile.profile", username=current_user.username)
            )

        return render_template("login.html")

    def sign_up(self):
        if current_user.is_authenticated:
            return redirect(
                url_for("user.profile.profile", username=current_user.username)
            )

        return render_template("signup.html")

    @login_required
    def logout(self):
        logout_user()
        return redirect(url_for("auth.login"))
