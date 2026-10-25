CREDS = {"email": "user@gmail.com", "password": "password123"}


def register(client):
    return client.post("/auth/register", json=CREDS)


def login(client, password="password123"):
    return client.post(
        "/auth/login", data={"username": CREDS["email"], "password": password}
    )


def test_register_login_me(client):
    assert register(client).status_code == 201
    response = login(client)
    assert response.status_code == 200
    token = response.json()["access_token"]
    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == CREDS["email"]


def test_duplicate_email(client):
    register(client)
    assert register(client).status_code == 409


def test_wrong_password(client):
    register(client)
    assert login(client, "wrong-password").status_code == 401


def test_me_without_token(client):
    assert client.get("/auth/me").status_code == 401