from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import select, union_all
from app.common.decorators import error_handler
from app.services.auth_services import get_auth_user
from db import db
from db.models import Expenses, ExpenseCategories, Incomes, IncomeCategories
from utils.mappers import last_operations_mapper

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

    if not result:
        return [], 201

    result_list = [last_operations_mapper(item) for item in result]
    return result_list, 201


@dashboard_bp.route("/plot_budget", methods=["GET"])
@error_handler
@jwt_required()
def plot_budget():
    user, error_response, status_code = get_auth_user()
    if error_response:
        return error_response, status_code
    data = {
        "Type": ["Rent", "Groceries", "Transport", "Entertainment", "Savings"],
        "Amount": [1200, 450, 150, 200, 500],
    }
    return jsonify(data) , 201


@dashboard_bp.route("/plot_expenses", methods=["GET"])
@error_handler
@jwt_required()
def plot_expenses():
    user, error_response, status_code = get_auth_user()
    if error_response:
        return error_response, status_code
    pass
