import bcrypt
from flask_jwt_extended import get_jwt_identity
from typing import Any
from flask import jsonify, Response

from app.common.decorators import error_handler
from db.models import Users


def _get_current_user(user_id: int):
    """
    :param user_id: User_id taken from JWT Identity
    :return: Returns the result of check if user with such an id exists in the db.
    """
    user = Users.query.filter_by(user_id=user_id).first()
    return user


@error_handler
def _get_user_id_from_token():
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


def verify_user(username, password):
    user = Users.query.filter_by(username=username).first_or_404()
    status = bcrypt.checkpw(
        password.encode("utf-8"),
        user.user_password,
    )
    if status:
        return (
            status,
            user.user_id,
        )
    return False, None
