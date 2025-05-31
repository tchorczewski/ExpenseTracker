from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended.exceptions import NoAuthorizationError
from typing import Any
from flask import jsonify, Response
from db.models import Users


def _get_current_user(user_id):
    """
    :param user_id: User_id taken from JWT Identity
    :return: Returns the result of check if user with such an id exists in the db.
    """
    user = Users.query.filter_by(user_id=user_id).first()
    return user


def _get_user_id_from_token():
    try:
        return get_jwt_identity()
    except NoAuthorizationError:
        return None


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
