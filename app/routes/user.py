from ..controllers.user_controller import UserController
from .profile_bp import profile
from flask import Blueprint


user = Blueprint("user", __name__, template_folder="../views/user")
controller = UserController()

user.register_blueprint(profile, url_prefix="/profile")

user.route("/create_user", methods=["POST"])(controller.create_user)
user.route("/authenticate_user", methods=["POST"])(controller.authenticate_user)
user.route("/follow/<username>", methods=["GET"])(controller.follow)
user.route("/unfollow/<username>", methods=["GET"])(controller.unfollow)
user.route("/add_to_watchlist/<id>", methods=["GET"])(controller.add_to_watchlist)
user.route("/remove_from_watchlist/<id>", methods=["GET"])(
    controller.remove_from_watchlist
)
user.route("/add_to_favorites/<id>", methods=["GET"])(controller.add_to_favorites)
user.route("/remove_from_favorites/<id>", methods=["GET"])(
    controller.remove_from_favorites
)
user.route("/recommend/<id>", methods=["GET", "POST"])(controller.recommend)
user.route("/post", methods=["POST"])(controller.post)
user.route("/support_requests", methods=["GET", "POST"])(controller.support_requests)
user.route("/add_profile_picture", methods=["GET", "POST"])(controller.profile_pic)
user.route("recommendation_advanced_search", methods=["GET", "POST"])(
    controller.recommendation_advanced_search
)
user.route("/notifications", methods=["GET"])(controller.notifications)
user.route("/new_notifications", methods=["GET"])(controller.new_notifications)
