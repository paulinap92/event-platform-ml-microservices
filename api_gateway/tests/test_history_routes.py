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
    app.register_blueprint(rec_module.history_blueprint)
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def test_attend_event_route_calls_history_attend(monkeypatch, client, rec_module):
    expected = {"status": "ok"}

    @client.application.before_request
    def _inject_user():
        from flask import g
        g.user_id = 5

    def fake_attend(user_id, payload):
        assert user_id == 5
        assert payload == {"event_id": 123}
        return expected

    monkeypatch.setattr(rec_module, "history_attend", fake_attend)

    resp = client.post("/api/history/attend", json={"event_id": 123})

    assert resp.status_code == 200
    assert resp.get_json() == expected


def test_get_user_history_route_calls_history_get_user(monkeypatch, client, rec_module):
    expected = [{"event_id": 1}, {"event_id": 2}]

    @client.application.before_request
    def _inject_user():
        from flask import g
        g.user_id = 11

    def fake_get_user(user_id):
        assert user_id == 11
        return expected

    monkeypatch.setattr(rec_module, "history_get_user", fake_get_user)

    resp = client.get("/api/history/user")

    assert resp.status_code == 200
    assert resp.get_json() == expected


def test_get_all_history_route_calls_history_get_all(monkeypatch, client, rec_module):
    expected = [{"user_id": 1, "event_id": 10}]
    monkeypatch.setattr(rec_module, "history_get_all", lambda: expected)

    resp = client.get("/api/history/all")

    assert resp.status_code == 200
    assert resp.get_json() == expected


def test_get_history_recommendations_route_calls_history_get_recommendations(monkeypatch, client, rec_module):
    expected = [{"event_id": 99, "score": 0.8}]
    monkeypatch.setattr(rec_module, "history_get_recommendations", lambda: expected)

    resp = client.get("/api/history/recommend")

    assert resp.status_code == 200
    assert resp.get_json() == expected

def test_history_get_recommendations(monkeypatch):
    import app.routes.recommendations as module
    from flask import Flask, g

    expected = [{"event_id": 99, "score": 0.8}]

    # fake response obiektu httpx
    class DummyResponse:
        def json(self):
            return expected

    # fake httpx.get
    def fake_get(url, headers):
        assert url == f"{module.RECOMMENDATIONS_URL}history/recommend"
        assert headers == {"X-User-ID": "42"}
        return DummyResponse()

    monkeypatch.setattr(module.httpx, "get", fake_get)

    # potrzebujemy kontekstu Flask + g.user_id
    app = Flask(__name__)
    with app.app_context():
        g.user_id = 42

        result = module.history_get_recommendations()

    assert result == expected
