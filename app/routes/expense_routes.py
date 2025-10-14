import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import OperationalError
from sqlalchemy import select, update
from datetime import datetime
from app.common.decorators import error_handler
from app.services.expenses_services import prepare_expense_data
from utils import validation
from db.models import Users, Expenses, ExpenseCategories
from db import db
from app.services.auth_services import get_auth_user

from utils.mappers import expense_mapper, category_mapper

expense_bp = Blueprint("expenses", __name__)


@expense_bp.route("/get_expenses", methods=["GET"])
@error_handler
@jwt_required()
def get_users_expenses():
    user, error_response, status_code = get_auth_user()
    if error_response:
        return error_response, status_code

    stmt = (
        select(Expenses)
        .join(Users, Expenses.user_id == Users.user_id)
        .filter(Users.user_id == user.user_id)
    )
    expenses = db.session.execute(stmt).scalars().all()

    expenses_list = [expense_mapper(expense) for expense in expenses]
    response = {"expenses": expenses_list}
    return jsonify(response), 200


@expense_bp.route("/add_expense", methods=["POST"])
@error_handler
@jwt_required()
def create_expense():
    user, error_response, status_code = get_auth_user()
    if error_response:
        return error_response, status_code

    raw_data = request.get_json()

    is_valid, error_msg = validation.validate_operation(raw_data)
    if not is_valid:
        return jsonify({"message": error_msg}), 400

    data, error_msg = prepare_expense_data(raw_data, user.user_id)
    if error_msg:
        return jsonify({"message": f"Something went wrong {error_msg}"}), 400

    expense = Expenses(**data)
    db.session.add(expense)
    db.session.commit()
    response = jsonify(expense_mapper(expense))
    return response, 201


@expense_bp.route("/<int:expense_id>/delete_expense", methods=["DELETE"])
@error_handler
@jwt_required()
# TODO Rmake this endpoint to allow expense id to be sent from frontend not to make repeated db calls
def delete_expense(expense_id):
    user, error_msg, status_code = get_auth_user()
    if error_msg:
        return error_msg, status_code

    stmt = select(Expenses).filter(Expenses.expense_id == expense_id)
    try:
        expense = db.session.execute(stmt).scalar_one_or_none()
    except OperationalError:
        msg = {"message": "Connection error"}
        return jsonify(msg), 500
    except Exception as e:
        return jsonify({"message": f"Error {str(e)}"}), 500

    if not expense:
        return jsonify({"message": "Expense not found"}), 404

    if expense.user_id != user.user_id:
        return (
            jsonify({"message": "Unauthorized"}),
            403,
        )

    db.session.delete(expense)
    db.session.commit()
    response = {"message": f"Expense {expense.expense_id} successfully deleted."}
    return jsonify(response), 200


@expense_bp.route("/edit_expense", methods=["PUT", "PATCH"])
@error_handler
@jwt_required()
def edit_expense():
    user, error_response, status_code = get_auth_user()
    if error_response:
        return error_response, status_code

    data = request.get_json()

    is_valid, error_msg = validation.validate_operation_edit(data)
    if not is_valid:
        return jsonify({"message": error_msg}), 400
    print(data)
    stmt = (
        update(Expenses)
        .where(
            Expenses.expense_id == data["expense_id"], Expenses.user_id == user.user_id
        )
        .values(**data, updated_at=datetime.now())
        .returning(Expenses)
    )
    updated_expense = db.session.execute(stmt).scalar_one_or_none()
    db.session.commit()

    return expense_mapper(updated_expense), 200


@expense_bp.route("/get_categories", methods=["GET"])
@jwt_required()
@error_handler
def get_categories():
    user, error_response, status_code = get_auth_user()
    if error_response:
        return error_response, status_code
    stmt = select(ExpenseCategories)
    results = db.session.execute(stmt).scalars().all()
    results_list = [category_mapper(row) for row in results]
    return jsonify(results_list), 200
