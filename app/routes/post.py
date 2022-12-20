from flask import Blueprint
from ..controllers.post_controller import PostController

post = Blueprint("post", __name__, template_folder="../views/post")
controller = PostController()

post.route("/<id>", methods=["GET"])(controller.post)
post.route("/react", methods=["POST"])(controller.react)
post.route("/<id>/comment", methods=["POST"])(controller.comment)
