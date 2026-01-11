from datetime import datetime
from sqlalchemy import select, func
from app.common.decorators import error_handler
from db import db
from db.models import Budgets
from utils.mappers import budget_mapper


@error_handler
def get_budget_for_user(user_id: int, month: int, year: int):
    """
    Retrieve the budget for given user and date (format: 'YYYY-MM')
    :param year: Budget's year
    :param month: Budget's month
    :param user_id: ID of user stored in JWT
    :return: Tuple (Budget object or None, error_message) if no budget found None, if no error, error_message is None
    """

    stmt = (
        select(Budgets)
        .filter(Budgets.user_id == user_id)
        .filter(Budgets.budget_month == month)
        .filter(Budgets.budget_year == year)
    )
    result = db.session.execute(stmt).scalar_one_or_none()
    if not result:
        return None, None, "No budget for selected period"
    return result, budget_mapper(result), None


def prepare_budget_data(data: dict, user_id: int):
    data["user_id"] = user_id
    data["amount"] = float(data.get("amount", "0"))
    data["budget_month"] = int(data["budget_month"])
    data["budget_year"] = int(data["budget_year"])
    data["status_id"] = 3
    data["created_at"] = datetime.now()
    data["updated_at"] = None
    return data


def verify_budget_change(user_id, date, current_budgets_id):
    """
    Method to check if the expense needs to be assigned to a different budget
    :param user_id: Stored in JWT users_id
    :param date: Date that user has passed in request to edit within the expense
    :param current_budgets_id ID of the budget the user is editing
    :return: Tuple (Bool, new_budget_id). new_budget_id will be an id or None
    """
    _, edited_budget, error_msg = get_budget_for_user(user_id, date)
    if error_msg:
        return False, None, error_msg
    if current_budgets_id == edited_budget["budget_id"]:
        return False, None, None
    return True, edited_budget["budget_id"], None


def check_if_budget_exists(budget_id: int):
    stmt = select(Budgets).filter(Budgets.id == budget_id)
    result = db.session.execute(stmt).scalar_one_or_none()
    if not result:
        return False
    return True
