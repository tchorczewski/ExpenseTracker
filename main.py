from flask import render_template, jsonify
from db import db
from app import create_app
from db.models import Users, Expenses

app = create_app()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/get_users", methods=["GET"])
def get_users():
    users = Users.query.all()
    user_list = [
        {
            "user_id": user.user_id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.e_mail,
        }
        for user in users
    ]
    return jsonify(user_list), 200


@app.route("/get_expenses", methods=["GET"])
def get_expenses():
    expenses = Expenses.query.all()
    expenses_list = [
        {
            "id": expense.id,
            "category": expense.category,
            "amount": expense.amount,
            "description": expense.description,
            "date": expense.date.strftime("%Y-%m-%d"),
        }
        for expense in expenses
    ]
    return jsonify(expenses_list), 200


with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
