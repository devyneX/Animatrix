from flask import Blueprint
from ..controllers.anime_controller import AnimeController


anime = Blueprint("anime", __name__, template_folder="../views/anime")
controller = AnimeController()

anime.route("/<id>", methods=["GET"])(controller.anime_page)
anime.route("/<id>/teaser", methods=["GET"])(controller.teaser)
anime.route("/<id>/trailer", methods=["GET"])(controller.trailer)
anime.route("/<id>/rate", methods=["POST"])(controller.rate)
anime.route("/<id>/post", methods=["POST"])(controller.post)
