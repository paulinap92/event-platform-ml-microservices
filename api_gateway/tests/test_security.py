import pytest
from unittest.mock import patch
from datetime import datetime, timedelta, UTC
import jwt
from jwt.exceptions import ExpiredSignatureError

MODULE = "app.security.configuration"  # <- tu jest Twój kod security


@pytest.fixture
def security_app(app):
    """Aktywuje security routes w aplikacji."""
    from app.security.configuration import configure_security
    configure_security()
    return app.test_client()


@pytest.fixture(autouse=True)
def jwt_config(app):
    app.config['JWT_SECRET'] = 'TEST_SECRET'
    app.config['JWT_AUTHTYPE'] = 'HS256'
    app.config['JWT_PREFIX'] = 'Bearer'
    app.config['JWT_ACCESS_MAX_AGE'] = 1
    app.config['JWT_REFRESH_MAX_AGE'] = 2


def test_login_user_not_found(security_app):
    response = security_app.post('/login', json={'username': 'x', 'password': 'y'})
    assert response.status_code == 400
    assert "user not found" in response.get_json()["message"].lower()


def test_login_user_not_active(security_app, user_factory):
    user_factory(username="alice", password="xyz", email="a@a.com", role="USER", is_active=False)

    response = security_app.post('/login', json={'username': 'alice', 'password': 'xyz'})
    assert response.status_code == 500
    assert "not active" in response.get_json()["message"].lower()


def test_login_wrong_password(security_app, user_factory):
    user_factory(username="bob", password="HASH", email="b@b.com", role="USER", is_active=True)

    with patch("app.db.entity.UserEntity.check_password", return_value=False):
        response = security_app.post('/login', json={'username': 'bob', 'password': 'wrong'})
        assert response.status_code == 400
        assert "password is not correct" in response.get_json()["message"].lower()


def test_login_success(security_app, user_factory):
    user_factory(username="john", password="HASH", email="j@j.com", role="ADMIN", is_active=True)

    with patch("app.db.entity.UserEntity.check_password", return_value=True):
        response = security_app.post('/login', json={'username': 'john', 'password': 'HASH'})

        assert response.status_code == 201

        body = response.get_json()
        assert 'access_token' in body
        assert 'refresh_token' in body
        assert response.headers.get('Access-Token') is not None
        assert response.headers.get('Refresh-Token') is not None




from datetime import datetime, timedelta, UTC
import jwt

def test_refresh_success(security_app, user_factory):
    user = user_factory(username="aaa", email="a@a.com", password="HASH", role="ADMIN", is_active=True)

    refresh_payload = {
        'iat': datetime.now(UTC),
        'exp': int((datetime.now(UTC) + timedelta(minutes=2)).timestamp()),  # REFRESH STILL VALID
        'sub': str(user.id),
        'role': "ADMIN",
        'access_token_exp': int((datetime.now(UTC) + timedelta(minutes=-1)).timestamp())  # ACCESS EXPIRED
    }

    refresh_token = jwt.encode(refresh_payload, 'TEST_SECRET', algorithm="HS256")

    response = security_app.post('/refresh', json={'token': refresh_token})

    assert response.status_code == 201
    body = response.get_json()
    assert "access_token" in body
    assert "refresh_token" in body


def test_refresh_expired_fail(security_app, user_factory):
    user = user_factory()

    expired_payload = {
        'iat': datetime.now(UTC),
        'exp': int((datetime.now(UTC) - timedelta(minutes=1)).timestamp()),  # REFRESH TOKEN EXPIRED
        'sub': str(user.id),
        'role': "USER",
        'access_token_exp': int((datetime.now(UTC) - timedelta(minutes=5)).timestamp())
    }

    token = jwt.encode(expired_payload, 'TEST_SECRET', algorithm="HS256")

    with pytest.raises(ExpiredSignatureError):
        security_app.post('/refresh', json={'token': token})

def test_authorize_no_header(app):
    from app.security.configuration import authorize

    @app.route("/secure")
    @authorize()
    def secure():
        return {"ok": True}, 200

    client = app.test_client()
    res = client.get("/secure")
    assert res.status_code == 401
    assert "no header" in res.get_json()["message"].lower()


def test_authorize_invalid_prefix(app):
    from app.security.configuration import authorize

    @app.route("/secure2")
    @authorize()
    def secure2():
        return {"ok": True}, 200

    client = app.test_client()
    res = client.get("/secure2", headers={"Authorization": "WRONG token"})
    assert res.status_code == 401


def test_authorize_role_denied(app):
    from app.security.configuration import authorize

    payload = {'sub': '1', 'role': 'USER', 'exp': int((datetime.now(UTC) + timedelta(minutes=5)).timestamp())}
    token = jwt.encode(payload, "TEST_SECRET", algorithm="HS256")

    @app.route("/admin")
    @authorize(roles=["ADMIN"])
    def admin():
        return {"ok": True}, 200

    client = app.test_client()
    res = client.get("/admin", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 403


def test_authorize_success(app):
    from app.security.configuration import authorize

    payload = {'sub': '1', 'role': 'ADMIN', 'exp': int((datetime.now(UTC) + timedelta(minutes=5)).timestamp())}
    token = jwt.encode(payload, "TEST_SECRET", algorithm="HS256")

    @app.route("/admin2")
    @authorize(roles=["ADMIN"])
    def admin2():
        return {"ok": True}, 200

    client = app.test_client()
    res = client.get("/admin2", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.get_json()["ok"] is True


import jwt
from datetime import datetime, timedelta, UTC

def test_authorize_invalid_token_hits_except(app):
    """
    Wejście w except: jwt.decode rzuca błąd (np. token nie jest JWT).
    Oczekujemy 401 i message == 'Authorization failed'.
    """
    from app.security.configuration import authorize

    @app.route("/secure_except_invalid_token")
    @authorize()
    def secure_except_invalid_token():
        return {"ok": True}, 200

    client = app.test_client()
    res = client.get(
        "/secure_except_invalid_token",
        headers={"Authorization": "Bearer not-a-jwt-token"},
    )

    assert res.status_code == 401
    assert "authorization failed" in res.get_json()["message"].lower()


def test_authorize_missing_token_part_hits_except(app):
    """
    Wejście w except: header zaczyna się od prefixu, ale nie ma tokena po spacji,
    więc header.split(' ')[1] rzuci IndexError.
    """
    from app.security.configuration import authorize

    @app.route("/secure_except_missing_part")
    @authorize()
    def secure_except_missing_part():
        return {"ok": True}, 200

    client = app.test_client()
    # UWAGA: to przechodzi przez startswith('Bearer'), ale potem split()[1] wybucha
    res = client.get(
        "/secure_except_missing_part",
        headers={"Authorization": "Bearer"},
    )

    assert res.status_code == 401
    assert "authorization failed" in res.get_json()["message"].lower()
