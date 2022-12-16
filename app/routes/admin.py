from flask import Blueprint
from ..controllers.admin_controller import AdminController

admin = Blueprint("admin", __name__, template_folder="../views/admin")
controller = AdminController()


admin.route("/login", methods=["GET", "POST"])(controller.login)
admin.route("/logout", methods=["GET"])(controller.logout)
admin.route("/users", methods=["GET"])(controller.users)
admin.route("/permanent_ban/<username>", methods=["GET"])(controller.permanent_ban)
admin.route("/anime", methods=["GET"])(controller.animes)
admin.route("/ban/<username>", methods=["GET"])(controller.ban_form)
admin.route("/ban", methods=["POST"])(controller.ban)
admin.route("/add_anime", methods=["GET", "POST"])(controller.add_anime)
admin.route("/edit_anime/<id>", methods=["GET", "POST"])(controller.edit_anime)
admin.route("/support_requests", methods=["GET"])(controller.support_requests)
admin.route("/support_response_form/<id>", methods=["GET"])(
    controller.support_response_form
)
admin.route("/support_response", methods=["POST"])(controller.support_respond)
