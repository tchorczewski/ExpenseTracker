from datetime import datetime

from sqlalchemy import select

from app.common.decorators import error_handler
from app.services.budget_services import get_budget_for_user
from db import db
from db.models import Expenses
from utils.mappers import expense_mapper


def prepare_expense_data(data: dict, user_id: int) -> (dict, str | None):
    """
    :param data: Dictionary form of data from request
    :param user_id: User_id from jwt identity
    :return: Filled data dictionary and an error message if budget returns nothing
    """
    data["amount"] = float(data.get("amount", "0"))
    data["user_id"] = user_id
    data["created_at"] = datetime.now().strftime("%Y-%m-%d")
    data["updated_at"] = None
    return data, None


@error_handler
def get_cyclical_expenses(budget_id: int):
    cyclical_expenses_stmt = select(Expenses.amount).filter(
        Expenses.budget_id == budget_id,
        Expenses.is_cyclical == True,
    )
    result = db.session.execute(cyclical_expenses_stmt).scalars().all()
    return result
