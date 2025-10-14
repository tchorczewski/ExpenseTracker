import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy import select, update
from sqlalchemy.exc import OperationalError
from datetime import datetime
from app.common.decorators import error_handler
from app.services.income_services import prepare_income_data
from db import db
from db.models import Users, Incomes, IncomeCategories
from utils import validation
from app.services.auth_services import get_auth_user
from utils.mappers import income_mapper, category_mapper
from utils.validation import validate_operation

income_bp = Blueprint("incomes", __name__)


@income_bp.route("/get_incomes", methods=["GET"])
@error_handler
@jwt_required()
def get_users_incomes():
    user, error_response, status_code = get_auth_user()
    if error_response:
        return error_response, status_code

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    stmt = (
        select(Incomes)
        .join(Users, Incomes.user_id == Users.user_id)
        .filter(Users.user_id == user.user_id)
        .limit(per_page)
        .offset((page - 1) * per_page)
    )
    incomes = db.session.execute(stmt).scalars().all()
    incomes_list = [income_mapper(income) for income in incomes]

    response = {"incomes": incomes_list}
    return jsonify(response), 200


@income_bp.route("/add_income", methods=["POST"])
@error_handler
@jwt_required()
def add_income():
    user, error_response, status_code = get_auth_user()
    if error_response:
        return error_response, status_code

    raw_data = request.get_json()
    is_valid, error_msg = validate_operation(raw_data)

    if not is_valid:
        return jsonify({"message": error_msg}), 400

    data, error_msg = prepare_income_data(raw_data, user.user_id)
    if error_msg:
        return jsonify({"message": f"{error_msg}"}), 400
    income = Incomes(**data)
    db.session.add(income)
    db.session.commit()
    response = jsonify(income_mapper(income))
    return response, 201


@income_bp.route("/<int:income_id>/delete_expense", methods=["DELETE"])
@error_handler
@jwt_required()
def delete_income(income_id):
    user, error_msg, status_code = get_auth_user()
    if error_msg:
        return error_msg, status_code

    stmt = select(Incomes).filter(Incomes.income_id == income_id)
    try:
        income = db.session.execute(stmt).scalar_one_or_none()
    except OperationalError:
        msg = {"message": "Connection error"}
        return jsonify(msg), 500
    except Exception as e:
        return jsonify({"message": f"Error {str(e)}"}), 500

    if not income:
        return jsonify({"message": "Expense not found"}), 404

    if income.user_id != user.user_id:
        return (
            jsonify({"message": "Unauthorized"}),
            403,
        )
    db.session.delete(income)
    db.session.commit()
    response = {"message": f"Expense {income.expense_id} successfully deleted."}
    return jsonify(response), 200


@income_bp.route("/edit_income", methods=["PUT", "PATCH"])
@error_handler
@jwt_required()
def edit_income():
    user, error_response, status_code = get_auth_user()
    if error_response:
        return error_response, status_code

    data = request.get_json()

    is_valid, error_msg = validation.validate_operation_edit(data)
    if not is_valid:
        return jsonify({"message": error_msg}), 400
    stmt = (
        update(Incomes)
        .where(Incomes.income_id == data["income_id"], Incomes.user_id == user.user_id)
        .values(**data, updated_at=datetime.now())
        .returning(Incomes)
    )
    updated_expense = db.session.execute(stmt).scalar_one_or_none()
    db.session.commit()

    return income_mapper(updated_expense), 200


@income_bp.route("/get_categories", methods=["GET"])
@jwt_required()
@error_handler
def get_categories():
    user, error_response, status_code = get_auth_user()
    if error_response:
        return error_response, status_code
    stmt = select(IncomeCategories)
    results = db.session.execute(stmt).scalars().all()
    results_list = [category_mapper(row) for row in results]
    return jsonify(results_list), 200
