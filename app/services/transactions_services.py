from datetime import datetime

from sqlalchemy import select, update

from app.common.decorators import error_handler
from db import db
from db.models import Transactions, Categories
from utils.mappers import category_mapper, transaction_mapper


def prepare_transaction_data(data: dict, user_id: int) -> object:
    """
    :param data: Dictionary form of data from request
    :param user_id: User_id from jwt identity
    :return: Filled data dictionary and an error message if budget returns nothing
    """
    data["amount"] = float(data.get("amount", "0"))
    data["user_id"] = user_id
    data["date"] = datetime.fromisoformat(data["date"])
    data["created_at"] = datetime.now()
    data["updated_at"] = None
    return data, None


@error_handler
def get_cyclical_transactions(budget_id: int) -> Transactions:

    cyclical_expenses_stmt = (
        select(Transactions)
        .where(Transactions.budget_id == budget_id, Transactions.is_cyclical == True)
        .order_by(Transactions.type)
    )
    result = db.session.execute(cyclical_expenses_stmt).scalars().all()
    return result


def fetch_categories() -> dict:
    stmt = select(Categories)
    results = db.session.execute(stmt).scalars().all()
    categories = {"income": [], "expense": []}
    results_list = [category_mapper(row) for row in results]
    for c in results_list:
        categories[c["type"]].append({"id": c["id"], "name": c["name"]})
    return categories


def push_edited_transaction(data, user):
    stmt = (
        update(Transactions)
        .where(Transactions.id == data["id"], Transactions.user_id == user.id)
        .values(**data, updated_at=datetime.now())
        .returning(Transactions)
    )
    updated_transaction = db.session.execute(stmt).scalar_one_or_none()
    db.session.commit()
    return updated_transaction


def transaction_getter(user):
    stmt = select(Transactions).where(Transactions.user_id == user.id)
    transactions = db.session.execute(stmt).scalars().all()

    transactions_list = [
        transaction_mapper(transaction) for transaction in transactions
    ]
    types = {"income": [], "expense": []}
    for t in transactions_list:
        types[t["type"]].append(t)
    return types
