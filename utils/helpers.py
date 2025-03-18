from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended.exceptions import NoAuthorizationError
from sqlalchemy import select
from sqlalchemy.exc import OperationalError

from db import db
from db.models import Users, Budgets
from datetime import datetime

from utils.mappers import budget_mapper


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


def get_auth_user():
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


def get_current_date():
    current_date = datetime.now()
    return current_date.year, current_date.month


def get_budget_for_user(user_id, selected_date_str):
    """
    Retrieve the budget for given user and date (format: 'YYYY-MM')
    :param user_id: ID of user stored in JWT
    :param selected_date_str: Passed by the user in the request
    :return: Tuple (Budget object or None, error_message) if no budget found None, if no error, error_message is None
    """
    try:
        selected_date = datetime.strptime(selected_date_str, "%Y-%m")
    except ValueError:
        return None, "Invalid date format. Expected YYYY-MM"

    stmt = (
        select(Budgets)
        .join(Users, Budgets.user_id == Users.user_id)
        .filter(Users.user_id == user_id)
        .filter(Budgets.budget_month == selected_date.month)
        .filter(Budgets.budget_year == selected_date.year)
    )
    try:
        result = db.session.execute(stmt).scalar_one_or_none()
        if not result:
            return None, "No budget for selected period"
        return result, budget_mapper(result), None
    except OperationalError:
        return None, None, "Connection error"
    except Exception as e:
        return None, None, f"Unexpected error {str(e)}"


def prepare_expense_data(data, user_id) -> (object, str):
    """

    :param data: Dictionary form of data from request
    :param user_id: User_id from jwt identity
    :return: Filled data dictionary and an error message if budget returns nothing
    """
    data["amount"] = float(data.get("amount", "0"))
    data["description"] = data.get("description", "None")
    data["user_id"] = int(user_id)
    data["created_at"] = datetime.now().strftime("%Y-%m-%d")
    data["updated_at"] = None
    budget, error_msg = get_budget_for_user(user_id, data["expense_date"][:7])
    if error_msg:
        return None, f"Something went wrong {error_msg}"
    data["budget_id"] = budget.get("budget_id")
    return data, None


def prepare_budget_data(data, user_id):
    data["user_id"] = user_id
    data["budget_amount"] = float(data.get("budget_amount", "0"))
    data["budget_month"] = int(data["budget_month"])
    data["budget_year"] = int(data["budget_year"])
    data["status_id"] = 1
    data["created_at"] = datetime.now().strftime("%Y-%m-%d")
    data["updated_at"] = None
    return data


def parse_date(year, month) -> str:
    """
    There is no need to validate data as it will be done on an earlier step
    :param year: Year from the request
    :param month: Month from the request
    :return: date in format YYYY-MM
    """
    return f"{year}-{int(month):02d}"
