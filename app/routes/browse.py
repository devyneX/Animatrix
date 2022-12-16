from flask import Blueprint
from ..controllers.browse_controller import BrowseController


browse = Blueprint("browse", __name__, template_folder="../views/browse")
controller = BrowseController()

browse.route("/")(controller.home)
browse.route("/top_anime", methods=["GET"])(controller.top_anime)
browse.route("/most_popular_anime", methods=["GET"])(controller.most_popular_anime)
browse.route("/search/anime/<search_term>", methods=["GET"])(controller.anime_search)
browse.route("/search/user/<search_term>", methods=["GET"])(controller.user_search)
browse.route("/search", methods=["POST"])(controller.search)
browse.route("/find_anime", methods=["GET", "POST"])(controller.advanced_search)
