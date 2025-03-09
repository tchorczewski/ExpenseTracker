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
from .routes.expense_routes import expense_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.permanent_session_lifetime = timedelta(days=1)
    jwt = JWTManager(app)
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.register_blueprint(expense_bp, url_prefix="/api/expenses")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(budget_bp, url_prefix="/api/budgets")

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

    return app
