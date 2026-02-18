import datetime
import logging
import random
import string
from dataclasses import dataclass

from werkzeug.security import generate_password_hash

from app.config import (
    ACTIVATION_TOKEN_EXPIRATION_TIME_IN_SECONDS,
    ACTIVATION_TOKEN_LENGTH,
)
from app.db.entity import ActivationTokenEntity
from app.db.repository import ActivationTokenRepository, UserRepository
from app.mail.configuration import MailSender  # noqa: F401
from app.service.dto import RegisterUserDto, UserDto

logging.basicConfig(level=logging.INFO)


@dataclass
class UserService:
    """
    Application service responsible for user registration and activation.

    Attributes:
        user_repository: Repository for UserEntity operations.
        activation_token_repository: Repository for ActivationTokenEntity operations.
    """

    user_repository: UserRepository
    activation_token_repository: ActivationTokenRepository

    def register_user(self, register_user_dto: RegisterUserDto) -> UserDto:
        """
        Register a new user and create an activation token.

        Validation rules (current behavior):
        - passwords must match
        - username must be unique
        - email must be unique

        The user is created as inactive and an activation token is stored.
        Sending an email is currently disabled (commented out).

        Args:
            register_user_dto: Registration payload.

        Returns:
            User dictionary created from UserDto (kept as current behavior).

        Raises:
            ValueError: If validation fails.
        """
        if not register_user_dto.check_passwords():
            raise ValueError("Passwords are not correct")

        if self.user_repository.find_by_username(register_user_dto.username):
            raise ValueError("Username already exists")

        if self.user_repository.find_by_email(register_user_dto.email):
            raise ValueError("Email already exists")

        user_entity = (
            register_user_dto.with_password(
                generate_password_hash(register_user_dto.password)
            ).to_user_entity()
        )
        self.user_repository.save_or_update(user_entity)

        # Generate activation token for the new user.
        timestamp = datetime.datetime.now(datetime.UTC) + datetime.timedelta(
            seconds=ACTIVATION_TOKEN_EXPIRATION_TIME_IN_SECONDS
        )
        token = UserService._generate_token(ACTIVATION_TOKEN_LENGTH)
        user_id = user_entity.id

        self.activation_token_repository.save_or_update(
            ActivationTokenEntity(
                timestamp=timestamp.timestamp(),
                token=token,
                user_id=user_id,
            )
        )

        # Planned for async Flask version / background processing:
        # MailSender.send(
        #     register_user_dto.email,
        #     "Activate Your Account",
        #     f"<h1>Activation Token: {str(token)}</h1>",
        # )

        return UserDto.from_user_entity(user_entity).to_dict()

    def activate_user(self, token: str) -> UserDto:
        """
        Activate a user account using an activation token.

        Current behavior:
        - If token not found -> ValueError('User not found')
        - Token entity is deleted immediately after being found
        - If token expired -> ValueError('Token has been expired')
        - User is activated and saved

        Args:
            token: Activation token string.

        Returns:
            User dictionary created from UserDto (kept as current behavior).

        Raises:
            ValueError: If token is invalid/expired.
        """
        activation_token_with_user = self.activation_token_repository.find_by_token(token)

        if activation_token_with_user is None:
            raise ValueError("User not found")

        self.activation_token_repository.delete_by_id(activation_token_with_user.id)

        if not activation_token_with_user.is_active():
            raise ValueError("Token has been expired")

        user_to_activate = activation_token_with_user.user
        user_to_activate.is_active = True
        self.user_repository.save_or_update(user_to_activate)

        return UserDto.from_user_entity(user_to_activate).to_dict()

    @staticmethod
    def _generate_token(size: int) -> str:
        """
        Generate a random alphanumeric token.

        Args:
            size: Token length.

        Returns:
            Random token string containing letters and digits.
        """
        characters = string.ascii_letters + string.digits
        return "".join([random.choice(characters) for _ in range(size)])
