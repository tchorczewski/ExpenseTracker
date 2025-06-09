from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import selectinload
from db import db
from db.models import Budgets, Users
from utils import validation
from sqlalchemy.exc import IntegrityError, OperationalError
from datetime import datetime
from sqlalchemy import select
from app.services.budget_services import get_budget_for_user, prepare_budget_data
from app.services.date_services import parse_date
from app.services.auth_services import get_auth_user
from utils.mappers import budget_mapper, expense_mapper
from utils.validation import validate_budget

budget_bp = Blueprint("budget", __name__)


@budget_bp.route("/get_budget", methods=["GET"])
@jwt_required()
def get_any_budget():
    """
    Display budget for a selected month
    :return: Budget amount if set, None if not set
    """
    user, error_response, status_code = get_auth_user()
    if error_response:
        return error_response, status_code
    selected_date = datetime.strptime(request.form["date"], "%Y-%m")
    if not selected_date:
        return jsonify({"message": "Date not provided"}), 401

    _, mapped_budget, error_msg = get_budget_for_user(user.user_id, selected_date)
    if error_msg:
        return jsonify({"message": error_msg})

    return jsonify(mapped_budget), 200


@budget_bp.route("/get_all_budgets", methods=["GET"])
@jwt_required()
def get_all_budgets():
    user, error_response, status_code = get_auth_user()
    if error_response:
        return error_response, status_code
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    try:
        stmt = (
            select(Budgets)
            .join(Users, Budgets.user_id == Users.user_id)
            .filter(Users.user_id == user.user_id)
            .limit(per_page)
            .offset((page - 1) * per_page)
        )
        result = db.session.execute(stmt).scalars().all()
        if not result:
            return jsonify({"message": "User has no budgets"}), 404
        budgets_list = [budget_mapper(budget) for budget in result]
        response = {"budgets": budgets_list}
        return jsonify(response), 200
    except OperationalError:
        msg = {"message": "Connection error"}
        return jsonify(msg), 500
    except Exception as e:
        return jsonify({"message": f"Error {str(e)}"}), 500


@budget_bp.route("/get_current_budget", methods=["GET"])
@jwt_required()
def get_current_months_budget():
    user, error_response, status_code = get_auth_user()
    if error_response:
        return error_response, status_code
    current_month, current_year = datetime.now().month, datetime.now().year
    try:
        stmt = (
            select(Budgets)
            .join(Users, Budgets.user_id == Users.user_id)
            .filter(Budgets.user_id == user.user_id)
            .filter(Budgets.budget_month == current_month)
            .filter(Budgets.budget_year == current_year)
        )
        result = db.session.execute(stmt).scalar_one_or_none()
        if not result:
            return jsonify({"message": "No budget for this period"}), 404
        return jsonify(budget_mapper(result)), 200
    except OperationalError:
        msg = {"message": "Connection error"}
        return jsonify(msg), 500
    except Exception as e:
        return jsonify({"message": f"Error {str(e)}"}), 500


@budget_bp.route("/<int:budget_id>/get_budget_details", methods=["GET"])
@jwt_required()
def get_budget_details(budget_id):
    user, error_response, status_code = get_auth_user()
    if error_response:
        return error_response, status_code
    stmt = (
        select(Budgets)
        .options(selectinload(Budgets.expenses))
        .filter(Budgets.budget_id == budget_id, Budgets.user_id == user.user_id)
    )
    try:
        budgets = db.session.execute(stmt).scalars().first()
        expenses = [expense_mapper(expense) for expense in budgets.expenses]
        return jsonify({"budget": budget_mapper(budgets), "expenses": expenses}), 200
    except OperationalError:
        return jsonify({"message": "Database connection issue"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@budget_bp.route("/create_budget", methods=["POST"])
@jwt_required()
def create_budget():
    user, error_response, status_code = get_auth_user()
    if error_response:
        return error_response, status_code
    raw_data = request.form.to_dict()
    is_valid, error_msg = validate_budget(raw_data)
    if not is_valid:
        return jsonify({"message": f"Something went wrong {error_msg}"}), 400
    data = prepare_budget_data(raw_data, user.user_id)
    existing_budget, _, _ = get_budget_for_user(
        user.user_id, parse_date(data["budget_year"], data["budget_month"])
    )
    if existing_budget:
        return jsonify({"message": "Budget already exists"}), 409

    budget = Budgets(**data)
    budget.is_generated = bool(budget.is_generated)  # TODO Clean the workaround
    try:
        db.session.add(budget)
        db.session.commit()
        response = jsonify(budget_mapper(budget))
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


@budget_bp.route("/<int:budget_id>/edit_budget", methods=["PUT", "PATCH"])
@jwt_required()
def edit_budget(budget_id):
    user, error_response, status_code = get_auth_user()
    if error_response:
        return error_response, status_code

    budget = db.session.execute(
        (select(Budgets).where(Budgets.budget_id == budget_id))
    ).scalar_one_or_none()

    if not budget:
        return jsonify({"message": "Budget not found"}), 404
    if user.user_id != budget.user_id:
        return (
            jsonify({"message": "Unauthorized"}),
            403,
        )

    data = request.form.to_dict()
    if request.method == "PUT":
        is_valid, error_msg = validation.validate_budget_edit(data)
        if not is_valid:
            return jsonify({"message": error_msg}), 400

    if request.method == "PATCH":
        is_valid, error_msg = validation.validate_budget_edit(data, is_patch=True)
        if not is_valid:
            return jsonify({"message": error_msg}), 400

    for key, value in data.items():
        if key == "budget_amount":
            setattr(budget, key, float(value))
        elif key == "is_generated":
            setattr(budget, key, data["is_generated"].lower() == "true")
        else:
            setattr(budget, key, value)

    budget.updated_at = datetime.now()
    try:
        db.session.commit()
        response = {
            "message": f"Budget {budget.budget_id} successfully updated",
            "updated_budget": {
                field: getattr(budget, field)
                for field in budget.__table__.columns.keys()
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
