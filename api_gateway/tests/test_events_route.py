import importlib
import pytest
from flask import Flask


@pytest.fixture
def events_module(monkeypatch):
    # PATCHUJEMY tam, skąd route bierze authorize:
    import app.security.configuration as sec

    def noop_authorize(*args, **kwargs):
        def decorator(fn):
            return fn
        return decorator

    monkeypatch.setattr(sec, "authorize", noop_authorize)

    # reload modułu, żeby dekoratory nałożyły się jeszcze raz (już z noop authorize)
    import app.routes.events as m  # <- dopasuj ścieżkę jeśli inna
    m = importlib.reload(m)
    return m


@pytest.fixture
def app(events_module):
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.register_blueprint(events_module.events_blueprint)
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def test_get_events_route_calls_events_get(monkeypatch, client, events_module):
    expected = [{"id": 1, "title": "A"}]
    monkeypatch.setattr(events_module, "events_get", lambda: expected)

    resp = client.get("/api/events/")

    assert resp.status_code == 200
    assert resp.get_json() == expected


def test_add_event_route_uses_g_user_id_and_request_json(monkeypatch, client, events_module):
    expected = {"id": 10, "title": "X"}

    @client.application.before_request
    def _inject_user():
        from flask import g
        g.user_id = 555

    def fake_events_add(organizer_id, event_data):
        assert organizer_id == 555
        assert event_data == {"title": "X"}
        return expected

    monkeypatch.setattr(events_module, "events_add", fake_events_add)

    resp = client.post("/api/events/", json={"title": "X"})

    assert resp.status_code == 200
    assert resp.get_json() == expected
