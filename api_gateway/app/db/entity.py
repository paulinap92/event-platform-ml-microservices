"""
SQLAlchemy entities used for user authentication and activation.
"""

import datetime

from sqlalchemy import (
    String,
    Boolean,
    BigInteger,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)
from werkzeug.security import generate_password_hash, check_password_hash

from app.db.configuration import sa


class UserEntity(sa.Model):
    """
    SQLAlchemy model representing an application user.

    This entity stores authentication and authorization data for users
    registered in the system. Passwords are stored as hashed values
    using Werkzeug utilities.

    Table:
        users

    Fields:
        id (int):
            Primary key. Unique identifier of the user.

        username (str):
            Public username of the user.

        password (str):
            Hashed password (never stored in plain text).

        email (str):
            User email address.

        role (str):
            User role (e.g. "admin", "user").

        is_active (bool):
            Indicates whether the user account is active.
            Defaults to False until account activation.
    """

    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(255))
    password: Mapped[str] = mapped_column(String(512))
    email: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(10))
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)

    def to_dict(self) -> dict[str, int | str]: # pragma: no cover
        """
        Serialize the user entity to a safe dictionary representation.

        Sensitive fields such as password and email are intentionally excluded.

        Returns:
            dict:
                Dictionary containing public user data:
                - id
                - username
                - role
        """
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role
        }

    def check_password(self, password: str) -> bool: # pragma: no cover
        """
        Verify a plain-text password against the stored hash.

        Args:
            password (str):
                Plain-text password provided by the user.

        Returns:
            bool:
                True if the password matches the stored hash,
                False otherwise.
        """
        return check_password_hash(self.password, password)

    def __str__(self) -> str: # pragma: no cover
        """
        Human-readable string representation of the user entity.

        Returns:
            str:
                String containing user ID and username.
        """
        return f'USER ENTITY: {self.id}, {self.username}'

    def __repr__(self): # pragma: no cover
        return str(self)

class ActivationTokenEntity(sa.Model):
    """
    SQLAlchemy model representing a user activation token.

    This entity is used during the account activation process.
    Each token is linked to a single user and has a time-based validity.

    Table:
        activation_tokens

    Fields:
        id (int):
            Primary key. Unique identifier of the token.

        token (str):
            Activation token value (usually a random string).

        timestamp (int):
            Expiration timestamp (UTC, seconds since epoch).

        user_id (int):
            Foreign key referencing the associated user.

        user (UserEntity):
            Relationship to the UserEntity.
    """

    __tablename__ = 'activation_tokens'

    id: Mapped[int] = mapped_column(primary_key=True)
    token: Mapped[str] = mapped_column(String(255))
    timestamp: Mapped[int] = mapped_column(BigInteger)

    user_id: Mapped[int] = mapped_column(sa.ForeignKey('users.id'))
    user: Mapped[UserEntity] = sa.relationship('UserEntity', uselist=False)

    def is_active(self) -> bool:
        """
        Check whether the activation token is still valid.

        The token is considered active if its timestamp is in the future
        relative to the current UTC time.

        Returns:
            bool:
                True if the token is still valid,
                False if it has expired.
        """
        return self.timestamp > datetime.datetime.now(datetime.UTC).timestamp()
