# -*- coding: utf-8 -*-

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_debugtoolbar import DebugToolbarExtension
from config import config
from flask_moment import Moment
import os
from basedir import basedir



"""
config
 -- 'default': DevelopmentConfig
 -- 'develop': DevelopmentConfig
 -- 'testing': TestingConfig
 -- 'production': ProductionConfig
    you can edit this in config.py
"""



db = SQLAlchemy()
moment = Moment()
login_manager = LoginManager()
login_manager.session_protection = 'strong'



"""
blueprint
you can register a <blueprint> by run:
 -- mana blueprint <blueprint>
under app folder
""""""
from main import main
app.register_blueprint(main, url_prefix='/main')
from auth import auth
app.register_blueprint(auth, url_prefix="/auth")
"""
def create_app(config_name=None,main=True) :
    if config_name is None :
        config_name = 'default'
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    config[config_name].init_app(app)
    db.init_app(app)
    moment.init_app(app)
    login_manager.init_app(app)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("AUTH_SQL") or "sqlite:///" + os.path.join(basedir, 'data.sqlite')

    from .auth import auth
    app.register_blueprint(auth)
    return app

from . import auth

app = create_app(config_name = 'default')
