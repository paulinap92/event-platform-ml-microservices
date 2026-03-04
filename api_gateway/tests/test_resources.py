from unittest.mock import patch
import pytest

MODULE = "app.service.configuration.user_service"  # JEDNO MIEJSCE Z PRAWDĄ O ŚCIEŻCE


def test_register_user_success(client):
    payload = {
        "username": "john",
        "email": "john@example.com",
        "password": "secret",
        "password_confirmation": "secret",
        "role": "USER"
    }

    # Patchujemy metodę na instancji user_service widzianej przez Resource
    with patch(f"{MODULE}.register_user") as mock_service:
        mock_service.return_value = ({"id": 1, "username": "john"}, 201)

        response = client.post("/users/register", json=payload)

        assert response.status_code == 201
        data = response.get_json()
        assert data["username"] == "john"
        mock_service.assert_called_once()


def test_register_user_missing_field(client):
    payload = {
        "username": "john",
        "email": "john@example.com",
        "password": "secret",
        # brak password_confirmation
        "role": "USER"
    }

    response = client.post("/users/register", json=payload)

    assert response.status_code == 400
    json_body = response.get_json()
    assert json_body["message"]["password_confirmation"] == "Password confirmation cannot be empty"


def test_activation_user_success(client):
    with patch(f"{MODULE}.activate_user") as mock_service:
        mock_service.return_value = ({"activated": True}, 200)

        response = client.post("/users/activate", json={"token": "ABC"})
        assert response.status_code == 200
        assert response.get_json()["activated"] is True
        mock_service.assert_called_once_with("ABC")


def test_activation_user_missing_token(client):
    response = client.post("/users/activate", json={})
    assert response.status_code == 400
    assert "Token cannot be empty" in response.get_json()["message"]['token']