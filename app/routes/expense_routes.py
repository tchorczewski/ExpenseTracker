from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from db.models import Users, Expenses
from db import db

expense_bp = Blueprint("expenses", __name__)


@expense_bp.route("/users_expenses", methods=["GET"])
@jwt_required()
def get_users_expenses():
    user_id = get_jwt_identity()
    user = Users.query.filter_by(user_id=user_id).first()
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
            .all()
        )
        expenses_list = [
            {
                "category": expense[0],
                "amount": expense[1],
                "description": expense[2],
                "date": expense[3].strftime("%Y-%m-%d"),
            }
            for expense in expenses
        ]
        return jsonify(expenses_list), 200
    else:
        return jsonify({"message": "User not found"}), 404
