# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
Modified
"""

import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

db = SQLAlchemy()  # flask-sqlalchemy
lm = LoginManager()  # flask-loginmanager
bc = Bcrypt()  # flask-bcrypt


def create_app():
    app = Flask(__name__)
    app.config.from_object('app.configuration.Config')
    init_apps(app)

    return app


def init_apps(app):
    db.init_app(app)
    lm.init_app(app)
    bc.init_app(app)


app = create_app()


@app.before_first_request
def initialize_database():
    db.create_all()


# Import routing, models and Start the App
from app import views, models

# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))
