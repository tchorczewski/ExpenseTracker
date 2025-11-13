from datetime import datetime
from typing import Any

from sqlalchemy import select, func, not_
from sqlalchemy.inspection import inspect

from app.common.decorators import error_handler
from app.services.transactions_services import get_cyclical_transactions
from db import db
from app.services.date_services import get_previous_month, set_next_month
from db.models import Budgets, Users, Transactions


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


def get_cyclical_data(budget_id: int):
    """
    Gets transactions marked as cyclical
    :param budget_id: Budget_id for which the cyclical incomes and expenses are to be returned
    :return:
    """
    transactions = get_cyclical_transactions(budget_id)

    return transactions


def calculate_budget_amount(transactions: list[Transactions]) -> float:
    """
    Calculates the budget for given month based on cyclical transactions
    :param transactions: List of cyclical transactions
    :return:
    """
    incomes = expenses = 0
    for t in transactions:
        if t["type"] == "income":
            incomes += t["amount"]
        else:
            expenses += t["amount"]

    return incomes - expenses


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
def push_data(data: list[Budgets | Transactions]) -> bool:
    db.session.add_all(data)
    db.session.commit()
    return True


# TODO Create abstract method to clone incomes/expenses


def clone_transactions(
    budget_id: int,
    transactions: list[Transactions],
    exclude_fields=("budget_id", "updated_at"),
):
    cloned = [
        Transactions(
            **{
                **{
                    column.key: getattr(transaction, column.key)
                    for column in inspect(Transactions).column_attrs
                    if column.key not in exclude_fields
                },
                "budget_id": budget_id,
                "date": set_next_month(transaction.date),
            }
        )
        for transaction in transactions
    ]
    return cloned
