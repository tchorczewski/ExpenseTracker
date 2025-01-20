from flask import Flask
from db import db
from .config import Config
from datetime import timedelta


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.permanent_session_lifetime = timedelta(days=1)

    db.init_app(app)

    return app
