def test_login_successful(client, test_user):
    response = client.post(
        "/api/auth/login", data={"login": "testuser", "password": "testpassword1!"}
    )
    assert response.status_code == 200


def test_login_wrong_password(client):
    response = client.post(
        "/api/auth/login", data={"login": "jason1234", "password": "failedpassword"}
    )
    assert response.status_code == 401


def test_login_unregistered_user(client):
    response = client.post(
        "/api/auth/login", data={"login": "faileduser", "password": "failedpassword"}
    )
    assert response.status_code == 401


def test_register_correct(client):
    response = client.post(
        "/api/auth/register",
        data={
            "username": "example_user",
            "email": "test_user@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "examplepassword1234!",
        },
    )
    assert response.status_code == 201


def test_register_wrong_mail(client):
    response = client.post(
        "/api/auth/register",
        data={
            "username": "test_user",
            "email": "test.user",
            "first_name": "Test",
            "last_name": "User",
            "password": "examplepassword1234",
        },
    )
    assert response.status_code == 400


def test_register_weak_password(client):
    response = client.post(
        "api/auth/register",
        data={
            "username": "wrong_password",
            "email": "wrong_password@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "pass",
        },
    )
    assert response.status_code == 400
