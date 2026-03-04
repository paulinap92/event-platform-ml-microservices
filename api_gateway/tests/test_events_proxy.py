import app.routes.events as events_module  # <- dopasuj ścieżkę do pliku


class DummyResponse:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


def test_events_get_calls_httpx_get(monkeypatch):
    expected = [{"id": 1, "title": "A"}]

    def fake_get(url):
        assert url == f"{events_module.EVENTS_URL}events"
        return DummyResponse(expected)

    monkeypatch.setattr(events_module.httpx, "get", fake_get)

    result = events_module.events_get()
    assert result == expected


def test_events_health_test_calls_httpx_get(monkeypatch):
    expected = {"status": "ok"}

    def fake_get(url):
        assert url == f"{events_module.EVENTS_URL}test"
        return DummyResponse(expected)

    monkeypatch.setattr(events_module.httpx, "get", fake_get)

    result = events_module.events_health_test()
    assert result == expected


def test_events_add_calls_httpx_post_with_header_and_json(monkeypatch):
    organizer_id = 123
    event_data = {
        "title": "Test",
        "description": "Desc",
        "location": "Madrid",
        "date": "2026-02-10",
    }
    expected = {"id": 10, "organizer_id": organizer_id, **event_data}

    def fake_post(url, json, headers):
        assert url == f"{events_module.EVENTS_URL}events"
        assert json == event_data
        assert headers == {"X-User-ID": str(organizer_id)}
        return DummyResponse(expected)

    monkeypatch.setattr(events_module.httpx, "post", fake_post)

    result = events_module.events_add(organizer_id, event_data)
    assert result == expected
