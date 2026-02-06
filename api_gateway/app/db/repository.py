import logging
from abc import ABC, abstractmethod

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload

from app.db.configuration import sa
from app.db.entity import ActivationTokenEntity, UserEntity

logging.basicConfig(level=logging.INFO)


# -----------------------------------------------------------------------
# [ CRUD REPO ]
# -----------------------------------------------------------------------
class CrudRepository[T](ABC):  # pragma: no cover
    """Base CRUD repository interface."""

    @abstractmethod
    def save_or_update(self, entity: T) -> None:
        """Persist a single entity (insert or update)."""
        raise NotImplementedError

    @abstractmethod
    def save_or_update_many(self, entities: list[T]) -> None:
        """Persist multiple entities (insert or update)."""
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, entity_id: int) -> T | None:
        """Return an entity by id or None if not found."""
        raise NotImplementedError

    @abstractmethod
    def find_all(self) -> list[T]:
        """Return all entities of this type."""
        raise NotImplementedError

    @abstractmethod
    def delete_by_id(self, entity_id: int) -> None:
        """Delete an entity by id if it exists."""
        raise NotImplementedError

    @abstractmethod
    def delete_all(self) -> None:
        """Delete all entities of this type."""
        raise NotImplementedError


# -----------------------------------------------------------------------
# [ CRUD REPO - ORM ]
# -----------------------------------------------------------------------
class CrudRepositoryORM[T: sa.Model](CrudRepository[T]):  # pragma: no cover
    """Generic SQLAlchemy/Flask-SQLAlchemy implementation of CRUD repository."""

    def __init__(self, db: SQLAlchemy) -> None:
        """
        Initialize the repository.

        Args:
            db: Flask-SQLAlchemy instance.
        """
        self.sa = db
        # Entity type is inferred from the generic parameter.
        self.entity_type = self.__class__.__orig_bases__[0].__args__[0]

    def save_or_update(self, entity: T) -> None:
        """Persist a single entity and commit the transaction."""
        self.sa.session.add(entity)
        self.sa.session.commit()

    def save_or_update_many(self, entities: list[T]) -> None:
        """Persist multiple entities and commit the transaction."""
        self.sa.session.add_all(entities)
        self.sa.session.commit()

    def find_by_id(self, entity_id: int) -> T | None:
        """Return an entity by id or None if not found."""
        return self.sa.session.query(self.entity_type).get(entity_id)

    def find_all(self) -> list[T]:
        """Return all entities of this type."""
        return sa.session.query(self.entity_type).all()

    def delete_by_id(self, entity_id: int) -> None:
        """Delete an entity by id if it exists, then commit."""
        entity = self.find_by_id(entity_id)
        if entity:
            self.sa.session.delete(entity)
            self.sa.session.commit()

    def delete_all(self) -> None:
        """Delete all entities of this type and commit."""
        self.sa.session.query(self.entity_type).delete()
        self.sa.session.commit()


class UserRepository(CrudRepositoryORM[UserEntity]):
    """Repository for UserEntity."""

    def __init__(self, db: SQLAlchemy) -> None:
        """
        Initialize the repository.

        Args:
            db: Flask-SQLAlchemy instance.
        """
        super().__init__(db)

    @staticmethod
    def find_by_username(username: str) -> UserEntity | None:
        """Return a user by username or None."""
        return UserEntity.query.filter_by(username=username).first()

    @staticmethod
    def find_by_email(email: str) -> UserEntity | None:
        """Return a user by email or None."""
        return UserEntity.query.filter_by(email=email).first()


class ActivationTokenRepository(CrudRepositoryORM[ActivationTokenEntity]):
    """Repository for ActivationTokenEntity."""

    def __init__(self, db: SQLAlchemy) -> None:
        """
        Initialize the repository.

        Args:
            db: Flask-SQLAlchemy instance.
        """
        super().__init__(db)

    @staticmethod
    def find_by_token(token: str) -> ActivationTokenEntity | None:
        """Return an activation token by token string (with loaded user) or None."""
        return (
            ActivationTokenEntity.query.options(joinedload(ActivationTokenEntity.user))
            .filter_by(token=token)
            .first()
        )


user_repository = UserRepository(sa)
activation_token_repository = ActivationTokenRepository(sa)
