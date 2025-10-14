from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.exc import OperationalError

from app.common.decorators import error_handler
from app.services.budget_services import get_budget_for_user
from db import db
from db.models import Incomes
from utils.mappers import income_mapper


def prepare_income_data(data: dict, user_id: int):
    data["user_id"] = user_id
    data["amount"] = float(data.get("amount", "0"))
    data["created_at"] = datetime.now().strftime("%Y-%m-%d")
    data["updated_at"] = None
    return data, None


@error_handler
def get_cyclical_incomes(budget_id: int):
    cyclical_expenses_stmt = select(Incomes).filter(
        Incomes.budget_id == budget_id,
        Incomes.is_cyclical == True,
    )
    result = db.session.execute(cyclical_expenses_stmt).scalars().all()
    incomes_list = [income_mapper(income) for income in result]
    return incomes_list
