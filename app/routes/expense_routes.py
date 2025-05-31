import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy import select

from app.services.budget_services import verify_budget_change
from app.services.expenses_services import prepare_expense_data
from utils import validation
from db.models import Users, Expenses
from db import db
from app.services.auth_services import get_auth_user

from utils.mappers import expense_mapper

expense_bp = Blueprint("expenses", __name__)


@expense_bp.route("/get_expenses", methods=["GET"])
@jwt_required()
def get_users_expenses():
    user, error_response, status_code = get_auth_user()
    if error_response:
        return error_response, status_code

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    try:
        stmt = (
            select(Expenses)
            .join(Users, Expenses.user_id == Users.user_id)
            .filter(Users.user_id == user.user_id)
            .limit(per_page)
            .offset((page - 1) * per_page)
        )
        expenses = db.session.execute(stmt).scalars().all()

        expenses_list = [expense_mapper(expense) for expense in expenses]
        response = {"expenses": expenses_list}
        return jsonify(response), 200

    except OperationalError:
        msg = {"message": "Connection error"}
        return jsonify(msg), 500
    except Exception as e:
        return jsonify({"message": f"Error {str(e)}"}), 500


@expense_bp.route("/add_expense", methods=["POST"])
@jwt_required()
def add_expense():
    user, error_response, status_code = get_auth_user()
    if error_response:
        return error_response, status_code

    raw_data = request.form.to_dict()

    is_valid, error_msg = validation.validate_expense(raw_data)
    if not is_valid:
        return jsonify({"message": error_msg}), 400

    data, error_msg = prepare_expense_data(raw_data, user.user_id)
    if error_msg:
        return jsonify({"message": f"Something went wrong {error_msg}"}), 400

    expense = Expenses(**data)
    try:
        db.session.add(expense)
        db.session.commit()
        response = jsonify(expense_mapper(expense))
        return response, 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "Database integrity error"}), 400
    except OperationalError:
        db.session.rollback()
        return jsonify({"message": "Database connection issue"}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@expense_bp.route("/<int:expense_id>/delete_expense", methods=["DELETE"])
@jwt_required()
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

    try:
        db.session.delete(expense)
        db.session.commit()
        response = {"message": f"Expense {expense.expense_id} successfully deleted."}
        return jsonify(response), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "Database integrity error"}), 400
    except OperationalError:
        db.session.rollback()
        return jsonify({"message": "Database connection issue"}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@expense_bp.route("/<int:expense_id>/edit_expense", methods=["PUT", "PATCH"])
@jwt_required()
def edit_expense(expense_id):
    user, error_response, status_code = get_auth_user()
    if error_response:
        return error_response, status_code

    expense = Expenses.query.get(expense_id)

    if not expense:
        return jsonify({"message": "Expense not found"}), 404
    if user.user_id != expense.user_id:
        return (
            jsonify({"message": "Unauthorized"}),
            403,
        )

    data = request.form.to_dict()
    if request.method == "PUT":
        is_valid, check_new_budget_id, error_msg = validation.validate_expense_edit(
            data
        )
        if not is_valid:
            return jsonify({"message": error_msg}), 400

    if request.method == "PATCH":
        is_valid, check_new_budget_id, error_msg = validation.validate_expense_edit(
            data, is_patch=True
        )
        if not is_valid:
            return jsonify({"message": error_msg}), 400

    if check_new_budget_id:
        status, new_budget_id, error_msg = verify_budget_change(
            user.user_id, data["expense_date"], expense.budget_id
        )
        if error_msg:
            return jsonify({"message": error_msg}), 400
        if status:
            expense.budget_id = new_budget_id

    for key, value in data.items():
        setattr(expense, key, float(value) if key == "amount" else value)
    expense.updated_at = datetime.datetime.now()
    try:
        db.session.commit()
        response = {
            "message": f"Expense {expense.expense_id} successfully updated",
            "updated_expense": {
                field: getattr(expense, field)
                for field in expense.__table__.columns.keys()
            },
        }
        return jsonify(response), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "Database integrity error"}), 400
    except OperationalError:
        db.session.rollback()
        return jsonify({"message": "Database connection issue"}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
