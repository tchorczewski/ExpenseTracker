from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.exc import OperationalError

from db import db
from db.models import Budgets, Users, Expenses, Incomes
from utils.mappers import budget_mapper


def get_budget_for_user(user_id, selected_date_str):
    """
    Retrieve the budget for given user and date (format: 'YYYY-MM')
    :param user_id: ID of user stored in JWT
    :param selected_date_str: Passed by the user in the request
    :return: Tuple (Budget object or None, error_message) if no budget found None, if no error, error_message is None
    """
    try:
        selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d")
    except ValueError:
        return None, None, "Invalid date format. Expected YYYY-MM-DD"

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
            return None, None, "No budget for selected period"
        return result, budget_mapper(result), None
    except OperationalError:
        return None, None, "Connection error"
    except Exception as e:
        return None, None, f"Unexpected error {str(e)}"


def prepare_budget_data(data, user_id):
    data["user_id"] = user_id
    data["budget_amount"] = float(data.get("budget_amount", "0"))
    data["budget_month"] = int(data["budget_month"])
    data["budget_year"] = int(data["budget_year"])
    data["status_id"] = 1
    data["created_at"] = datetime.now().strftime("%Y-%m-%d")
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


def check_budget_generation_status(budget, user, budget_id):
    if budget.is_generated:
        expense_stmt = (
            select(func.sum(Expenses.amount))
            .join(Users, Expenses.user_id == Users.user_id)
            .where(Users.user_id == user.user_id)
            .where(Expenses.budget_id == budget_id)
            .where(Expenses.is_cyclical == False)
        )
        income_stmt = (
            select(func.sum(Incomes.amount))
            .join(Users, Incomes.user_id == Users.user_id)
            .where(Users.user_id == user.user_id)
            .where(Incomes.budget_id == budget_id)
            .where(Incomes.is_cyclical == False)
        )
    else:
        expense_stmt = (
            select(func.sum(Expenses.amount))
            .join(Users, Expenses.user_id == Users.user_id)
            .where(Users.user_id == user.user_id)
            .where(Expenses.budget_id == budget_id)
            .where(Expenses.is_cyclical == True)
        )
        income_stmt = (
            select(func.sum(Incomes.amount))
            .join(Users, Incomes.user_id == Users.user_id)
            .where(Users.user_id == user.user_id)
            .where(Incomes.budget_id == budget_id)
            .where(Incomes.is_cyclical == True)
        )

    return expense_stmt, income_stmt
