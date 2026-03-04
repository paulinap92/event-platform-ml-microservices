import logging

from flask import Response
from flask_restful import Resource, reqparse

from app.service.configuration import user_service
from app.service.dto import RegisterUserDto


logging.basicConfig(level=logging.INFO)


class RegisterUserResource(Resource):
    """
    Resource responsible for user registration.

    Expects a JSON payload with:
    - username
    - email
    - password
    - password_confirmation
    - role
    """

    parser = reqparse.RequestParser()
    parser.add_argument("username", type=str, required=True, help="Username cannot be empty")
    parser.add_argument("email", type=str, required=True, help="Email cannot be empty")
    parser.add_argument("password", type=str, required=True, help="Password cannot be empty")
    parser.add_argument(
        "password_confirmation",
        type=str,
        required=True,
        help="Password confirmation cannot be empty",
    )
    parser.add_argument("role", type=str, required=True, help="Role cannot be empty")

    def post(self) -> Response:
        """
        Register a new user.

        Returns:
            Response returned by user_service.register_user().
        """
        register_user_dto = RegisterUserDto.from_dict(RegisterUserResource.parser.parse_args())
        return user_service.register_user(register_user_dto)


class ActivationUserResource(Resource):
    """
    Resource responsible for activating a user account by token.

    Expects a JSON payload with:
    - token
    """

    parser = reqparse.RequestParser()
    parser.add_argument("token", type=str, required=True, help="Token cannot be empty")

    def post(self) -> Response:
        """
        Activate a user account using the activation token.

        Returns:
            Response returned by user_service.activate_user().
        """
        json_body = ActivationUserResource.parser.parse_args()
        return user_service.activate_user(json_body["token"])
