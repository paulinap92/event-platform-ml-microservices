from app.db.entity import UserEntity, ActivationTokenEntity
from app.db.repository import ActivationTokenRepository, UserRepository
from app.db.configuration import sa


def test_activation_token_save_and_find(app, session):
    user_repo = UserRepository(sa)
    token_repo = ActivationTokenRepository(sa)

    user = UserEntity(username="u", password = 'xcvxvxb', email="u@example.com", role="user")
    user_repo.save_or_update(user)

    token = ActivationTokenEntity(token="ABC123", timestamp = 1,  user_id=user.id)
    token_repo.save_or_update(token)

    found = ActivationTokenRepository.find_by_token("ABC123")

    assert found is not None
    assert found.token == "ABC123"
    assert found.user.id == user.id
