def test_registration_login_and_private_lists(client):
    credentials = {"username": "smoke_user", "email": "smoke@example.invalid", "password": "Test-only-password-123!"}
    response = client.post("/api/auth/register", json=credentials)
    assert response.status_code == 201
    assert client.post("/api/auth/register", json=credentials).status_code == 400
    assert client.post("/api/auth/login", json={**credentials, "password": "wrong"}).status_code == 401
    response = client.post("/api/auth/login", json=credentials)
    assert response.status_code == 200
    headers = {"Authorization": "Bearer " + response.json["access_token"]}
    assert client.get("/api/auth/me", headers=headers).json["user"]["username"] == credentials["username"]
    for path in ("/api/conversations", "/api/documents", "/api/templates"):
        assert client.get(path, headers=headers).status_code == 200
        assert client.get(path).status_code == 401

def test_invalid_registration(client):
    assert client.post("/api/auth/register", json={}).status_code == 400
