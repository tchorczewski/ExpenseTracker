from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from db.models import Budgets, Users
from utils import helpers
from sqlalchemy.exc import IntegrityError, OperationalError
from datetime import datetime
from sqlalchemy import select

budget_bp = Blueprint("budget", __name__)


@budget_bp.route("/get_budget", methods=["GET"])
@jwt_required()
def get_any_budget():
    """
    Get budget for current month
    :return: Budget amount if set, None if not set
    """
    user_id = get_jwt_identity()
    selected_date = datetime.strptime(request.form["date"], "%Y-%M")
    user = helpers.get_current_user(user_id)
    if user:
        stmt = (
            select(Budgets)
            .join(Users, Budgets.user_id == Users.user_id)
            .filter(Users.user_id == user.user_id)
            .filter(Budgets.budget_month == selected_date.month)
            .filter(Budgets.budget_year == selected_date.year)
        )
        pass
    pass


@budget_bp.route("/create_budget", methods=["POST"])
@jwt_required()
def create_budget():
    """
    Gotta check if there is one for passed month and year, then validate against it and return an error that u need to edit/delete one
    :return:
    """
    current_user = get_jwt_identity()
