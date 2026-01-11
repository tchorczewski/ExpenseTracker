from datetime import datetime
import json

from db.models import Transactions


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
    print(test_res)
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


def test_edit_transaction(
    client, test_user, test_budget, test_transaction, database, app
):
    res = client.post(
        "/api/auth/login", data={"login": "testuser", "password": "testpassword1!"}
    )
    assert res.status_code == 200

    test_res = client.patch(
        "/api/transactions/edit_transaction",
        content_type="application/json",
        data=json.dumps(
            {
                "id": test_transaction.id,
                "category_id": test_transaction.category_id,
                "amount": 34.99,
                "type": "income",
                "date": test_transaction.date,
                "is_cyclical": test_transaction.is_cyclical,
            }
        ),
    )
    tx = database.session.get(Transactions, id=test_transaction.id)
    assert tx.status_code == 200
    assert tx.amount == test_res.data["amount"]
