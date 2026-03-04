import os
import pytest

from app import create_app
from app.db.configuration import sa
from app.db.repository import EventsRepository  # <- dopasuj ścieżkę


# ---------------------------------------------------------------------------
# ENV / DB SETUP (Docker MySQL test DB)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def test_db_env():
    # dopasuj do swojego kontenera testowego
    os.environ["DB_USERNAME"] = "user"
    os.environ["DB_PASSWORD"] = "user1234"
    os.environ["DB_NAME"] = "db_events_test"
    os.environ["DB_HOST"] = "127.0.0.1"
    os.environ["DB_PORT"] = "3312"  # <- np. inny port niż users
    yield


@pytest.fixture
def app(test_db_env):
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_ECHO": False,
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    })

    with app.app_context():
        sa.create_all()
        yield app
        sa.session.remove()
        sa.drop_all()


@pytest.fixture
def session(app):
    return sa.session


@pytest.fixture
def repo(app):
    return EventsRepository(sa)


@pytest.fixture
def event_data():
    return {
        "title": "Test Event",
        "description": "Test description",
        "location": "Madrid",
        "date": "2026-02-10",
    }
