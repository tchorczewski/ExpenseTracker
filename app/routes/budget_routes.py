from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.common.decorators import error_handler
from db import db
from db.models import (
    Budgets,
    Transactions,
    Categories,
    Statuses,
)
from utils import validation
from datetime import datetime
from sqlalchemy import select, update
from app.services.budget_services import get_budget_for_user, prepare_budget_data
from app.services.auth_services import get_auth_user
from utils.mappers import (
    budget_mapper,
    status_mapper,
    transaction_mapper,
)
from utils.validation import validate_budget

budget_bp = Blueprint("budget", __name__)


@budget_bp.route("/get_statuses", methods=["GET"])
@jwt_required()
@error_handler
def get_statuses():
    user, error_response, status_code = get_auth_user()
    if error_response:
        return error_response, status_code
    stmt = select(Statuses)
    results = db.session.execute(stmt).scalars().all()
    results_list = [status_mapper(row) for row in results]
    statuses = {"users": [], "budgets": []}
    for t in results_list:
        statuses[t["type"]].append(t)
    return jsonify(statuses), 200


@budget_bp.route("/get_all_budgets", methods=["GET"])
@error_handler
@jwt_required()
def get_all_budgets():
    user, error_response, status_code = get_auth_user()
    if error_response:
        return error_response, status_code
    stmt = (
        select(Budgets, Statuses.name)
        .outerjoin(Statuses, Budgets.status_id == Statuses.id)
        .filter(Budgets.user_id == user.id)
    )
    result = db.session.execute(stmt).all()
    if not result:
        return jsonify({"message": "User has no budgets"}), 404
    budgets_list = [budget_mapper(row.Budgets, row.name) for row in result]
    response = {"budgets": budgets_list}
    return jsonify(response), 200


@budget_bp.route("/<int:budget_id>/get_budget_details", methods=["GET"])
@error_handler
@jwt_required()
def get_budget_details(budget_id):
    user, error_response, status_code = get_auth_user()
    if error_response:
        return error_response, status_code
    transactions_stmt = (
        select(Transactions, Categories.name)
        .join(Categories, Transactions.category_id == Categories.id)
        .where(Transactions.budget_id == budget_id)
    )

    results = db.session.execute(transactions_stmt).all()
    transactions = {"income": [], "expense": []}
    for t, category in results:
        transactions[t.type].append(transaction_mapper(t, category))
    return jsonify(transactions), 200


@budget_bp.route("/create_budget", methods=["POST"])
@error_handler
@jwt_required()
def create_budget():
    user, error_response, status_code = get_auth_user()
    if error_response:
        return error_response, status_code
    raw_data = request.get_json()
    is_valid, error_msg = validate_budget(raw_data)
    if not is_valid:
        return jsonify({"message": f"Something went wrong {error_msg}"}), 400
    data = prepare_budget_data(raw_data, user.id)
    existing_budget, _, _ = get_budget_for_user(
        user.id,
        data["budget_month"],
        data["budget_year"],
    )
    if existing_budget:
        return jsonify({"message": "Budget already exists"}), 409

    budget = Budgets(**data)
    budget.is_generated = bool(budget.is_generated)

    db.session.add(budget)
    db.session.commit()
    response = jsonify(budget_mapper(budget))
    return response, 201


@budget_bp.route("/edit_budget", methods=["PATCH"])
@error_handler
@jwt_required()
def edit_budget():
    user, error_response, status_code = get_auth_user()
    if error_response:
        return error_response, status_code

    data = request.get_json()

    is_valid, error_msg = validation.validate_budget_edit(data)
    if not is_valid:
        return jsonify({"message": error_msg}), 400
    stmt = (
        update(Budgets)
        .where(Budgets.id == data["id"])
        .values(**data, updated_at=datetime.now())
        .returning(Budgets)
    )
    updated_budget = db.session.execute(stmt).scalar_one_or_none()
    db.session.commit()
    return budget_mapper(updated_budget), 200
