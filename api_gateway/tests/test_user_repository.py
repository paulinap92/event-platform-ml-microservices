from app.db.entity import UserEntity
from app.db.repository import UserRepository
from app.db.configuration import sa


def test_user_repository_save_and_find(app, session):
    repo = UserRepository(sa)

    user = UserEntity(username="testuser", password ='bfhde', email="t@example.com", role="admin")
    repo.save_or_update(user)

    found = repo.find_by_id(user.id)

    assert found is not None
    assert found.username == "testuser"
    assert found.email == "t@example.com"



def test_find_by_username(repo, app):
    with app.app_context():
        user = UserEntity(username="alice", password ='xxx', email="alice@example.com", role="admin")
        sa.session.add(user)
        sa.session.commit()

        found = repo.find_by_username("alice")
        assert found is not None
        assert found.username == "alice"


def test_find_by_email(repo, app):
    with app.app_context():
        user = UserEntity(username="bob", password = 'xxx', email="bob@example.com", role="admin")
        sa.session.add(user)
        sa.session.commit()

        found = repo.find_by_email("bob@example.com")
        assert found is not None
        assert found.email == "bob@example.com"

