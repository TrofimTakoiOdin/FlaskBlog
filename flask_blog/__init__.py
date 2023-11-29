from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_blog.config import DevelopmentConfig, TestingConfig
from flask_migrate import Migrate
from flask_pagedown import PageDown
from flask_bootstrap import Bootstrap

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
pagedown = PageDown()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
mail = Mail()


def create_app(environment='testing'):
    app = Flask(__name__)

    if environment == 'development':
        app.config.from_object('flask_blog.config.DevelopmentConfig')
    elif environment == 'testing':
        app.config.from_object('flask_blog.config.TestingConfig')

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    pagedown.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    Bootstrap(app)

    from flask_blog.app.users.routes import users
    from flask_blog.app.posts.routes import posts
    from flask_blog.app.main.routes import main
    from flask_blog.errors.error_handlers import errors
    from flask_blog.commands.users_crud_cli import users_crud
    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(main)
    app.register_blueprint(errors)
    app.register_blueprint(users_crud)

    return app
