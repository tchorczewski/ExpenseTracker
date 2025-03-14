from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from db import db
from db.models import Budgets, Users
from utils import helpers
from sqlalchemy.exc import IntegrityError, OperationalError
from datetime import datetime
from sqlalchemy import select
from utils.mappers import budget_mapper
from utils.validation import validate_budget

budget_bp = Blueprint("budget", __name__)


@budget_bp.route("/get_budget", methods=["GET"])
@jwt_required()
def get_any_budget():
    """
    Display budget for a selected month
    :return: Budget amount if set, None if not set
    """
    user_id = helpers.get_user_id_from_token()
    if not user_id:
        return jsonify({"message": "Unauthorized"}), 401
    selected_date = datetime.strptime(request.form["date"], "%Y-%m")
    if not selected_date:
        return jsonify({"message": "Date not provided"}), 401

    budget, error_msg = helpers.get_budget_for_user(user_id, selected_date)
    if error_msg:
        return jsonify({"message": error_msg})

    return jsonify(budget), 200


@budget_bp.route("/get_all_budgets", methods=["GET"])
@jwt_required()
def get_all_budgets():
    user_id = helpers.get_user_id_from_token()
    if not user_id:
        return jsonify({"message": "Unauthorized"}), 401
    user = helpers.get_current_user(user_id)
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
    user_id = helpers.get_user_id_from_token()
    if not user_id:
        return jsonify({"message": "Unauthorized"}), 401
    user = helpers.get_current_user(user_id)
    current_month, current_year = datetime.now().month, datetime.now().year
    try:
        stmt = (
            select(Budgets)
            .join(Users, Budgets.user_id == Users.user_id)
            .filter(Users.user_id == user.user_id)
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


@budget_bp.route("/create_budget", methods=["POST"])
@jwt_required()
def create_budget():
    user_id = helpers.get_user_id_from_token()
    if not user_id:
        return jsonify({"message": "Unauthorized"}), 401
    user = helpers.get_current_user(user_id)
    raw_data = request.form.to_dict()
    is_valid, error_msg = validate_budget(raw_data)
    if not is_valid:
        return jsonify({"message": f"Something went wrong {error_msg}"}), 400
    data = helpers.prepare_budget_data(raw_data, user.user_id)
    selected_date = f"{data['budget_year']}-{data['budget_month']}"
    existing_budget, _ = helpers.get_budget_for_user(user_id, selected_date)
    if existing_budget:
        return jsonify({"message": "Budget already exists"}), 409

    budget = Budgets(**data)
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
