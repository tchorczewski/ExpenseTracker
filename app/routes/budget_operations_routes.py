from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy import select, func
from sqlalchemy.exc import OperationalError, IntegrityError
from db import db
from db.models import Expenses, Users, Incomes, Budgets
from utils.helpers import get_auth_user

operations_bp = Blueprint("operations", __name__)


@operations_bp.route("/<int:budget_id>/get_current_budget", methods=["GET"])
@jwt_required()
def fetch_budget_summary(budget_id):
    user, error_response, status_code = get_auth_user()
    if error_response:
        return error_response, status_code

    try:
        expense_stmt = (
            select(func.sum(Expenses.amount))
            .join(Users, Expenses.user_id == Users.user_id)
            .where(Users.user_id == user.user_id)
            .where(Expenses.budget_id == budget_id)
            .where(Expenses.is_cyclical == False)
        )
        income_stmt = (
            select(func.sum(Incomes.amount))
            .join(Users, Incomes.user_id == Users.user_id)
            .where(Users.user_id == user.user_id)
            .where(Incomes.budget_id == budget_id)
            .where(Incomes.is_cyclical == False)
        )
        budget_stmt = (
            select(Budgets.budget_amount)
            .join(Users, Budgets.user_id == Users.user_id)
            .where(Budgets.budget_id == budget_id)
        )
        budget = db.session.execute(budget_stmt).scalar_one_or_none()
        if budget is None:
            return jsonify({"message": "Budget not created for given month"}), 400

        additional_expenses = db.session.execute(expense_stmt).scalar_one_or_none()
        if not additional_expenses:
            additional_expenses = 0

        additional_incomes = db.session.execute(income_stmt).scalar_one_or_none()
        if not additional_incomes:
            additional_incomes = 0

        return jsonify(
            {
                "message": f"Budget status: {(budget + additional_incomes) - additional_expenses}"
            }
        )

    except OperationalError:
        msg = {"message": "Connection error"}
        return jsonify(msg), 500
    except Exception as e:
        return jsonify({"message": f"Error {str(e)}"}), 500
