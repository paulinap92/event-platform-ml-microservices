import datetime
import logging
from functools import wraps

import jwt
from flask import current_app, make_response, request, g

from app.db.repository import user_repository


logging.basicConfig(level=logging.INFO)


def configure_security() -> None:
    """
    Register security routes (login and refresh) on the current Flask app.

    This function must be called after the Flask app is created and an app
    context is available, because it uses `current_app.route(...)`.
    """

    # --------------------------------------------------------------------------------------------------------------
    # Login
    # --------------------------------------------------------------------------------------------------------------
    @current_app.route("/login", methods=["POST"])
    def login():
        """
        Authenticate a user and return access/refresh tokens.

        Returns:
            - 201 + tokens (JSON body + headers + cookies) on success
            - 400/500 on authentication errors (as defined by current logic)
        """
        data = request.get_json()
        username = data["username"]
        password = data["password"]

        user = user_repository.find_by_username(username)

        if not user:
            return make_response({"message": "Authentication - user not found"}, 400)

        if not user.is_active:
            return make_response({"message": "Authentication - user is not active"}, 500)

        if not user.check_password(password):
            return make_response({"message": "Authentication - password is not correct"}, 400)

        access_token_exp = int(
            (
                datetime.datetime.now(datetime.UTC)
                + datetime.timedelta(minutes=current_app.config["JWT_ACCESS_MAX_AGE"])
            ).timestamp()
        )
        refresh_token_exp = int(
            (
                datetime.datetime.now(datetime.UTC)
                + datetime.timedelta(minutes=current_app.config["JWT_REFRESH_MAX_AGE"])
            ).timestamp()
        )

        access_token_payload = {
            "iat": datetime.datetime.now(datetime.UTC),
            "exp": access_token_exp,
            "sub": str(user.id),
            "role": str(user.role),
        }

        refresh_token_payload = {
            "iat": datetime.datetime.now(datetime.UTC),
            "exp": refresh_token_exp,
            "sub": str(user.id),
            "role": user.role,
            "access_token_exp": access_token_exp,
        }

        access_token = jwt.encode(
            access_token_payload,
            current_app.config["JWT_SECRET"],
            algorithm=current_app.config["JWT_AUTHTYPE"],
        )
        refresh_token = jwt.encode(
            refresh_token_payload,
            current_app.config["JWT_SECRET"],
            algorithm=current_app.config["JWT_AUTHTYPE"],
        )

        # Version 1 - return tokens in JSON body
        response_body = {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
        response = make_response(response_body, 201)

        # Version 2 - set headers
        response.headers["Access-Token"] = access_token
        response.headers["Refresh-Token"] = refresh_token

        # Version 3 - set cookies
        response.set_cookie("AccessToken", access_token, httponly=True)
        response.set_cookie("RefreshToken", refresh_token, httponly=True)

        return response

    # --------------------------------------------------------------------------------------------------------------
    # Refresh token
    # --------------------------------------------------------------------------------------------------------------
    @current_app.route("/refresh", methods=["POST"])
    def refresh():
        """
        Refresh access token using a refresh token provided in JSON body.

        Returns:
            - 201 + new tokens (JSON body + headers) on success
            - Exceptions from jwt.decode are not caught here (kept as-is)
        """
        # Refresh token is provided in JSON body (or can be taken from headers/cookies).
        request_data = request.get_json()
        refresh_token = request_data["token"]
        # refresh_token = request.headers.get('Refresh-Token')
        # refresh_token = request.cookies.get('RefreshToken')

        # Decode refresh token
        decoded_refresh_token = jwt.decode(
            refresh_token,
            current_app.config["JWT_SECRET"],
            algorithms=[current_app.config["JWT_AUTHTYPE"]],
        )

        logging.info(">>>>>>>>>>>>>>>>>> TIMESTAMPS")
        logging.info(decoded_refresh_token["access_token_exp"])
        logging.info(datetime.datetime.now(datetime.UTC).timestamp())
        logging.info(decoded_refresh_token["access_token_exp"] < datetime.datetime.now(datetime.UTC).timestamp())
        # if decoded_refresh_token['access_token_exp'] < datetime.datetime.now(datetime.UTC).timestamp():
        #     return make_response({'message': 'Cannot refresh token - access token has been expired'}, 401)

        # Compute new access token expiration
        new_access_token_exp = int(
            (
                datetime.datetime.now(datetime.UTC)
                + datetime.timedelta(minutes=current_app.config["JWT_ACCESS_MAX_AGE"])
            ).timestamp()
        )

        access_token_payload = {
            "iat": datetime.datetime.now(datetime.UTC),
            "exp": new_access_token_exp,
            "sub": decoded_refresh_token["sub"],
            "role": decoded_refresh_token["role"],
        }

        refresh_token_payload = {
            "iat": datetime.datetime.now(datetime.UTC),
            "exp": decoded_refresh_token["exp"],
            "sub": decoded_refresh_token["sub"],
            "role": decoded_refresh_token["role"],
            "access_token_exp": new_access_token_exp,
        }

        access_token = jwt.encode(
            access_token_payload,
            current_app.config["JWT_SECRET"],
            algorithm=current_app.config["JWT_AUTHTYPE"],
        )
        refresh_token = jwt.encode(
            refresh_token_payload,
            current_app.config["JWT_SECRET"],
            algorithm=current_app.config["JWT_AUTHTYPE"],
        )

        # Version 1 - return tokens in JSON body
        response_body = {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
        response = make_response(response_body, 201)

        # Version 2 - set headers
        response.headers["Access-Token"] = access_token
        response.headers["Refresh-Token"] = refresh_token

        # Version 3 - cookies (disabled as in original)
        # response.set_cookie('AccessToken', access_token, httponly=True)
        # response.set_cookie('RefreshToken', refresh_token, httponly=True)

        return response


# --------------------------------------------------------------------------------------------------------------
# Authorization decorator
# --------------------------------------------------------------------------------------------------------------


def authorize(roles: list[str] | None = None):
    """
    Authorization decorator based on JWT access token in the Authorization header.

    Args:
        roles: Optional list of allowed roles. If provided, user must match one of them.

    Returns:
        Decorator that:
        - validates Authorization header format and JWT token
        - stores user id in `g.user_id`
        - optionally enforces roles
        - returns 401/403 responses according to current logic
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Access token is taken from the Authorization header.
                # access_token = request.cookies.get('access_token', None)

                header = request.headers.get("Authorization")
                if not header:
                    return make_response({"message": "Authorization failed - no header"}, 401)

                if not header.startswith(current_app.config["JWT_PREFIX"]):
                    return make_response(
                        {"message": "Authorization failed - access token without prefix"},
                        401,
                    )

                # Split prefix and token
                logging.info(">>>>>>>>>>>>>>>>>> AUTH HEADER")
                logging.info(header)

                access_token = str(header.split(" ")[1])

                logging.info(access_token)

                decoded_access_token = jwt.decode(
                    access_token,
                    current_app.config["JWT_SECRET"],
                    algorithms=[current_app.config["JWT_AUTHTYPE"]],
                )

                logging.info(">>>>>>>>>>>>>>>>>> AUTH HEADER")
                logging.info(decoded_access_token)

                g.user_id = int(decoded_access_token["sub"])

                logging.info(g.user_id)
                logging.info("ACCESS TOKEN DATA")
                logging.info(decoded_access_token["role"])

                if roles and decoded_access_token["role"].lower() not in [
                    role.lower() for role in roles
                ]:
                    return make_response({"message": "Access denied!"}, 403)

            except Exception as error:
                logging.info(repr(error))
                return make_response({"message": "Authorization failed"}, 401)

            return f(*args, **kwargs)

        return decorated_function

    return decorator
