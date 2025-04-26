from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy import select, func
from sqlalchemy.exc import OperationalError, IntegrityError
from db import db
from db.models import Expenses, Users, Incomes, Budgets
from utils.helpers import get_auth_user, check_budget_generation_status

operations_bp = Blueprint("operations", __name__)


@operations_bp.route("/<int:budget_id>/get_current_budget", methods=["GET"])
@jwt_required()
def fetch_budget_summary(budget_id):
    # Need to check the method of budget generation and adjust the income and expense statements to include/exclude cyclical ones
    user, error_response, status_code = get_auth_user()
    if error_response:
        return error_response, status_code
    try:
        budget_stmt = (
            select(Budgets.budget_amount)
            .join(Users, Budgets.user_id == Users.user_id)
            .where(Budgets.budget_id == budget_id)
        )
        budget = db.session.execute(budget_stmt).scalar_one_or_none()
        if budget is None:
            return jsonify({"message": "Budget not created for given month"}), 400
        expense_stmt, income_stmt = check_budget_generation_status(
            budget, user, budget_id
        )
        additional_expenses = db.session.execute(expense_stmt).scalar_one_or_none()
        additional_incomes = db.session.execute(income_stmt).scalar_one_or_none()
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
