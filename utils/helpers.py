from flask_jwt_extended import get_jwt_identity
from db.models import Users


def get_current_user():
    user_id = get_jwt_identity()
    user = Users.query.filter_by(user_id=user_id).first()
    return user
