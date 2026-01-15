from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.common.decorators import error_handler, jwt_required_user
from db import db
from db.models import Budgets
from utils import validation
from app.services.budget_services import (
    prepare_budget_data,
    status_getter,
    budgets_getter,
    budget_details,
    check_existing_budget,
    push_edited_budget,
)
from app.services.auth_services import get_auth_user
from utils.mappers import budget_mapper
from utils.validation import validate_budget

budget_bp = Blueprint("budget", __name__)


@budget_bp.route("/get_statuses", methods=["GET"])
@jwt_required()
@jwt_required_user
@error_handler
def get_statuses():
    user, error_response, status_code = get_auth_user()
    if error_response:
        return error_response, status_code
    statuses = status_getter()
    return jsonify(statuses), 200


@budget_bp.route("/get_all_budgets", methods=["GET"])
@error_handler
@jwt_required()
@jwt_required_user
def get_all_budgets(user):
    budgets = budgets_getter(user)
    if not budgets:
        return jsonify({"message": "No budgets found"}), 404
    return jsonify({"budgets": budgets}), 200


@budget_bp.route("/<int:budget_id>/get_budget_details", methods=["GET"])
@error_handler
@jwt_required()
@jwt_required_user
def get_budget_details(user, budget_id):
    transactions = budget_details(budget_id)
    return jsonify(transactions), 200


@budget_bp.route("/create_budget", methods=["POST"])
@error_handler
@jwt_required()
@jwt_required_user
def create_budget(user):
    raw_data = request.get_json()
    is_valid, error_msg = validate_budget(raw_data)
    if not is_valid:
        return jsonify({"message": f"Something went wrong {error_msg}"}), 400
    data = prepare_budget_data(raw_data, user)
    existing_budget = check_existing_budget(
        user, data["budget_month"], data["budget_year"]
    )
    if existing_budget:
        return (
            jsonify(
                {
                    "message": f"Budget for {data['budget_month']}.{ data['budget_year']} already exists"
                }
            ),
            409,
        )

    budget = Budgets(**data)
    db.session.add(budget)
    db.session.commit()
    response = jsonify(budget_mapper(budget))
    return response, 201


@budget_bp.route("/edit_budget", methods=["PATCH"])
@error_handler
@jwt_required()
@jwt_required_user
def edit_budget(user):
    data = request.get_json()
    is_valid, error_msg = validation.validate_budget_edit(data)
    if not is_valid:
        return jsonify({"message": error_msg}), 400
    updated_budget = push_edited_budget(data)
    return budget_mapper(updated_budget), 200
