import pytest
from flask import Flask
from flask_restful import Api

import app.routes.resource as module  # <-- ZMIEŃ jeśli inna ścieżka


# ---------------------------------------------------------------------------
# APP / CLIENT
# ---------------------------------------------------------------------------

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["TESTING"] = True

    api = Api(app)
    api.add_resource(module.EventsResource, "/events")

    return app


@pytest.fixture
def client(app):
    return app.test_client()


# ---------------------------------------------------------------------------
# POST /events
# ---------------------------------------------------------------------------

def test_post_events_missing_user_id_header(client):
    """
    POST /events
    Missing X-User-ID header -> 401
    """
    resp = client.post(
        "/events",
        json={
            "title": "Test",
            "description": "Desc",
            "location": "Madrid",
            "date": "2026-01-01",
        },
    )

    assert resp.status_code == 401
    assert resp.get_json()["error"] == "Missing X-User-ID header"


def test_post_events_missing_required_field_returns_400(client):
    """
    POST /events
    Missing required field -> reqparse returns 400
    """
    resp = client.post(
        "/events",
        headers={"X-User-ID": "1"},
        json={
            "title": "Test",
            # description missing
            "location": "Madrid",
            "date": "2026-01-01",
        },
    )

    assert resp.status_code == 400


def test_post_events_calls_service_and_returns_201(monkeypatch, client):
    """
    POST /events
    Valid request -> calls events_service.add_event and returns 201
    """
    expected = {
        "id": 1,
        "title": "Test",
        "description": "Desc",
        "location": "Madrid",
        "date": "2026-01-01",
        "predicted_category": "music",
    }

    def fake_add_event(organizer_id, dto):
        assert organizer_id == 5
        assert dto.title == "Test"
        assert dto.description == "Desc"
        assert dto.location == "Madrid"
        assert dto.date == "2026-01-01"
        return expected

    monkeypatch.setattr(module.events_service, "add_event", fake_add_event)

    resp = client.post(
        "/events",
        headers={"X-User-ID": "5"},
        json={
            "title": "Test",
            "description": "Desc",
            "location": "Madrid",
            "date": "2026-01-01",
        },
    )

    assert resp.status_code == 201
    assert resp.get_json() == expected


# ---------------------------------------------------------------------------
# GET /events
# ---------------------------------------------------------------------------

def test_get_events_returns_events(monkeypatch, client):
    """
    GET /events
    Should return list of events from service
    """
    expected = [
        {"id": 1, "title": "A"},
        {"id": 2, "title": "B"},
    ]

    monkeypatch.setattr(module.events_service, "get_events", lambda: expected)

    resp = client.get("/events")

    assert resp.status_code == 200
    assert resp.get_json() == expected
