import pytest
from app.service.dto import RegisterUserDto


def test_register_user_success(user_service, session):
    dto = RegisterUserDto(
        username="john",
        email="john@example.com",
        password="secret",
        password_confirmation="secret",
        role="USER"
    )

    result = user_service.register_user(dto)

    assert result["username"] == "john"
    assert "id" in result

    # sprawdzamy czy user i token są utworzeni
    from app.db.entity import UserEntity, ActivationTokenEntity
    assert session.query(UserEntity).count() == 1
    assert session.query(ActivationTokenEntity).count() == 1


def test_register_user_password_mismatch(user_service):
    dto = RegisterUserDto(
        username="john",
        email="john@example.com",
        password="a",
        password_confirmation="b",
        role="USER"
    )

    with pytest.raises(ValueError):
        user_service.register_user(dto)


def test_register_user_username_exists(user_service, user_factory):
    user_factory(username="john")  # zamiast 6 linii ręcznego tworzenia encji

    dto = RegisterUserDto(
        username="john",
        email="john2@example.com",
        password="secret",
        password_confirmation="secret",
        role="USER"
    )

    with pytest.raises(ValueError, match="Username already exists"):
        user_service.register_user(dto)


def test_register_user_mail_exists(user_service, user_factory):
    user_factory(email="john@example.com")  # dużo czyściej

    dto = RegisterUserDto(
        username="john88",
        email="john@example.com",
        password="secret",
        password_confirmation="secret",
        role="USER"
    )

    with pytest.raises(ValueError, match="Email already exists"):
        user_service.register_user(dto)


def test_activate_user_success(user_service, user_factory, token_factory, session):
    user = user_factory(is_active=False)
    token_factory(user, token="XYZ")  # TOKEN WAŻNY

    result = user_service.activate_user("XYZ")

    assert result["username"] == user.username

    # sprawdzamy flagę aktywacji
    assert session.get(type(user), user.id).is_active is True


def test_activate_user_not_found(user_service):
    with pytest.raises(ValueError, match="User not found"):
        user_service.activate_user("UNKNOWN")


def test_activate_user_expired(user_service, user_factory, token_factory):
    user = user_factory()
    token_factory(user, token="XYZ", expired=True)  # wymuszona utrata ważności

    with pytest.raises(ValueError, match="Token has been expired"):
        user_service.activate_user("XYZ")
