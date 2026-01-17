import json
from datetime import datetime


def test_create_budget(client, test_user, test_status):
    res = client.post(
        "/api/auth/login", data={"login": "testuser", "password": "testpassword1!"}
    )
    assert res.status_code == 200

    test_res = client.post(
        "/api/budgets/create_budget",
        content_type="application/json",
        data=json.dumps(
            {
                "user_id": test_user.id,
                "budget_month": 2,
                "budget_year": 2026,
                "status_id": test_status.id,
                "amount": 5500,
                "created_at": datetime.now().strftime("%Y-%m-%d"),
                "is_generated": False,
            }
        ),
    )
    assert test_res.status_code == 201


def test_create_duplicate_budget(client, test_user, test_status, test_budget):
    res = client.post(
        "/api/auth/login", data={"login": "testuser", "password": "testpassword1!"}
    )
    assert res.status_code == 200

    test_res = client.post(
        "/api/budgets/create_budget",
        content_type="application/json",
        data=json.dumps(
            {
                "user_id": test_user.id,
                "budget_month": 1,
                "budget_year": 2026,
                "status_id": test_status.id,
                "amount": 5500,
                "created_at": datetime.now().strftime("%Y-%m-%d"),
                "is_generated": False,
            }
        ),
    )
    assert test_res.status_code == 409


def test_incorrect_amount(client, test_user, test_status):
    res = client.post(
        "/api/auth/login", data={"login": "testuser", "password": "testpassword1!"}
    )
    assert res.status_code == 200

    test_res = client.post(
        "/api/budgets/create_budget",
        content_type="application/json",
        data=json.dumps(
            {
                "user_id": test_user.id,
                "budget_month": 1,
                "budget_year": 2026,
                "status_id": test_status.id,
                "amount": -5500,
                "created_at": datetime.now().strftime("%Y-%m-%d"),
                "is_generated": False,
            }
        ),
    )
    assert test_res.status_code == 400


def test_create_budget_invalid_user(client, test_user, test_status):
    res = client.post(
        "/api/auth/login", data={"login": "nouser", "password": "testpassword1!"}
    )
    assert res.status_code == 401


def test_create_budget_not_logged_in(client, test_user, test_status):
    test_res = client.post(
        "/api/budgets/create_budget",
        content_type="application/json",
        data=json.dumps(
            {
                "user_id": test_user.id,
                "budget_month": 2,
                "budget_year": 2026,
                "status_id": test_status.id,
                "amount": 5500,
                "created_at": datetime.now().strftime("%Y-%m-%d"),
                "is_generated": False,
            }
        ),
    )
    assert test_res.status_code == 401
