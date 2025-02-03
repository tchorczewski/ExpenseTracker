import bcrypt
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    set_access_cookies,
    jwt_required,
    unset_jwt_cookies,
)
from db.models import Users
from db import db

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login_user():
    if request.method == "POST":
        username = request.form["login"]
        password = request.form["password"]
        status, usr_id = get_pwd(username, password)
        if status:
            access_token = create_access_token(identity=str(usr_id))
            response = jsonify({"message": "Login Successful"})
            set_access_cookies(response, access_token)
            return response, 200
        return {"message": "Invalid username or password"}, 401


def get_pwd(username, password):
    user = Users.query.filter_by(username=username).first_or_404()
    return (
        bcrypt.checkpw(
            password.encode("utf-8"),
            user.user_password,
        ),
        user.user_id,
    )


@auth_bp.route("/register", methods=["POST"])
def user_create():
    if request.method == "POST":
        password = request.form["password"]
        user = Users(
            username=request.form["username"],
            e_mail=request.form["e_mail"],
            first_name=request.form["first_name"],
            last_name=request.form["last_name"],
            user_password=bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()),
        )
        db.session.add(user)
        db.session.commit()
        return (
            jsonify(
                {
                    "user_id": user.user_id,
                    "username": user.username,
                    "e_mail": user.e_mail,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                }
            ),
            201,
        )


@auth_bp.route("/logout")
@jwt_required()
def logout():
    response = jsonify({"message": "Logout successful"})
    unset_jwt_cookies(response)
    return response, 200
