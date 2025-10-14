from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.common.decorators import error_handler
from db import db
from db.models import (
    Budgets,
    BudgetStatuses,
    Expenses,
    Incomes,
    ExpenseCategories,
    IncomeCategories,
)
from utils import validation
from datetime import datetime
from sqlalchemy import select, update
from app.services.budget_services import get_budget_for_user, prepare_budget_data
from app.services.auth_services import get_auth_user
from utils.mappers import budget_mapper, expense_mapper, income_mapper, status_mapper
from utils.validation import validate_budget

budget_bp = Blueprint("budget", __name__)


@budget_bp.route("/get_budget", methods=["GET"])
@jwt_required()
@error_handler
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


@budget_bp.route("/get_statuses", methods=["GET"])
@jwt_required()
@error_handler
def get_statuses():
    user, error_response, status_code = get_auth_user()
    if error_response:
        return error_response, status_code
    stmt = select(BudgetStatuses)
    results = db.session.execute(stmt).scalars().all()
    results_list = [status_mapper(row) for row in results]
    return jsonify(results_list), 200


@budget_bp.route("/get_all_budgets", methods=["GET"])
@error_handler
@jwt_required()
def get_all_budgets():
    user, error_response, status_code = get_auth_user()
    if error_response:
        return error_response, status_code
    stmt = (
        select(Budgets, BudgetStatuses.status_name)
        .outerjoin(BudgetStatuses, Budgets.status_id == BudgetStatuses.status_id)
        .filter(Budgets.user_id == user.user_id)
    )
    result = db.session.execute(stmt).all()
    if not result:
        return jsonify({"message": "User has no budgets"}), 404
    budgets_list = [budget_mapper(row.Budgets, row.status_name) for row in result]
    response = {"budgets": budgets_list}
    return jsonify(response), 200


@budget_bp.route("/<int:budget_id>/get_budget_details", methods=["GET"])
@error_handler
@jwt_required()
def get_budget_details(budget_id):
    user, error_response, status_code = get_auth_user()
    if error_response:
        return error_response, status_code
    expense_stmt = (
        select(Expenses, ExpenseCategories.category_name)
        .where(Expenses.budget_id == budget_id, Expenses.user_id == user.user_id)
        .join(
            ExpenseCategories,
            ExpenseCategories.category_id == Expenses.category_id,
        )
    )
    incomes_stmt = (
        select(Incomes, IncomeCategories.category_name)
        .where(Incomes.budget_id == budget_id, Incomes.user_id == user.user_id)
        .join(
            IncomeCategories,
            IncomeCategories.category_id == Incomes.category_id,
        )
    )

    expenses = db.session.execute(expense_stmt).all()
    incomes = db.session.execute(incomes_stmt).all()
    expenses_list = [
        expense_mapper(row.Expenses, row.category_name) for row in expenses
    ]
    incomes_list = [income_mapper(row.Incomes, row.category_name) for row in incomes]
    return jsonify({"expenses": expenses_list, "incomes": incomes_list}), 200


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
    data = prepare_budget_data(raw_data, user.user_id)
    existing_budget, _, _ = get_budget_for_user(
        user.user_id,
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


@budget_bp.route("/<int:budget_id>/edit_budget", methods=["PATCH"])
@error_handler
@jwt_required()
def edit_budget(budget_id):
    user, error_response, status_code = get_auth_user()
    if error_response:
        return error_response, status_code

    data = request.get_json()

    is_valid, error_msg = validation.validate_budget_edit(data)
    if not is_valid:
        return jsonify({"message": error_msg}), 400

    # Check if budget exists
    existing_budget, _, _ = get_budget_for_user(
        user.user_id,
        data["budget_month"],
        data["budget_year"],
    )
    if existing_budget:
        return jsonify({"message": "Budget already exists"}), 409

    stmt = (
        update(Budgets)
        .where(Budgets.budget_id == budget_id, Budgets.user_id == user.user_id)
        .values(**data, updated_at=datetime.now())
        .returning(Budgets)
    )
    updated_budget = db.session.execute(stmt).scalar_one_or_none()
    db.session.commit()
    return budget_mapper(updated_budget), 200
