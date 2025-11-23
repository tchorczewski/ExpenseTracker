from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    unset_jwt_cookies,
)
from app.common.decorators import error_handler
from app.services.auth_services import log_in, register_user
from utils.validation import validate_register

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login_user():
    username = request.form["login"]
    password = request.form["password"]
    if username is None or password is None:
        return {"message": "Missing username or password"}, 400
    message, status_code = log_in(username, password)
    return message, status_code


@auth_bp.route("/register", methods=["POST"])
@error_handler
def register():
    data = request.form
    is_valid, error_message = validate_register(data)
    if not is_valid:
        return jsonify({"message": error_message}), 400

    return register_user(data)


@auth_bp.route("/logout")
def logout():
    response = jsonify({"message": "Logout successful"})
    unset_jwt_cookies(response)
    return response, 200
