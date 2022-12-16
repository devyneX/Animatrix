from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager


db = SQLAlchemy()


migrate = Migrate()


login_manager = LoginManager()
login_manager.login_view = 'auth.login'


def init_user_loader(UserClass):
    @login_manager.user_loader
    def load_user(id):
        return UserClass.query.get(id)
