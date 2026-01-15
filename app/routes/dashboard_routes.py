from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from app.common.decorators import error_handler, jwt_required_user
from app.services.dashboard_services import (
    get_recent_operations,
    get_curr_month_transactions,
)

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard_bp.route("/get_last_transactions", methods=["GET"])
@error_handler
@jwt_required()
@jwt_required_user
def get_last_operations(user):
    result = get_recent_operations(user)
    if not result:
        return [], 201
    return result, 201


@dashboard_bp.route("/get_curr_expenses", methods=["GET"])
@error_handler
@jwt_required()
@jwt_required_user
def plot_expenses(user):
    data = get_curr_month_transactions(user.id)["expense"]
    return jsonify(data), 201


@dashboard_bp.route("/get_curr_incomes", methods=["GET"])
@error_handler
@jwt_required()
@jwt_required_user
def plot_incomes(user):
    data = get_curr_month_transactions(user.id)["income"]
    return jsonify(data), 201
