import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy import select
from sqlalchemy.exc import OperationalError, IntegrityError

from app.services.budget_services import verify_budget_change
from app.services.income_services import prepare_income_data
from db import db
from db.models import Users, Incomes
from utils import validation
from app.services.auth_services import get_auth_user
from utils.mappers import income_mapper
from utils.validation import validate_income

income_bp = Blueprint("incomes", __name__)


@income_bp.route("/get_incomes", methods=["GET"])
@jwt_required()
def get_users_incomes():
    user, error_response, status_code = get_auth_user()
    if error_response:
        return error_response, status_code

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    try:
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

    except OperationalError:
        msg = {"message": "Connection error"}
        return jsonify(msg), 500
    except Exception as e:
        return jsonify({"message": f"Error {str(e)}"}), 500


@income_bp.route("/add_income", methods=["POST"])
@jwt_required()
def create_income():
    user, error_response, status_code = get_auth_user()
    if error_response:
        return error_response, status_code

    raw_data = request.form.to_dict()
    is_valid, error_msg = validate_income(raw_data)

    if not is_valid:
        return jsonify({"message": error_msg}), 400

    data, error_msg = prepare_income_data(raw_data, user.user_id)
    if error_msg:
        return jsonify({"message": f"{error_msg}"}), 400
    income = Incomes(**data)
    try:
        db.session.add(income)
        db.session.commit()
        response = jsonify(income_mapper(income))
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


@income_bp.route("/<int:income_id>/delete_expense", methods=["DELETE"])
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

    try:
        db.session.delete(income)
        db.session.commit()
        response = {"message": f"Expense {income.expense_id} successfully deleted."}
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


@income_bp.route("/<int:income_id>/edit_income", methods=["PUT", "PATCH"])
@jwt_required()
def edit_income(income_id):
    user, error_response, status_code = get_auth_user()
    if error_response:
        return error_response, status_code

    income = Incomes.query.get(income_id)

    if not income:
        return jsonify({"message": "Income not found"}), 404
    if user.user_id != income.user_id:
        return (
            jsonify({"message": "Unauthorized"}),
            403,
        )

    data = request.form.to_dict()
    if request.method == "PUT":
        is_valid, check_new_budget_id, error_msg = validation.validate_income_edit(data)
        if not is_valid:
            return jsonify({"message": error_msg}), 400

    if request.method == "PATCH":
        is_valid, check_new_budget_id, error_msg = validation.validate_income_edit(
            data, is_patch=True
        )
        if not is_valid:
            return jsonify({"message": error_msg}), 400

    if check_new_budget_id:
        status, new_budget_id, error_msg = verify_budget_change(
            user.user_id, data["income_date"], income.budget_id
        )
        if error_msg:
            return jsonify({"message": error_msg}), 400
        if status:
            income.budget_id = new_budget_id

    for key, value in data.items():
        setattr(income, key, float(value) if key == "amount" else value)
    income.updated_at = datetime.datetime.now()
    try:
        db.session.commit()
        response = {
            "message": f"Income {income.income_id} successfully updated",
            "updated_expense": {
                field: getattr(income, field)
                for field in income.__table__.columns.keys()
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
