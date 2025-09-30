from flask import Blueprint, render_template
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


@main_bp.route("/budget")
@jwt_required()
def budget():
    return render_template("budget.html")


@main_bp.route("/history")
@jwt_required()
def history():
    return render_template("history.html")
