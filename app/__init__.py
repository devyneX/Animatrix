from flask import Flask, render_template

# from .populate_db_script import fill_db, drop_all, drop_all_rows

# extensions
from .extensions import db, migrate, login_manager, init_user_loader

# models
from .models.UserModel import BaseUser

# routes
from .routes.auth import auth
from .routes.user import user
from .routes.anime import anime
from .routes.post import post
from .routes.admin import admin
from .routes.browse import browse


def create_app():
    app = Flask(__name__, template_folder="views")

    app.config.from_object("config.DevelopmentConfig")

    # extensions_initialization
    db.init_app(app)
    migrate.init_app(app, db)

    login_manager.init_app(app)
    init_user_loader(BaseUser)

    # fill_db(db, app)

    # @app.route("/", methods=["GET"])
    # def index():
    #     return render_template("base.html")

    app.register_blueprint(browse)
    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(user, url_prefix="/users")
    app.register_blueprint(anime, url_prefix="/anime")
    app.register_blueprint(post, url_prefix="/post")
    app.register_blueprint(admin, url_prefix="/admin")

    return app
