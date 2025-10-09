from flask import Blueprint, render_template, request, redirect, url_for
from flask_jwt_extended import jwt_required

main_bp = Blueprint("main", __name__)


@main_bp.route("/login", methods=["GET", "POST"])
def login_page():
    return render_template("login.html")


@main_bp.route("/register", methods=["GET"])
def register_page():
    return render_template("register.html")


@main_bp.route("/")
@jwt_required()
def dashboard():
    return render_template("dashboard.html")


@main_bp.route("/budgets")
@jwt_required()
def budget():
    return render_template("budgets.html")


@main_bp.route("/operations")
@jwt_required()
def operations():
    budget_id = request.args.get("budget_id")
    if not budget_id:
        return redirect(url_for("main.dashboard"))
    return render_template("operations.html")
