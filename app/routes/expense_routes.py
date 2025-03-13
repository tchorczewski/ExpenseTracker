from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy import select
from utils import validation, helpers
from db.models import Users, Expenses
from db import db
from utils.mappers import expense_mapper

expense_bp = Blueprint("expenses", __name__)


@expense_bp.route("/get_expenses", methods=["GET"])
@jwt_required()
def get_users_expenses():
    user_id = helpers.get_user_id_from_token()
    if not user_id:
        return jsonify({"message": "Unauthorized"}), 401
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    user = helpers.get_current_user(user_id)
    if user:
        stmt = (
            select(Expenses)
            .join(Users, Expenses.user_id == Users.user_id)
            .filter(Users.user_id == user.user_id)
            .limit(per_page)
            .offset((page - 1) * per_page)
        )
        expenses = db.session.execute(stmt).scalars().all()

        expenses_list = [expense_mapper(expense) for expense in expenses]
        response = {
            "expenses": expenses_list,
            # "page": expenses.page,
            # "per_page": expenses.per_page,
            # "total": expenses.total,
            # "pages": expenses.pages,
        }
        return jsonify(response), 200
    else:
        return jsonify({"message": "User not found"}), 404


@expense_bp.route("/add_expense", methods=["POST"])
@jwt_required()
def add_expense():
    if request.method == "POST":
        user = helpers.get_user_id_from_token()
        if not user:
            return jsonify({"message": "Unauthorized"}), 401
        raw_data = request.form.to_dict()
        data, error_msg = helpers.prepare_expense_data(raw_data, user)
        if error_msg:
            return jsonify({"message": f"Something went wrong {error_msg}"}), 400
        is_valid, error_msg = validation.validate_expense(data)
        if not is_valid:
            return jsonify({"message": error_msg}), 400
        expense = Expenses(**data)
        try:
            db.session.add(expense)
            db.session.commit()
            response = jsonify(expense_mapper(expense))
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


@expense_bp.route("/delete_expense/<int:expense_id>", methods=["DELETE"])
@jwt_required()
def delete_expense(expense_id):
    user_id = helpers.get_user_id_from_token()
    if not user_id:
        return jsonify({"message": "Unauthorized"}), 404
    if request.method == "DELETE":
        expense = Expenses.query.get(expense_id)

        if not expense:
            return jsonify({"message": "Expense not found"}), 404

        if expense.user_id != int(user_id):
            return (
                jsonify({"message": "Unauthorized"}),
                403,
            )

        try:
            db.session.delete(expense)
            db.session.commit()
            response = f"Expense {expense.id} successfully deleted."
            return jsonify(response), 200
        except IntegrityError:
            db.session.rollback()
            return jsonify({"message": "Database integrity error"}), 400
        except OperationalError:
            db.session.rollback()
            return jsonify({"message": "Database connection issue"}), 500
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500


@expense_bp.route("/edit_expense/<int:expense_id>", methods=["PUT"])
@jwt_required()
def edit_expense(expense_id):
    user_id = helpers.get_user_id_from_token()
    if not user_id:
        return jsonify({"message": "Unauthorized"}), 404
    if request.method == "PUT":
        expense = Expenses.query.get(expense_id)

        if not expense:
            return jsonify({"message": "Expense not found"}), 404
        if int(user_id) != expense.user_id:
            return (
                jsonify({"message": "Unauthorized"}),
                403,
            )
        data = request.get_json()
        allowed_fields = set(Expenses.__table__.columns.keys()) - {"id", "user_id"}

        for key, value in data.items():
            if key in allowed_fields:
                setattr(expense, key, float(value) if key == "amount" else value)

        try:
            db.session.commit()
            response = {
                "message": f"Expense {expense.id} successfully updated",
                "updated_expense": {
                    field: getattr(expense, field) for field in allowed_fields
                },
            }
            return jsonify(response), 200
        except IntegrityError:
            db.session.rollback()
            return jsonify({"message": "Database integrity error"}), 400
        except OperationalError:
            db.session.rollback()
            return jsonify({"message": "Database connection issue"}), 500
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500
