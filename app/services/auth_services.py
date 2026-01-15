import bcrypt
from flask_jwt_extended import get_jwt_identity, set_access_cookies, create_access_token
from typing import Any
from flask import jsonify, Response
from db import db
from db.models import Users
from utils.mappers import user_mapper


def _get_current_user(user_id: int):
    """
    :param user_id: User_id taken from JWT Identity
    :return: Returns the result of check if user with such an id exists in the db.
    """
    user = Users.query.filter_by(id=user_id).first()
    return user


def _get_user_id_from_token():
    """
    :return: Identity taken from JWT Token, in this case, user_id
    """
    return get_jwt_identity()


def get_auth_user() -> tuple[None, Response, int] | tuple[Any | None, None, int]:
    """
    Gets and verifies the user based on JWT cookies.
    :return: (user, error_response,status_code)
    """
    user_id = _get_user_id_from_token()
    if not user_id:
        return None, jsonify({"message": "Unauthorized"}), 401
    user = _get_current_user(user_id)
    if not user:
        return None, jsonify({"message": "User not found"}), 404
    return user, None, 200


def log_in(login, password):
    """
    Takes login and password entered in login form by user and loggs him in, creating JWT token.
    :param login: Login
    :param password: Password
    :return: Result message and status code
    """
    status, user_id = verify_user(login, password)
    if not status:
        message, status_code = {"message": "Invalid username or password"}, 401
        return message, status_code
    message, status_code = generate_token(user_id), 200
    return message, status_code


def verify_user(username, password):
    """
    Verifies if the given username and password are correct and matching to one of the users registered in DB.
    :param username: Username
    :param password: Password
    :return:
    """
    user = Users.query.filter_by(username=username).first()
    if user is None:
        return False, None
    status = bcrypt.checkpw(
        password.encode("utf-8"),
        user.password,
    )
    if status:
        return (
            status,
            user.id,
        )
    return False, None


def generate_token(user_id):
    """
    Generates and sets JWT access token for given user_id in cookies.
    :param user_id: User_id
    :return: Response given to user
    """
    access_token = create_access_token(identity=str(user_id))
    response = jsonify({"message": "Login Successful"})
    set_access_cookies(response, access_token)
    return response


def register_user(data):
    """
    Creates model object and adds it to db
    :param data: Data received from frontend
    :return:
    """
    user = Users(
        username=data["username"],
        email=data["email"],
        first_name=data["first_name"],
        last_name=data["last_name"],
        password=bcrypt.hashpw(data["password"].encode("utf-8"), bcrypt.gensalt()),
        status_id=2,
        role_id=1,
    )
    db.session.add(user)
    db.session.commit()
    return jsonify(user_mapper(user)), 201
