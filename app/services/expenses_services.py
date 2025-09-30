from datetime import datetime

from sqlalchemy import select

from app.common.decorators import error_handler
from app.services.budget_services import get_budget_for_user
from db import db
from db.models import Expenses
from utils.mappers import expense_mapper


def prepare_expense_data(data: dict, user_id: int) -> (dict, str):
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
    _, budget, error_msg = get_budget_for_user(user_id, data["expense_date"])
    if error_msg:
        return None, f"Something went wrong {error_msg}"
    data["budget_id"] = budget.get("budget_id")
    data["is_cyclical"] = data["is_cyclical"].lower() == "true"
    return data, None


@error_handler
def get_cyclical_expenses(budget_id: int):
    cyclical_expenses_stmt = select(Expenses.amount).filter(
        Expenses.budget_id == budget_id,
        Expenses.is_cyclical == True,
    )
    result = db.session.execute(cyclical_expenses_stmt).scalars().all()
    return result
