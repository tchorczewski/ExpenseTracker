from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app.common.decorators import error_handler
from app.services.auth_services import get_auth_user
from app.services.dashboard_services import (
    get_recent_operations,
    get_curr_month_expenses,
    get_curr_month_incomes,
)

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard_bp.route("/get_last_operations", methods=["GET"])
@error_handler
@jwt_required()
def get_last_operations():
    user, error_response, status_code = get_auth_user()
    if error_response:
        return error_response, status_code

    result = get_recent_operations(user)

    if not result:
        return [], 201

    return result, 201


@dashboard_bp.route("/get_curr_expenses", methods=["GET"])
@error_handler
@jwt_required()
def plot_expenses():
    user, error_response, status_code = get_auth_user()
    if error_response:
        return error_response, status_code
    data = get_curr_month_expenses()
    return jsonify(data), 201


@dashboard_bp.route("/get_curr_incomes", methods=["GET"])
@error_handler
@jwt_required()
def plot_incomes():
    user, error_response, status_code = get_auth_user()
    if error_response:
        return error_response, status_code
    data = get_curr_month_incomes()
    return jsonify(data), 201
