import os
from flask import Flask, render_template, request
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_babel import Babel
from flask_mail import Mail
from flask_admin import Admin, BaseView, expose
#from flask_apscheduler import APScheduler


#flask extensions
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
babel = Babel()
mail = Mail()
admin = Admin(name='管理首页')
#scheduler = APScheduler()


def create_app():
    # create and config the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    db.init_app(app)
    login.init_app(app)
    migrate.init_app(app)
    babel.init_app(app)
    mail.init_app(app)
    admin.init_app(app)
    #scheduler.init_app(app)
    #scheduler.start()

    app.config["DEFAULT_BABEL_LOCALE"] = "en"

    #URL of homepage
    @app.route('/', methods=['GET'])
    @app.route('/index', methods=['GET'])
    def index():
        return render_template('index.html')


    @babel.localeselector
    def get_locale():
        return request.accept_languages.best_match(app.config['LANGUAGES'])

    #registrations of blueprints
    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)

    from . import course
    app.register_blueprint(course.bp)

    from . import cousession
    app.register_blueprint(cousession.bp)

    from . import profile
    app.register_blueprint(profile.bp)

    from . import manage
    app.register_blueprint(manage.bp)

    from . import guide
    app.register_blueprint(guide.bp)

    from . import download
    app.register_blueprint(download.bp)

    from . import api
    app.register_blueprint(api.bp)


    return app

#from flaskr import models