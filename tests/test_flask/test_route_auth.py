import pytest
from unittest.mock import patch
from flask import json

#-------------------------
# TEST: /create_user
#-------------------------
@patch("app.routes.auth_routes.username_is_taken", return_value=False)
@patch("app.routes.auth_routes.create_user_service", return_value=None)
def test_create_user_success(mock_create, mock_taken, client):
    payload = {"username": "test_user", "password": "1234"}
    response = client.post("/create_user", json=payload)
    data = response.get_json()

    assert response.status_code == 200
    assert "Success" in data
    mock_create.assert_called_once()

def test_create_user_invalid_schema(client):
    response = client.post("/create_user", json={"username": ""})
    assert response.status_code == 400
    assert "Error" in response.get_json()

@patch("app.routes.auth_routes.username_is_taken", return_value=True)
def test_create_user_username_taken(mock_taken, client):
    payload = {"username": "existing_user", "password": "pass"}
    response = client.post("/create_user", json=payload)
    data = response.get_json()
    assert response.status_code == 409
    assert data["Error"] == "User already exists"


#-------------------------
# TEST: /login_user
#-------------------------
@patch("app.routes.auth_routes.login_user_service", return_value={"token": "abc"})
def test_login_user_success(mock_login, client):
    payload = {"username": "test", "password": "123"}
    response = client.post("/login_user", json=payload)
    data = response.get_json()

    assert response.status_code == 200
    assert "token" in data
    mock_login.assert_called_once()

@patch("app.routes.auth_routes.login_user_service", return_value=None)
def test_login_user_invalid_credentials(mock_login, client):
    payload = {"username": "wrong", "password": "wrong"}
    response = client.post("/login_user", json=payload)
    data = response.get_json()
    assert response.status_code == 401
    assert data["Error"] == "Credenziali non valide"

def test_login_user_validation_error(client):
    response = client.post("/login_user", json={"username": ""})
    assert response.status_code == 400
    assert "Error" in response.get_json()


#-------------------------
# TEST: /refresh_token
#-------------------------
@patch("app.routes.auth_routes.refresh_token_service", return_value={"access_token": "new-token"})
def test_refresh_token_success(mock_refresh, client, mock_jwt, auth_headers):
    response = client.post("/refresh_token", headers=auth_headers)
    data = response.get_json()

    assert response.status_code == 200
    assert "access_token" in data
    mock_refresh.assert_called_once()