from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError, OperationalError

budget_bp = Blueprint("budget", __name__)


@budget_bp.route("/set_budget", methods=["POST"])
@jwt_required()
def set_monthly_budget():
    current_user = get_jwt_identity()
