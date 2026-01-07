import pytest
from flask_jwt_extended import create_access_token

from app import create_app
from db import db as _db
import bcrypt


@pytest.fixture()
def app():
    app, _ = create_app()
    app.Testing = True
    ctx = app.app_context()
    ctx.push()
    yield app
    ctx.pop()


@pytest.fixture()
def db(app):
    _db.create_all()
    yield _db
    _db.drop_all()


@pytest.fixture(autouse=True)
def clean_db(app):
    yield _db.session.rollback()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def auth_headers():
    from db.models import Users

    password = "password123!"
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    user = _db.session.query(Users).filter_by(email="test@example.com").first()
    if not user:
        user = Users(
            id=1,
            username="testuser",
            email="test@example.com",
            password=password_hash,
            first_name="test",
            last_name="test",
            status_id=2,
            role_id=1,
        )
        _db.session.add(user)
        _db.session.commit()
    token = create_access_token(identity=user.id)
    return {"access_token_cookie": token}
