from datetime import datetime, timezone

import pytest
from app import create_app
from app.test_config import TestConfig
from db import db as _db
import bcrypt


@pytest.fixture()
def app():
    app, _ = create_app(TestConfig)
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def db(app):
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()


@pytest.fixture(scope="function")
def test_user(app, db):
    from db.models import Users

    password = "testpassword1!"
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
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
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture(scope="function")
def test_budget(app, db, test_user, test_status):
    from db.models import Budgets

    budget = Budgets(
        id=1,
        user_id=test_user.id,
        budget_month=1,
        budget_year=2026,
        amount=5500.00,
        created_at=datetime.now(timezone.utc),
        status_id=test_status.id,
        is_generated=False,
    )
    db.session.add(budget)
    db.session.commit()
    return budget


@pytest.fixture(scope="function")
def test_status(app, db):
    from db.models import Statuses

    status = Statuses(id=1, name="test", type="budgets")
    db.session.add(status)
    db.session.commit()
    return status


@pytest.fixture(scope="function")
def test_category(app, db):
    from db.models import Categories

    category = Categories(id=1, name="test", type="expense")
    db.session.add(category)
    db.session.commit()
    return category


@pytest.fixture(scope="function")
def test_transaction(app, db, test_user, test_budget, test_category):
    from db.models import Transactions

    transaction = Transactions(
        id=2,
        category_id=test_category.id,
        amount=785.78,
        date=datetime.now().strftime("%Y-%m-%d"),
        is_cyclical=False,
        budget_id=test_budget.id,
        type="expense",
        user_id=test_user.id,
    )
    return transaction


@pytest.fixture(scope="function")
def database(app):
    with app.app_context():
        yield _db
        _db.session.rollback()
