from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError, OperationalError
from utils import validation
from db.models import Users, Expenses
from db import db

expense_bp = Blueprint("expenses", __name__)


@expense_bp.route("/users_expenses", methods=["GET"])
@jwt_required()
def get_users_expenses():
    user_id = get_jwt_identity()
    user = Users.query.filter_by(user_id=user_id).first()
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    if user:
        expenses = (
            db.session.query(
                Expenses.category,
                Expenses.amount,
                Expenses.description,
                Expenses.date,
            )
            .join(Users, Expenses.user_id == Users.user_id)
            .filter(Users.user_id == user.user_id)
            .paginate(page=page, per_page=per_page, error_out=False)
        )
        expenses_list = [
            {
                "category": expense[0],
                "amount": expense[1],
                "description": expense[2],
                "date": expense[3].strftime("%Y-%m-%d"),
            }
            for expense in expenses.items
        ]
        response = {
            "expenses": expenses_list,
            "page": expenses.page,
            "per_page": expenses.per_page,
            "total": expenses.total,
            "pages": expenses.pages,
        }
        return jsonify(response), 200
    else:
        return jsonify({"message": "User not found"}), 404


@expense_bp.route("/add_expense", methods=["POST"])
@jwt_required()
def add_expense():
    if request.method == "POST":
        data = request.form.to_dict()
        data["amount"] = float(data.get("amount", "0"))
        data["description"] = data.get("description", "None")
        data["user_id"] = get_jwt_identity()

        is_valid, error_msg = validation.validate_expense(data)
        if not is_valid:
            return jsonify({"message": error_msg}), 400

        expense = Expenses(**data)

        try:
            db.session.add(expense)
            db.session.commit()
            response = jsonify(
                {
                    "category": expense.category,
                    "amount": expense.amount,
                    "description": expense.description,
                    "date": expense.date,
                    "user_id": expense.user_id,
                }
            )
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
    current_user = get_jwt_identity()
    if request.method == "DELETE":
        expense = Expenses.query.get(expense_id)

        if not expense:
            return jsonify({"message": "Expense not found"}), 404

        if expense.user_id != int(current_user):
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
    current_user = get_jwt_identity()
    if request.method == "PUT":
        expense = Expenses.query.get(expense_id)

        if not expense:
            return jsonify({"message": "Expense not found"}), 404
        if int(current_user) != expense.user_id:
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
