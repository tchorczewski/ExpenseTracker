from datetime import datetime

from flask import jsonify

from db import db
from db.models import Budgets, Transactions, Categories
from sqlalchemy import select, union_all, func

from utils.mappers import last_operations_mapper


def get_recent_operations(user):
    """
    This method gets 5 most recent expenses/incomes based on user
    :param user: Current user, passed from JWT
    :return: List of 5 most recent incomes/expenses
    """
    last_transactions_stmt = (
        select(
            Transactions.amount, Transactions.date, Categories.name, Transactions.type
        )
        .join(Categories, Transactions.category_id == Categories.id)
        .where(Transactions.user_id == user.id)
        .order_by(Transactions.date.desc())
        .limit(5)
    )

    result = db.session.execute(last_transactions_stmt).all()
    result_list = [last_operations_mapper(item) for item in result]

    return result_list


def get_curr_month_transactions(user_id):
    """
    Gets all transactions for user, in current month
    :param user_id:
    :return:
    """
    budget_id = get_curr_month_budget_id(user_id)
    transaction_stmt = (
        select(
            func.sum(Transactions.amount).label("total"),
            Categories.name.label("category"),
            Transactions.type,
        )
        .outerjoin(Transactions, Categories.id == Transactions.category_id)
        .where(Transactions.budget_id == budget_id)
        .group_by(Categories.name, Transactions.type)
    )
    transactions_sums = db.session.execute(transaction_stmt).all()

    transactions = [dict(row._mapping) for row in transactions_sums]
    result = {"income": [], "expense": []}
    for t in transactions:
        result[t["type"]].append(
            {"Category": t["category"], "Amount": float(t["total"])}
        )

    return result


def get_curr_month_budget_id(user_id):
    now = datetime.now()
    stmt = select(Budgets.id).where(
        Budgets.budget_year == now.year,
        Budgets.budget_month == now.month,
        Budgets.user_id == user_id,
    )
    budget_id = db.session.execute(stmt).scalar_one_or_none()
    return budget_id
