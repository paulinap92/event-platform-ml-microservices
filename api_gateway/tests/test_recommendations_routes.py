import importlib
import pytest
from flask import Flask


@pytest.fixture
def rec_module(monkeypatch):
    import app.security.configuration as sec

    def noop_authorize(*args, **kwargs):
        def decorator(fn):
            return fn
        return decorator

    monkeypatch.setattr(sec, "authorize", noop_authorize)

    import app.routes.recommendations as m
    m = importlib.reload(m)
    return m


@pytest.fixture
def app(rec_module):
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.register_blueprint(rec_module.recommendations_blueprint)
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def test_get_recommendations_route_calls_recommendations_get(monkeypatch, client, rec_module):
    expected = [{"event_id": 1, "score": 0.95}]

    @client.application.before_request
    def _inject_user():
        from flask import g
        g.user_id = 42

    def fake_get(user_id):
        assert user_id == 42
        return expected

    monkeypatch.setattr(rec_module, "recommendations_get", fake_get)

    resp = client.get("/api/recommendations")

    assert resp.status_code == 200
    assert resp.get_json() == expected


def test_add_recommendations_route_calls_recommendations_add(monkeypatch, client, rec_module):
    expected = {"status": "saved"}

    @client.application.before_request
    def _inject_user():
        from flask import g
        g.user_id = 99

    def fake_add(user_id, payload):
        assert user_id == 99
        assert payload == {"q1": 5, "q2": "yes"}
        return expected

    monkeypatch.setattr(rec_module, "recommendations_add", fake_add)

    resp = client.post("/api/recommendations", json={"q1": 5, "q2": "yes"})

    assert resp.status_code == 200
    assert resp.get_json() == expected
