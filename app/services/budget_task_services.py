from datetime import datetime
from typing import Any

from sqlalchemy import select, func, not_
from sqlalchemy.exc import OperationalError, IntegrityError
from sqlalchemy.inspection import inspect

from app.common.decorators import error_handler
from app.services.expenses_services import get_cyclical_expenses
from app.services.income_services import get_cyclical_incomes
from db import db
from app.services.date_services import get_previous_month, set_next_month
from db.models import Budgets, Users, Incomes, Expenses
from concurrent.futures import ThreadPoolExecutor


@error_handler
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
    return set(db.session.execute(missing_budget_users_stmt).scalars().all())


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
    """
    :param incomes: Incomes for given budget
    :param expenses: Expenses for given budget
    :return: Sum of incomes and expenses
    """
    return sum(item.get("amount", 0) for item in incomes) - sum(
        item.get("amount", 0) for item in expenses
    )


def clone_budget(
    budget: Budgets, budget_amount: float, exclude_fields=("budget_id", "updated_at")
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


@error_handler
def push_data(
    data: list[Budgets | Incomes | Expenses],
):
    db.session.add_all(data)
    db.session.commit()
    return True


# TODO Create abstract method to clone incomes/expenses


def clone_incomes(
    budget_id, incomes: list[Incomes], exclude_fields=("budget_id", "updated_at")
):
    incomes = [
        Incomes(
            **{
                **{
                    column.key: getattr(income, column.key)
                    for column in inspect(Incomes).column_attrs
                    if column.key not in exclude_fields
                },
                "budget_id": budget_id,
                "income_date": set_next_month(income.income_date),
            }
        )
        for income in incomes
    ]
    return incomes


def income_cloning(
    budget_id, income, exclude_fields=("budget_id", "updated_at", "created_at")
):
    mapper = inspect(Incomes)
    data = {
        column.key: getattr(income, column.key)
        for column in mapper.column_attrs
        if column.key not in exclude_fields
    }
    data["budget_id"] = budget_id
    data["income_date"] = set_next_month(income.income_date)
    return


def clone_expenses(
    budget_id,
    expenses: list[Expenses],
    exclude_fields=("budget_id", "updated_at", "created_at"),
):
    expenses = [
        Expenses(
            **{
                **{
                    column.key: getattr(expense, column.key)
                    for column in inspect(Expenses).column_attrs
                    if column.key not in exclude_fields
                },
                "budget_id": budget_id,
                "expense_date": set_next_month(expense.expense_date),
            }
        )
        for expense in expenses
    ]
    return expenses
