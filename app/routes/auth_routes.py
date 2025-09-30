import bcrypt
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    set_access_cookies,
    jwt_required,
    unset_jwt_cookies,
)

from app.common.decorators import error_handler
from app.services.auth_services import verify_user
from db.models import Users
from db import db
from utils.validation import is_valid_email, is_valid_password

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login_user():
    username = request.form["login"]
    password = request.form["password"]
    status, usr_id = verify_user(username, password)
    if status:
        access_token = create_access_token(identity=str(usr_id))
        response = jsonify({"message": "Login Successful"})
        set_access_cookies(response, access_token)
        return response, 200
    return {"message": "Invalid username or password"}, 401


@auth_bp.route("/register", methods=["POST"])
@error_handler
def register_user():
    password = request.form["password"]

    if not is_valid_password(password):
        return (
            jsonify(
                {
                    "message": "Password must be at least 8 characters long, contain a number and a letter"
                }
            ),
            400,
        )
    if not is_valid_email(request.form["email"]):
        return jsonify({"message": "Invalid email format"}), 400

    user = Users(
        username=request.form["username"],
        email=request.form["email"],
        first_name=request.form["first_name"],
        last_name=request.form["last_name"],
        user_password=bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()),
        user_status_id=5,
        user_role_id=2,
    )

    db.session.add(user)
    db.session.commit()
    return (
        jsonify(
            {
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "status_id": user.user_status_id,
                "role_id": user.user_role_id,
            }
        ),
        201,
    )


@auth_bp.route("/logout")
def logout():
    response = jsonify({"message": "Logout successful"})
    unset_jwt_cookies(response)
    return response, 200
