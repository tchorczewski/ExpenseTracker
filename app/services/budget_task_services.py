from datetime import datetime
from sqlalchemy import select, func, not_
from sqlalchemy.exc import OperationalError
from app.services.expenses_services import get_cyclical_expenses
from app.services.income_services import get_cyclical_incomes
from db import db
from app.services.date_services import get_previous_month
from db.models import Budgets, Users
from concurrent.futures import ThreadPoolExecutor


def get_users_with_missing_budget() -> tuple:
    previous_year, previous_month = get_previous_month()
    current_year, current_month = datetime.now().year, datetime.now().month
    current_month_subq = select(Budgets.user_id).filter(
        Budgets.budget_month == current_month, Budgets.budget_year == current_year
    )

    missing_budget_users_stmt = select(func.distinct(Users.user_id)).filter(
        Budgets.budget_year == previous_year,
        Budgets.budget_month == previous_month,
        not_(Budgets.user_id.in_(current_month_subq)),
    )
    try:
        return (
            set(db.session.execute(missing_budget_users_stmt).scalars().all()),
            previous_year,
            previous_month,
        )
    except OperationalError:
        return {"message": "Database connection issue"}, None, None
    except Exception as e:
        return {"error": str(e)}, None, None


def get_cyclical_data(budget_id: int) -> tuple:
    """
    Performs calls to db to get cyclical incomes and expenses and returns them as a Tuple
    :param budget_id: Budget_id for which the cyclical incomes and expenses are to be returned
    :return: Tuple of all cyclical incomes and expenses for given budget
    """
    with ThreadPoolExecutor(max_workers=2) as executor:
        previous_incomes = executor.submit(get_cyclical_incomes, budget_id)
        previous_expenses = executor.submit(get_cyclical_expenses, budget_id)

        incomes = previous_incomes.result()
        expenses = previous_expenses.result()

        return incomes, expenses


def calculate_budget_amount(incomes: list, expenses: list) -> float:
    return sum(item.get("amount", 0) for item in incomes) - sum(
        item.get("amount", 0) for item in expenses
    )
