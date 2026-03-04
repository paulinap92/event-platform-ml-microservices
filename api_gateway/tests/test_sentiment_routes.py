import importlib
import pytest
from flask import Flask


@pytest.fixture
def sentiment_module(monkeypatch):
    # 1) no-op authorize w ORYGINALNYM miejscu (tam skąd decorator jest brany)
    import app.security.configuration as sec

    def noop_authorize(*args, **kwargs):
        def decorator(fn):
            return fn
        return decorator

    monkeypatch.setattr(sec, "authorize", noop_authorize)

    # 2) reload modułu z blueprintem, żeby dekoratory nałożyły się na nowo
    import app.routes.sentiments as m
    m = importlib.reload(m)
    return m


@pytest.fixture
def app(sentiment_module):
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.register_blueprint(sentiment_module.sentiment_blueprint)
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def test_get_sentiment_route_calls_sentiment_get(monkeypatch, client, sentiment_module):
    expected = [{"label": "positive", "score": 0.9}]
    monkeypatch.setattr(sentiment_module, "sentiment_get", lambda: expected)

    resp = client.get("/api/sentiment/")

    assert resp.status_code == 200
    assert resp.get_json() == expected


def test_add_sentiment_route_uses_g_user_id_and_request_json(monkeypatch, client, sentiment_module):
    expected = {"label": "neutral", "score": 0.5}

    @client.application.before_request
    def _inject_user():
        from flask import g
        g.user_id = 777

    def fake_sentiment_add(user_id, payload):
        assert user_id == 777
        assert payload == {"text": "hello"}
        return expected

    monkeypatch.setattr(sentiment_module, "sentiment_add", fake_sentiment_add)

    resp = client.post("/api/sentiment/", json={"text": "hello"})

    assert resp.status_code == 200
    assert resp.get_json() == expected
