import app.routes.recommendations as module


class DummyResponse:
    def __init__(self, payload):
        self.payload = payload

    def json(self):
        return self.payload


def test_recommendations_health(monkeypatch):
    expected = {"status": "ok"}

    def fake_get(url):
        assert url == f"{module.RECOMMENDATIONS_URL}test"
        return DummyResponse(expected)

    monkeypatch.setattr(module.httpx, "get", fake_get)

    assert module.recommendations_health_test() == expected


def test_recommendations_add(monkeypatch):
    expected = {"result": "saved"}
    payload = {"q1": 5}

    def fake_post(url, json, headers):
        assert url == f"{module.RECOMMENDATIONS_URL}recommendations"
        assert json == payload
        assert headers == {"X-User-ID": "10"}
        return DummyResponse(expected)

    monkeypatch.setattr(module.httpx, "post", fake_post)

    assert module.recommendations_add(10, payload) == expected


def test_recommendations_get(monkeypatch):
    expected = [{"event_id": 1}]

    def fake_get(url, headers):
        assert url == f"{module.RECOMMENDATIONS_URL}recommendations"
        assert headers == {"X-User-ID": "5"}
        return DummyResponse(expected)

    monkeypatch.setattr(module.httpx, "get", fake_get)

    assert module.recommendations_get(5) == expected


def test_history_attend(monkeypatch):
    payload = {"event_id": 99}
    expected = {"status": "ok"}

    def fake_post(url, json, headers):
        assert url == f"{module.RECOMMENDATIONS_URL}history/attend"
        assert json == payload
        assert headers == {"X-User-ID": "3"}
        return DummyResponse(expected)

    monkeypatch.setattr(module.httpx, "post", fake_post)

    assert module.history_attend(3, payload) == expected


def test_history_get_user(monkeypatch):
    expected = [{"event_id": 1}]

    def fake_get(url, headers):
        assert url == f"{module.RECOMMENDATIONS_URL}history/user"
        assert headers == {"X-User-ID": "7"}
        return DummyResponse(expected)

    monkeypatch.setattr(module.httpx, "get", fake_get)

    assert module.history_get_user(7) == expected


def test_history_get_all(monkeypatch):
    expected = [{"user_id": 1, "event_id": 2}]

    def fake_get(url):
        assert url == f"{module.RECOMMENDATIONS_URL}history/all"
        return DummyResponse(expected)

    monkeypatch.setattr(module.httpx, "get", fake_get)

    assert module.history_get_all() == expected
