from dataclasses import dataclass
from typing import Self

from app.db.entity import UserEntity


@dataclass
class RegisterUserDto:
    """
    DTO used during user registration.

    Attributes:
        username: Username chosen by the user.
        email: User email address.
        password: Plain-text password (as provided in request).
        password_confirmation: Password confirmation (as provided in request).
        role: User role (e.g., USER, ADMIN).
    """

    username: str
    email: str
    password: str
    password_confirmation: str
    role: str

    def check_passwords(self) -> bool:
        """
        Validate that password and confirmation match.

        Returns:
            True if password equals password_confirmation, otherwise False.
        """
        return self.password == self.password_confirmation

    def with_password(self, new_password: str) -> Self:
        """
        Create a copy of this DTO with a replaced password.

        Args:
            new_password: New password value.

        Returns:
            New RegisterUserDto instance with updated password.
        """
        return RegisterUserDto(
            username=self.username,
            email=self.email,
            password=new_password,
            password_confirmation=self.password_confirmation,
            role=self.role,
        )

    def to_user_entity(self) -> UserEntity:
        """
        Convert this DTO to a UserEntity.

        Returns:
            UserEntity instance with is_active set to False.
        """
        return UserEntity(
            username=self.username,
            email=self.email,
            password=self.password,
            is_active=False,
            role=self.role,
        )

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> Self:
        """
        Build RegisterUserDto from a dictionary.

        Args:
            data: Dictionary containing registration fields.

        Returns:
            RegisterUserDto instance.
        """
        return cls(
            username=data["username"],
            email=data["email"],
            password=data["password"],
            password_confirmation=data["password_confirmation"],
            role=data["role"],
        )


@dataclass
class UserDto:
    """
    DTO representing a user in API responses.

    Attributes:
        id: User id.
        username: Username.
        email: Email address.
        role: User role.
    """

    id: int
    username: str
    email: str
    role: str

    def to_dict(self) -> dict[str, int | str]:
        """
        Convert this DTO to a dictionary.

        Returns:
            Dictionary containing id, username, email, and role.
        """
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
        }

    @classmethod
    def from_user_entity(cls, user_entity: UserEntity) -> Self:
        """
        Create UserDto from a UserEntity instance.

        Args:
            user_entity: ORM user entity.

        Returns:
            UserDto instance.
        """
        return cls(
            user_entity.id,
            user_entity.username,
            user_entity.email,
            user_entity.role,
        )
