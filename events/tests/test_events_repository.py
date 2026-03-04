from app.db.entity import EventEntity


# ---------------------------------------------------------------------------
# EVENTS REPOSITORY (wrapper methods)
# ---------------------------------------------------------------------------

def test_save_event_persists_and_returns_dict(repo, session, event_data):
    result = repo.save_event(
        organizer_id=123,
        event_data=event_data,
        predicted_category="music"
    )

    assert isinstance(result, dict)
    assert result["id"] is not None
    assert result["organizer_id"] == 123
    assert result["title"] == event_data["title"]
    assert result["description"] == event_data["description"]
    assert result["location"] == event_data["location"]
    assert result["date"] == event_data["date"]
    assert result["predicted_category"] == "music"

    assert session.query(EventEntity).count() == 1


def test_save_event_allows_null_predicted_category(repo, session, event_data):
    result = repo.save_event(
        organizer_id=1,
        event_data=event_data,
        predicted_category=None
    )

    assert result["predicted_category"] is None
    assert session.query(EventEntity).count() == 1


def test_get_event_by_id_returns_entity(repo, event_data):
    saved = repo.save_event(
        organizer_id=7,
        event_data=event_data,
        predicted_category="sports"
    )
    event_id = saved["id"]

    entity = repo.get_event_by_id(event_id)

    assert entity is not None
    assert isinstance(entity, EventEntity)
    assert entity.id == event_id
    assert entity.organizer_id == 7
    assert entity.title == event_data["title"]
    assert entity.description == event_data["description"]
    assert entity.location == event_data["location"]
    assert entity.date == event_data["date"]
    assert entity.predicted_category == "sports"


def test_get_event_by_id_returns_none_when_missing(repo):
    assert repo.get_event_by_id(999999) is None


def test_get_events_returns_all(repo, event_data):
    repo.save_event(organizer_id=1, event_data=event_data, predicted_category="a")

    repo.save_event(
        organizer_id=2,
        event_data={
            "title": "Second Event",
            "description": "Second description",
            "location": "Barcelona",
            "date": "2026-03-01",
        },
        predicted_category="b"
    )

    events = repo.get_events()

    assert isinstance(events, list)
    assert len(events) == 2
    assert all(isinstance(e, EventEntity) for e in events)

    titles = sorted([e.title for e in events])
    assert titles == ["Second Event", "Test Event"]


def test_delete_event_removes_row(repo, session, event_data):
    saved = repo.save_event(
        organizer_id=1,
        event_data=event_data,
        predicted_category=None
    )
    event_id = saved["id"]

    assert session.query(EventEntity).count() == 1

    repo.delete_event(event_id)

    assert session.query(EventEntity).count() == 0
    assert repo.get_event_by_id(event_id) is None


def test_delete_event_missing_id_does_not_crash(repo, session):
    repo.delete_event(999999)
    assert session.query(EventEntity).count() == 0


# ---------------------------------------------------------------------------
# CRUD BASE CLASS COVERAGE (CrudRepositoryORM)
# ---------------------------------------------------------------------------

def test_save_or_update_persists_entity(repo, session, event_data):
    entity = EventEntity(
        organizer_id=123,
        predicted_category="music",
        **event_data
    )

    saved = repo.save_or_update(entity)

    assert saved is entity
    assert saved.id is not None
    assert session.query(EventEntity).count() == 1

    db_row = session.query(EventEntity).first()
    assert db_row.organizer_id == 123
    assert db_row.title == event_data["title"]


def test_find_all_and_find_by_id(repo, event_data):
    e1 = EventEntity(organizer_id=1, predicted_category=None, **event_data)
    e2 = EventEntity(
        organizer_id=2,
        predicted_category="x",
        title="E2",
        description="D2",
        location="L2",
        date="2026-01-01",
    )

    repo.save_or_update(e1)
    repo.save_or_update(e2)

    all_events = repo.find_all()
    assert len(all_events) == 2

    found = repo.find_by_id(e1.id)
    assert found is not None
    assert found.id == e1.id
    assert found.organizer_id == 1


def test_delete_by_id_existing_and_missing(repo, session, event_data):
    e = EventEntity(organizer_id=1, predicted_category=None, **event_data)
    repo.save_or_update(e)
    assert session.query(EventEntity).count() == 1

    repo.delete_by_id(e.id)
    assert session.query(EventEntity).count() == 0

    # missing id should do nothing
    repo.delete_by_id(999999)
    assert session.query(EventEntity).count() == 0


def test_delete_all_deletes_everything(repo, session, event_data):
    repo.save_event(organizer_id=1, event_data=event_data, predicted_category=None)
    repo.save_event(
        organizer_id=2,
        event_data={"title": "E2", "description": "D2", "location": "L2", "date": "2026-01-01"},
        predicted_category=None
    )

    assert session.query(EventEntity).count() == 2

    repo.delete_all()

    assert session.query(EventEntity).count() == 0
