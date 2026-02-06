import os
import pytest
from datetime import datetime, UTC, timedelta

from app import create_app
from app.db.configuration import sa
from app.db.entity import UserEntity, ActivationTokenEntity
from app.db.repository import UserRepository, ActivationTokenRepository
from app.service.user_service import UserService


# ---------------------------------------------------------------------------
# ENV / DB SETUP
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def test_db_env():
    os.environ["DB_USERNAME"] = "user"
    os.environ["DB_PASSWORD"] = "user1234"
    os.environ["DB_NAME"] = "db_users_test"
    os.environ["DB_HOST"] = "127.0.0.1"
    os.environ["DB_PORT"] = "3308"
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


# ---------------------------------------------------------------------------
# REPOSITORIES / SERVICE
# ---------------------------------------------------------------------------

@pytest.fixture
def repo(app):
    return UserRepository(sa)

@pytest.fixture
def client(app):
    """
    Flask test client for hitting HTTP endpoints
    """
    return app.test_client()


@pytest.fixture
def activation_repo(app):
    return ActivationTokenRepository(sa)


@pytest.fixture
def user_service(repo, activation_repo):
    return UserService(repo, activation_repo)


# ---------------------------------------------------------------------------
# FACTORIES (eliminują duplikację encji w testach)
# ---------------------------------------------------------------------------

@pytest.fixture
def user_factory(session):
    def _create_user(username="john", email="john@example.com",
                     password="xyz", role="USER", is_active=False):
        user = UserEntity(
            username=username,
            email=email,
            password=password,
            role=role,
            is_active=is_active
        )
        session.add(user)
        session.commit()
        return user
    return _create_user


@pytest.fixture
def token_factory(session):
    def _create_token(user, token="ABC", expired=False, lifetime=3600):
        """
        lifetime - liczba sekund do wygaśnięcia tokenu
        expired=True nadpisuje lifetime na -10, aby wymusić wygaśnięcie
        """
        expiry = -10 if expired else lifetime

        token_entity = ActivationTokenEntity(
            token=token,
            timestamp=(datetime.now(UTC) + timedelta(seconds=expiry)).timestamp(),
            user_id=user.id
        )

        session.add(token_entity)
        session.commit()
        return token_entity

    return _create_token
