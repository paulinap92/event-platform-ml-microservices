import app.routes.sentiments as module


class DummyResponse:
    def __init__(self, payload):
        self.payload = payload

    def json(self):
        return self.payload


def test_sentiment_health(monkeypatch):
    expected = {"status": "ok"}

    def fake_get(url):
        assert url == f"{module.SENTIMENT_URL}test"
        return DummyResponse(expected)

    monkeypatch.setattr(module.httpx, "get", fake_get)

    result = module.sentiment_health_test()
    assert result == expected


def test_sentiment_get(monkeypatch):
    expected = [{"label": "positive", "score": 0.92}]

    def fake_get(url):
        assert url == f"{module.SENTIMENT_URL}sentiment"
        return DummyResponse(expected)

    monkeypatch.setattr(module.httpx, "get", fake_get)

    result = module.sentiment_get()
    assert result == expected


def test_sentiment_add(monkeypatch):
    user_id = 42
    payload = {"text": "I love this event"}
    expected = {"label": "positive", "score": 0.95}

    def fake_post(url, json, headers):
        assert url == f"{module.SENTIMENT_URL}sentiment"
        assert json == payload
        assert headers == {"X-User-ID": str(user_id)}
        return DummyResponse(expected)

    monkeypatch.setattr(module.httpx, "post", fake_post)

    result = module.sentiment_add(user_id, payload)
    assert result == expected
