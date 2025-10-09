from db import db
from db.models import IncomeCategories, Incomes, Expenses, ExpenseCategories
from sqlalchemy import select, union_all

from utils.mappers import last_operations_mapper


def get_recent_operations(user):
    """
    This method gets 5 most recent expenses/incomes based on user
    :param user: Current user, passed from JWT
    :return: List of 5 most recent incomes/expenses
    """
    last_expenses_query = (
        select(
            Expenses.amount,
            Expenses.expense_date.label("date"),
            ExpenseCategories.category_name,
        )
        .join(ExpenseCategories, Expenses.category_id == ExpenseCategories.category_id)
        .where(Expenses.user_id == user.user_id)
    )

    last_incomes_query = (
        select(
            Incomes.amount,
            Incomes.income_date.label("date"),
            IncomeCategories.category_name,
        )
        .join(IncomeCategories, Incomes.category_id == IncomeCategories.category_id)
        .where(Incomes.user_id == user.user_id)
    )

    combined = union_all(last_expenses_query, last_incomes_query).subquery("combined")

    last_operations_stmt = (
        select(
            combined.c.amount,
            combined.c.date,
            combined.c.category_name,
        )
        .order_by(combined.c.date.desc())
        .limit(5)
    )
    result = db.session.execute(last_operations_stmt).all()
    result_list = [last_operations_mapper(item) for item in result]

    return result_list
