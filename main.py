from flask import render_template, jsonify, request, session
from db import db
from app import create_app
from db.models import Users, Expenses
import bcrypt

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


@app.route("/register", methods=["POST"])
def user_create():
    if request.method == "POST":
        password = request.form["password"]
        user = Users(
            username=request.form["username"],
            e_mail=request.form["e_mail"],
            first_name=request.form["first_name"],
            last_name=request.form["last_name"],
            user_password=bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()),
        )
        db.session.add(user)
        db.session.commit()
        return (
            jsonify(
                {
                    "user_id": user.user_id,
                    "username": user.username,
                    "e_mail": user.e_mail,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                }
            ),
            201,
        )


def get_pwd(username, password):
    user = Users.query.filter_by(username=username).first_or_404()
    return bcrypt.checkpw(
        password.encode("utf-8"),
        user.user_password,
    )


@app.route("/login", methods=["POST"])
def login_user():
    if request.method == "POST":
        username = request.form["login"]
        password = request.form["password"]
        if get_pwd(username, password):
            session["user"] = username
            session.permanent = True
            return {"message": "Login Successful"}, 200
        return {"message": "Invalid username or password"}, 401


@app.route("/logout")
def logout():
    session.pop("user", None)
    return {"message": "Logout successful"}, 200


@app.route("/users_expenses", methods=["GET"])
def get_users_expenses():
    if "user" in session:
        username = session["user"]
        user = Users.query.filter_by(username=username).first_or_404()
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
    return jsonify({"error": "Unauthorized"}), 401


with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
