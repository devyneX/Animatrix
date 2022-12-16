from flask import Blueprint
from ..controllers.profile_controller import ProfileController

profile = Blueprint("profile", __name__, template_folder="../views/profile")
controller = ProfileController()


profile.route("/<username>", methods=["GET"])(controller.profile)
profile.route("/<username>/followers", methods=["GET"])(controller.followers)
profile.route("/<username>/following", methods=["GET"])(controller.following)
profile.route("/<username>/friends", methods=["GET"])(controller.friends)
profile.route("/<username>/favorites", methods=["GET"])(controller.favorites)
profile.route("/watchlist", methods=["GET"])(controller.watchlist)
profile.route("/recommendations", methods=["GET"])(controller.recommendations)
