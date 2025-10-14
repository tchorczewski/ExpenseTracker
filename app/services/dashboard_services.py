from datetime import datetime

from flask import jsonify

from db import db
from db.models import IncomeCategories, Incomes, Expenses, ExpenseCategories, Budgets
from sqlalchemy import select, union_all, func

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
            Expenses.date,
            ExpenseCategories.category_name,
        )
        .join(ExpenseCategories, Expenses.category_id == ExpenseCategories.category_id)
        .where(Expenses.user_id == user.user_id)
    )

    last_incomes_query = (
        select(
            Incomes.amount,
            Incomes.date,
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


def get_curr_month_expenses():
    budget_id = get_curr_month_budget_id()
    expense_stmt = (
        select(
            func.sum(Expenses.amount).label("total"),
            ExpenseCategories.category_name.label("category"),
        )
        .outerjoin(Expenses, ExpenseCategories.category_id == Expenses.category_id)
        .where(Expenses.budget_id == budget_id)
        .group_by(ExpenseCategories.category_name)
    )
    expense_sums = db.session.execute(expense_stmt).all()

    expenses = [dict(row._mapping) for row in expense_sums]
    return {
        "Category": [i["category"] for i in expenses],
        "Amount": [i["total"] if i["total"] is not None else 0 for i in expenses],
    }


def get_curr_month_incomes():
    budget_id = get_curr_month_budget_id()
    income_stmt = (
        select(
            func.sum(Incomes.amount).label("total"),
            IncomeCategories.category_name.label("category"),
        )
        .outerjoin(Incomes, IncomeCategories.category_id == Incomes.category_id)
        .where(Incomes.budget_id == budget_id)
        .group_by(IncomeCategories.category_name)
    )
    income_sums = db.session.execute(income_stmt).all()
    incomes = [dict(row._mapping) for row in income_sums]
    return {
        "Category": [i["category"] for i in incomes],
        "Amount": [i["total"] if i["total"] is not None else 0 for i in incomes],
    }


def get_curr_month_budget_id():
    now = datetime.now()
    stmt = select(Budgets.budget_id).where(
        Budgets.budget_year == now.year,
        Budgets.budget_month == now.month,
    )
    budget_id = db.session.execute(stmt).scalar_one_or_none()
    return budget_id
