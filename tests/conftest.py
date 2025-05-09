import pytest
from app import create_app
from db import db


@pytest.fixture()
def app():
    app = create_app()

    with app.app_context():
        db.create_all()

    yield app


@pytest.fixture()
def client(app):
    return app.test_client()
