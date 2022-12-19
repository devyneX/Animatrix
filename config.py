import os


class BaseConfig(object):
    SECRET_KEY = "Nothing"
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DEV_DB")
    UPLOAD_FOLDER = os.environ.get("DEV_UPLOAD")
    # SQLALCHEMY_ECHO = True


class TestingConfig(BaseConfig):
    SECRET_KEY = os.environ.get("SECRET")
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DB")
    UPLOAD_FOLDER = os.environ.get("TEST_UPLOAD")


class ProductionConfig(BaseConfig):
    SECRET_KEY = os.environ.get("SECRET")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    UPLOAD_FOLDER = os.environ.get("CDN")
