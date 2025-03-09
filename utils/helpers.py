from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended.exceptions import NoAuthorizationError

from db.models import Users
from datetime import datetime


def get_current_user(user_id):
    """
    :param user_id: User_id taken from JWT Identity
    :return: Returns the result of check if user with such an id exists in the db.
    """
    user = Users.query.filter_by(user_id=user_id).first()
    return user


def get_user_id_from_token():
    try:
        return get_jwt_identity()
    except NoAuthorizationError:
        return None


def get_current_date():
    current_date = datetime.now()
    return current_date.year, current_date.month
