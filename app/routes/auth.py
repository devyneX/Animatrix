from ..controllers.auth_controller import AuthController
from flask import Blueprint


auth = Blueprint("auth", __name__, template_folder="../views/auth")
controller = AuthController()


auth.route("/login", methods=["GET"])(controller.login)
auth.route("/signup", methods=["GET"])(controller.sign_up)
auth.route("/logout", methods=["GET"])(controller.logout)
