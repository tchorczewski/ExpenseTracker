from datetime import datetime
import json


def test_create_transaction_valid(client, test_user, test_budget):
    # login
    res = client.post(
        "/api/auth/login", data={"login": "testuser", "password": "testpassword1!"}
    )
    assert res.status_code == 200

    test_res = client.post(
        "/api/transactions/add_transaction",
        content_type="application/json",
        data=json.dumps(
            {
                "category_id": 1,
                "amount": 154.39,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "is_cyclical": False,
                "budget_id": 1,
                "type": "expense",
            }
        ),
    )
    assert test_res.status_code == 201


def test_create_transaction_no_budget(client, test_user, test_budget):
    # login
    res = client.post(
        "/api/auth/login", data={"login": "testuser", "password": "testpassword1!"}
    )
    assert res.status_code == 200

    test_res = client.post(
        "/api/transactions/add_transaction",
        content_type="application/json",
        data=json.dumps(
            {
                "category_id": 1,
                "amount": 154.39,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "is_cyclical": False,
                "budget_id": 15,
                "type": "expense",
            }
        ),
    )
    assert test_res.status_code == 400


def test_create_transaction_invalid_amount(client, test_user, test_budget):
    # login
    res = client.post(
        "/api/auth/login", data={"login": "testuser", "password": "testpassword1!"}
    )
    assert res.status_code == 200
    test_res = client.post(
        "/api/transactions/add_transaction",
        content_type="application/json",
        data=json.dumps(
            {
                "category_id": 1,
                "amount": -0.0001,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "is_cyclical": False,
                "budget_id": 15,
                "type": "expense",
            }
        ),
    )
    assert test_res.status_code == 400


def test_create_transaction_incorrect_month(client, test_user, test_budget):
    res = client.post(
        "/api/auth/login", data={"login": "testuser", "password": "testpassword1!"}
    )
    assert res.status_code == 200

    test_res = client.post(
        "/api/transactions/add_transaction",
        content_type="application/json",
        data=json.dumps(
            {
                "category_id": 1,
                "amount": 154.39,
                "date": "2021-04-01",
                "is_cyclical": False,
                "budget_id": 15,
                "type": "expense",
            }
        ),
    )
    assert test_res.status_code == 400


def test_delete_transaction(client, test_user, test_budget, test_transaction):
    res = client.post(
        "/api/auth/login", data={"login": "testuser", "password": "testpassword1!"}
    )
    assert res.status_code == 200

    test_res = client.delete(
        "/api/transactions/delete_transaction",
        content_type="application/json",
        data=json.dumps({"id": test_transaction.id, "user_id": test_user.id}),
    )

    assert test_res.status_code == 200
