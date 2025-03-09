from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from db import db
from db.models import Budgets, Users
from utils import helpers
from sqlalchemy.exc import IntegrityError, OperationalError
from datetime import datetime
from sqlalchemy import select
from utils.mappers import budget_mapper

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
        return jsonify({"message": "Unauthorized"}), 404
    selected_date = datetime.strptime(request.form["date"], "%Y-%m")
    user = helpers.get_current_user(user_id)
    if user:
        # Database query
        stmt = (
            select(Budgets)
            .join(Users, Budgets.user_id == Users.user_id)
            .filter(Users.user_id == user.user_id)
            .filter(Budgets.budget_month == selected_date.month)
            .filter(Budgets.budget_year == selected_date.year)
        )
        try:
            result = db.session.execute(stmt).scalar_one_or_none()
            if not result:
                return jsonify({"message": "No budget for selected period"}), 404
            budget = budget_mapper(result)
            return jsonify(budget), 200
        except OperationalError:
            msg = {"message": "Connection error"}
            return jsonify(msg), 500
        except Exception as e:
            return jsonify({"message": f"Error {str(e)}"}), 500
    else:
        return jsonify({"message": "Not authorized"}), 404


@budget_bp.route("/get_all_budgets", methods=["GET"])
@jwt_required()
def get_all_budgets():
    user_id = helpers.get_user_id_from_token()
    if not user_id:
        return jsonify({"message": "Unauthorized"}), 404
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
        return jsonify({"message": "Unauthorized"}), 404
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
    """
    Gotta check if there is one for passed month and year, then validate against it and return an error that u need to edit/delete one
    :return:
    """
    user_id = helpers.get_user_id_from_token()
    if not user_id:
        return jsonify({"message": "Unauthorized"}), 404
    user = helpers.get_current_user(user_id)
