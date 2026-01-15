from datetime import datetime
from flask import jsonify
from sqlalchemy import select, update
from db import db
from db.models import Budgets, Statuses, Transactions, Categories
from utils.mappers import budget_mapper, status_mapper, transaction_mapper
from utils.validation import validate_budget


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
        return None, None
    return result, budget_mapper(result)


def map_budget_data(data: dict, user_id: int):
    data["user_id"] = user_id
    data["amount"] = float(data.get("amount", "0"))
    data["budget_month"] = int(data["budget_month"])
    data["budget_year"] = int(data["budget_year"])
    data["status_id"] = 3
    data["is_generated"] = bool(data["is_generated"])
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


def status_getter():
    stmt = select(Statuses)
    results = db.session.execute(stmt).scalars().all()
    results_list = [status_mapper(row) for row in results]
    statuses = {"users": [], "budgets": []}
    for t in results_list:
        statuses[t["type"]].append(t)
    return statuses


def budgets_getter(user):
    stmt = (
        select(Budgets, Statuses.name)
        .outerjoin(Statuses, Budgets.status_id == Statuses.id)
        .filter(Budgets.user_id == user.id)
    )
    result = db.session.execute(stmt).all()
    if not result:
        return None
    budgets_list = [budget_mapper(row.Budgets, row.name) for row in result]
    return budgets_list


def budget_details(budget_id):
    transactions_stmt = (
        select(Transactions, Categories.name)
        .join(Categories, Transactions.category_id == Categories.id)
        .where(Transactions.budget_id == budget_id)
    )

    results = db.session.execute(transactions_stmt).all()
    transactions = {"income": [], "expense": []}
    for t, category in results:
        transactions[t.type].append(transaction_mapper(t, category))
    return transactions


def check_existing_budget(user, month, year):
    existing_budget, _ = get_budget_for_user(
        user.id,
        int(month),
        int(year),
    )
    return existing_budget


def prepare_budget_data(raw_data, user) -> dict:
    data = map_budget_data(raw_data, user.id)
    return data


def push_edited_budget(data):
    stmt = (
        update(Budgets)
        .where(Budgets.id == data["id"])
        .values(**data, updated_at=datetime.now())
        .returning(Budgets)
    )
    updated_budget = db.session.execute(stmt).scalar_one_or_none()
    db.session.commit()
    return updated_budget
