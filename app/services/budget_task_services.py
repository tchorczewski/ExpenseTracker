from datetime import datetime
from typing import Any

from sqlalchemy import select, func, not_
from sqlalchemy.exc import OperationalError, IntegrityError
from sqlalchemy.inspection import inspect

from app.services.expenses_services import get_cyclical_expenses
from app.services.income_services import get_cyclical_incomes
from db import db
from app.services.date_services import get_previous_month
from db.models import Budgets, Users
from concurrent.futures import ThreadPoolExecutor


def get_users_with_missing_budget() -> dict[str, str] | set[Any]:
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
        return set(db.session.execute(missing_budget_users_stmt).scalars().all())
    except OperationalError:
        # TODO Standardize returns, add logging, create something to avoid multiple if none checks (decorator maybe?)
        return {"message": "Database connection issue"}
    except Exception as e:
        return {"error": str(e)}


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


def clone_budget(
    budget: Budgets, budget_amount: float, exclude_fields=("budget_id",)
) -> Budgets:
    if budget_amount == 0:
        budget_amount = budget.budget_amount
    mapper = inspect(Budgets)
    data = {
        column.key: getattr(budget, column.key)
        for column in mapper.column_attrs
        if column.key not in exclude_fields
    }
    data["budget_amount"] = budget_amount
    data["budget_year"] = datetime.now().year
    data["budget_month"] = datetime.now().month
    return Budgets(**data)


def push_budget(budgets: list[Budgets]):  # TODO Logging
    try:
        db.session.add_all(budgets)
        db.session.commit()
        return True
    except IntegrityError:
        db.session.rollback()
        return False
    except OperationalError:
        db.session.rollback()
        return False
    except Exception as e:
        db.session.rollback()
        return False


def create_cyclical_incomes():
    pass


def create_cyclical_expenses():
    pass
