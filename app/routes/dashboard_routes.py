from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import select, union, union_all
from app.common.decorators import error_handler
from app.services.auth_services import get_auth_user
from db import db
from db.models import Expenses, ExpenseCategories, Incomes, IncomeCategories

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard_bp.route("/get_last_operations", methods=["GET"])
@error_handler
@jwt_required()
def get_last_operations():
    user, error_response, status_code = get_auth_user()
    if error_response:
        return error_response, status_code
    last_expenses_query = (
        select(
            Expenses.amount,
            Expenses.expense_date.label("date"),
            ExpenseCategories.category_name,
        )
        .join(ExpenseCategories, Expenses.category_id == ExpenseCategories.category_id)
        .where(Incomes.user_id == user.user_id)
    )

    last_incomes_query = (
        select(
            Incomes.amount,
            Incomes.income_date.label("date"),
            IncomeCategories.category_name,
        )
        .join(Incomes, Incomes.income_date.label("income_date"))
        .where(Expenses.user_id == user.user_id)
    )

    combined = union_all(last_expenses_query, last_incomes_query).subquery("combined")

    last_operations_stmt = (
        select(
            combined.c.amount,
            combined.c.date,
            combined.c.category_name,
            combined.c.type,
        )
        .order_by(combined.c.date.desc())
        .limit(5)
    )

    result = db.session.execute(last_operations_stmt)

    return jsonify(result), 201


"""
#TODO COnvert this stuff
SELECT * FROM 
(SELECT expenses.amount, expense_date as date, expense_categories.category_name FROM expenses
INNER JOIN expense_categories ON expenses.category_id = expense_categories.category_id
WHERE user_id = 1

UNION ALL

SELECT incomes.amount, income_date as date, income_categories.category_name FROM incomes
INNER JOIN income_categories ON incomes.category_id = income_categories.category_id
WHERE user_id = 1)  as combined
Order BY date DESC
Limit 5
into an endpoint to call
"""
