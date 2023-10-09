import os


class DevelopmentConfig:
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///development.db'
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DB_URI')
    MAIL_SERVER = 'smtp.yandex.ru'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_DEV')
    MAIL_PASSWORD = os.environ.get('MAIL_DEV_PWD')


class TestingConfig:
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    TESTING = True
    WTF_CSRF_ENABLED = False
    MAIL_SERVER = 'smtp.yandex.ru'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_DEV')
    MAIL_PASSWORD = os.environ.get('MAIL_DEV_PWD')
