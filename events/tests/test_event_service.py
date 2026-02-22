import importlib
from io import BytesIO

import pytest


# -----------------------------------------------------------------------------
# Dummy ML artifacts
# -----------------------------------------------------------------------------

class DummyPipeline:
    def __init__(self, encoded_prediction=7):
        self.encoded_prediction = encoded_prediction
        self.last_input = None

    def predict(self, X):
        # X: list[str]
        self.last_input = X
        return [self.encoded_prediction]


class DummyLabelEncoder:
    def __init__(self, decoded_label="sports"):
        self.decoded_label = decoded_label
        self.last_input = None

    def inverse_transform(self, y):
        # y: list[int]
        self.last_input = y
        return [self.decoded_label]


# -----------------------------------------------------------------------------
# Dummy repo + DTO + entity
# -----------------------------------------------------------------------------

class DummyRepo:
    def __init__(self):
        self.saved_calls = []
        self.events_by_id = {}
        self.deleted_ids = []

    def save_event(self, organizer_id: int, event_data: dict, predicted_category: str | None):
        self.saved_calls.append((organizer_id, event_data, predicted_category))
        return {
            "id": 1,
            "organizer_id": organizer_id,
            **event_data,
            "predicted_category": predicted_category,
        }

    def get_event_by_id(self, event_id: int):
        return self.events_by_id.get(event_id)

    def get_events(self):
        return list(self.events_by_id.values())

    def delete_event(self, event_id: int):
        self.deleted_ids.append(event_id)
        self.events_by_id.pop(event_id, None)


class DummyEventEntity:
    def __init__(self, id, organizer_id, title, description, location, date, predicted_category=None):
        self.id = id
        self.organizer_id = organizer_id
        self.title = title
        self.description = description
        self.location = location
        self.date = date
        self.predicted_category = predicted_category

    def to_dict(self):
        return {
            "id": self.id,
            "organizer_id": self.organizer_id,
            "title": self.title,
            "description": self.description,
            "location": self.location,
            "date": self.date,
            "predicted_category": self.predicted_category,
        }


class DummyEventDto:
    def __init__(self, title, description, location, date):
        self.title = title
        self.description = description
        self.location = location
        self.date = date

    def to_dict(self):
        return {
            "title": self.title,
            "description": self.description,
            "location": self.location,
            "date": self.date,
        }


# -----------------------------------------------------------------------------
# Import module with ML loading mocked (important!)
# -----------------------------------------------------------------------------

@pytest.fixture
def service_bundle(monkeypatch):
    """
    The EventsService module loads ML artifacts at import time.
    We patch open() and joblib.load() BEFORE importing/reloading the module.
    """
    import builtins
    import joblib

    # open(...) must return a context-manager; BytesIO works
    monkeypatch.setattr(builtins, "open", lambda *args, **kwargs: BytesIO(b"fake-bytes"))

    pipeline = DummyPipeline(encoded_prediction=7)
    encoder = DummyLabelEncoder(decoded_label="sports")

    # joblib.load called twice: pipeline first, encoder second
    loads = iter([pipeline, encoder])
    monkeypatch.setattr(joblib, "load", lambda *args, **kwargs: next(loads))

    # IMPORTANT: import AFTER patching
    import app.service.events_service as module  # <-- ZMIEŃ na swój moduł
    module = importlib.reload(module)

    # make sure globals point to our fake objects
    module.model_pipeline = pipeline
    module.label_encoder = encoder

    return module, pipeline, encoder


@pytest.fixture
def repo():
    return DummyRepo()


@pytest.fixture
def service(service_bundle, repo):
    module, _, _ = service_bundle
    return module.EventsService(repo=repo)


# -----------------------------------------------------------------------------
# add_event
# -----------------------------------------------------------------------------

def test_add_event_runs_prediction_and_saves(service_bundle, repo):
    module, pipeline, encoder = service_bundle
    service = module.EventsService(repo=repo)

    dto = DummyEventDto(
        title="Rock concert",
        description="Live music and guitars",
        location="Madrid",
        date="2026-02-10",
    )

    result = service.add_event(organizer_id=123, dto=dto)

    # ML input
    assert pipeline.last_input == ["Rock concert Live music and guitars"]
    assert encoder.last_input == [7]

    # repo call
    assert len(repo.saved_calls) == 1
    organizer_id, event_data, predicted_category = repo.saved_calls[0]
    assert organizer_id == 123
    assert event_data == dto.to_dict()
    assert predicted_category == "sports"

    # returned result
    assert result["id"] == 1
    assert result["organizer_id"] == 123
    assert result["title"] == "Rock concert"
    assert result["predicted_category"] == "sports"


# -----------------------------------------------------------------------------
# get_event
# -----------------------------------------------------------------------------

def test_get_event_returns_dict_when_exists(service, repo):
    repo.events_by_id[10] = DummyEventEntity(
        id=10,
        organizer_id=1,
        title="E",
        description="D",
        location="L",
        date="2026-01-01",
        predicted_category="music",
    )

    result = service.get_event(10)

    assert result == {
        "id": 10,
        "organizer_id": 1,
        "title": "E",
        "description": "D",
        "location": "L",
        "date": "2026-01-01",
        "predicted_category": "music",
    }


def test_get_event_returns_none_when_missing(service):
    assert service.get_event(9999) is None


# -----------------------------------------------------------------------------
# get_events
# -----------------------------------------------------------------------------

def test_get_events_returns_list_of_dicts(service, repo):
    repo.events_by_id[1] = DummyEventEntity(1, 1, "A", "DA", "LA", "2026-01-01", "x")
    repo.events_by_id[2] = DummyEventEntity(2, 2, "B", "DB", "LB", "2026-01-02", None)

    result = service.get_events()

    assert result == [
        {"id": 1, "organizer_id": 1, "title": "A", "description": "DA", "location": "LA", "date": "2026-01-01", "predicted_category": "x"},
        {"id": 2, "organizer_id": 2, "title": "B", "description": "DB", "location": "LB", "date": "2026-01-02", "predicted_category": None},
    ]


# -----------------------------------------------------------------------------
# delete_event
# -----------------------------------------------------------------------------

def test_delete_event_returns_false_when_missing(service, repo):
    assert service.delete_event(12345) is False
    assert repo.deleted_ids == []


def test_delete_event_deletes_and_returns_true(service, repo):
    repo.events_by_id[5] = DummyEventEntity(5, 1, "A", "D", "L", "2026-01-01", None)

    ok = service.delete_event(5)

    assert ok is True
    assert repo.deleted_ids == [5]
    assert 5 not in repo.events_by_id
