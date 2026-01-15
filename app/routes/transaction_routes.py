import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy import delete
from datetime import datetime
from app.common.decorators import error_handler, jwt_required_user
from app.services.transactions_services import (
    prepare_transaction_data,
    fetch_categories,
    push_edited_transaction,
)
from utils import validation
from db.models import Transactions
from db import db

from utils.mappers import transaction_mapper

transaction_bp = Blueprint("expenses", __name__)


def trasaction_getter(user):
    pass


@transaction_bp.route("/get_transactions", methods=["GET"])
@error_handler
@jwt_required()
@jwt_required_user
def get_users_transactions(user):
    types = trasaction_getter(user)
    return jsonify(types), 200


@transaction_bp.route("/add_transaction", methods=["POST"])
@error_handler
@jwt_required()
@jwt_required_user
def create_transaction(user):
    raw_data = request.get_json()
    is_valid, error_msg = validation.validate_transaction(raw_data)
    if not is_valid:
        return jsonify({"message": error_msg}), 400

    data, error_msg = prepare_transaction_data(raw_data, user.id)
    if error_msg:
        return jsonify({"message": f"Something went wrong {error_msg}"}), 400

    transaction = Transactions(**data)
    db.session.add(transaction)
    db.session.commit()
    response = jsonify(transaction_mapper(transaction))
    return response, 201


@transaction_bp.route("/delete_transaction", methods=["DELETE"])
@error_handler
@jwt_required()
@jwt_required_user
def delete_transaction(user):
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
@jwt_required_user
def edit_transaction(user):
    data = request.get_json()
    is_valid, error_msg = validation.validate_transaction_edit(data)
    if not is_valid:
        return jsonify({"message": error_msg}), 400

    data["date"] = datetime.fromisoformat(data["date"])

    updated_transaction = push_edited_transaction(data, user)

    return transaction_mapper(updated_transaction), 200


@transaction_bp.route("/get_categories", methods=["GET"])
@jwt_required()
@error_handler
@jwt_required_user
def get_categories(user):
    categories = fetch_categories()
    return jsonify(categories), 200
