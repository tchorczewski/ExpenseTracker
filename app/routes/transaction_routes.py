import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy import select, update, delete
from datetime import datetime
from app.common.decorators import error_handler
from app.services.transactions_services import prepare_transaction_data
from utils import validation
from db.models import Users, Transactions, Categories
from db import db
from app.services.auth_services import get_auth_user

from utils.mappers import category_mapper, transaction_mapper

transaction_bp = Blueprint("expenses", __name__)


@transaction_bp.route("/get_transactions", methods=["GET"])
@error_handler
@jwt_required()
def get_users_transactions():
    user, error_response, status_code = get_auth_user()
    if error_response:
        return error_response, status_code

    stmt = select(Transactions).where(Users.user_id == user.user_id)
    transactions = db.session.execute(stmt).scalars().all()

    transactions_list = [
        transaction_mapper(transaction) for transaction in transactions
    ]
    response = {"expenses": transactions_list}
    return jsonify(response), 200


@transaction_bp.route("/add_transaction", methods=["POST"])
@error_handler
@jwt_required()
def create_transaction():
    user, error_response, status_code = get_auth_user()
    if error_response:
        return error_response, status_code

    raw_data = request.get_json()

    is_valid, error_msg = validation.validate_transaction(raw_data)
    if not is_valid:
        return jsonify({"message": error_msg}), 400

    data, error_msg = prepare_transaction_data(raw_data, user.id)
    if error_msg:
        return jsonify({"message": f"Something went wrong {error_msg}"}), 400

    print(data)
    transaction = Transactions(**data)
    db.session.add(transaction)
    db.session.commit()
    response = jsonify(transaction_mapper(transaction))
    return response, 201


@transaction_bp.route("/delete_transaction", methods=["DELETE"])
@error_handler
@jwt_required()
def delete_transaction():
    user, error_msg, status_code = get_auth_user()
    if error_msg:
        return error_msg, status_code
    data = request.get_json()

    stmt = delete(Transactions).where(
        Transactions.id == data["id"], Transactions.user_id == user.id
    )
    db.session.execute(stmt)
    db.session.commit()
    return {"message": "Ok"}, 200


@transaction_bp.route("/edit_transaction", methods=["PATCH"])
@error_handler
@jwt_required()
def edit_transaction():
    user, error_response, status_code = get_auth_user()
    if error_response:
        return error_response, status_code

    data = request.get_json()

    is_valid, error_msg = validation.validate_operation_edit(data)
    if not is_valid:
        return jsonify({"message": error_msg}), 400
    stmt = (
        update(Transactions)
        .where(Transactions.id == data["id"], Transactions.user_id == user.user_id)
        .values(**data, updated_at=datetime.now())
        .returning(Transactions)
    )
    updated_transaction = db.session.execute(stmt).scalar_one_or_none()
    db.session.commit()

    return transaction_mapper(updated_transaction), 200


@transaction_bp.route("/get_categories", methods=["GET"])
@jwt_required()
@error_handler
def get_categories():
    user, error_response, status_code = get_auth_user()
    if error_response:
        return error_response, status_code
    stmt = select(Categories)
    results = db.session.execute(stmt).scalars().all()
    categories = {"income": [], "expense": []}
    results_list = [category_mapper(row) for row in results]
    for c in results_list:
        categories[c["type"]].append({"id": c["id"], "name": c["name"]})
    return jsonify(categories), 200
