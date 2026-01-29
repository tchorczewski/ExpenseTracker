from os import getenv
from flask import url_for, redirect
from flask import Flask
from flask_jwt_extended import (
    JWTManager,
    get_jwt,
    create_access_token,
    get_jwt_identity,
    set_access_cookies,
)

from db import db
from .config import Config
from datetime import timedelta, datetime
from .routes.auth_routes import auth_bp
from .routes.budget_routes import budget_bp
from .routes.dashboard_routes import dashboard_bp
from .routes.transaction_routes import transaction_bp
from .routes.swagger import swagger_bp
from .routes.ui_routes import main_bp
from app.extensions import celery


def create_app(config_object):
    app = Flask(__name__)
    app.config.from_object(config_object)
    app.permanent_session_lifetime = timedelta(days=1)
    jwt = JWTManager(app)
    db.init_app(app)
    celery.conf.update(app.config["CELERY"])
    celery.set_current()
    app.extensions["celery"] = celery

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    with app.app_context():
        db.create_all()
    app.register_blueprint(main_bp)
    app.register_blueprint(transaction_bp, url_prefix="/api/transactions")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(budget_bp, url_prefix="/api/budgets")
    app.register_blueprint(swagger_bp, prefix=getenv("SWAGGER_URL"))
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")

    @jwt.unauthorized_loader
    def unauthorized_callback(err_msg):
        return redirect(url_for("main.login_page"))

    @jwt.invalid_token_loader
    def invalid_token_callback(err_msg):
        return redirect(url_for("main.login_page"))

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return redirect(url_for("main.login_page"))

    @app.after_request
    def refresh_expiring_jwt(response):
        try:
            exp_timestamp = get_jwt()["exp"]
            now = datetime.now()
            target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
            if target_timestamp > exp_timestamp:
                access_token = create_access_token(identity=get_jwt_identity())
                set_access_cookies(response, access_token)
            return response
        except (RuntimeError, KeyError):
            return response

    return app, celery
