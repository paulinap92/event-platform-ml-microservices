import logging

import httpx
from flask import Blueprint, Response, g, request

from app.config import RECOMMENDATIONS_URL
from app.security.configuration import authorize

logging.basicConfig(level=logging.INFO)

# ---------------------------------------------------------------------
# Survey / Recommendations
# ---------------------------------------------------------------------

recommendations_blueprint = Blueprint(
    "recommendations",
    __name__,
    url_prefix="/api/recommendations",
)


@recommendations_blueprint.route("", methods=["GET"])
@authorize()
def get_recommendations_route():
    """
    Proxy endpoint for fetching recommendations for the current user.
    """
    user_id = g.user_id
    return recommendations_get(user_id)


@recommendations_blueprint.route("", methods=["POST"])
@authorize()
def add_recommendations_route():
    """
    Proxy endpoint for sending a survey to the Recommendations service.
    """
    user_id = g.user_id
    data = request.json

    return recommendations_add(user_id, data)


def recommendations_health_test() -> Response:
    """
    Forward a health-check request to the Recommendations service.
    """
    response = httpx.get(f"{RECOMMENDATIONS_URL}test")
    return response.json()


def recommendations_add(user_id: int, survey_data: dict) -> Response:
    """
    Forward survey data to the Recommendations service.

    Args:
        user_id: ID of the user taken from JWT.
        survey_data: Survey payload.

    Returns:
        JSON response returned by the Recommendations service.
    """
    logging.info(f"[Gateway→Rec] Forwarding survey for user {user_id}")

    response = httpx.post(
        f"{RECOMMENDATIONS_URL}recommendations",
        json=survey_data,
        headers={"X-User-ID": str(user_id)},
    )
    return response.json()


def recommendations_get(user_id: int) -> Response:
    """
    Fetch recommendations for a specific user.

    Args:
        user_id: ID of the user taken from JWT.

    Returns:
        JSON response returned by the Recommendations service.
    """
    logging.info(f"[Gateway→Rec] Fetching survey for user {user_id}")

    response = httpx.get(
        f"{RECOMMENDATIONS_URL}recommendations",
        headers={"X-User-ID": str(user_id)},
    )
    return response.json()


# ---------------------------------------------------------------------
# History of attended events
# ---------------------------------------------------------------------

history_blueprint = Blueprint(
    "history",
    __name__,
    url_prefix="/api/history",
)


@history_blueprint.route("/attend", methods=["POST"])
@authorize()
def attend_event_route():
    """
    Register attendance of the current user for an event.
    """
    user_id = g.user_id
    data = request.json

    return history_attend(user_id, data)


@history_blueprint.route("/user", methods=["GET"])
@authorize()
def get_user_history_route():
    """
    Fetch event history for the current user.
    """
    user_id = g.user_id
    return history_get_user(user_id)


@history_blueprint.route("/all", methods=["GET"])
@authorize()
def get_all_history_route():
    """
    Fetch all event history entries.
    """
    return history_get_all()


@history_blueprint.route("/recommend", methods=["GET"])
@authorize()
def get_all_history_recommendations_route():
    """
    Fetch event recommendations based on user history.
    """
    return history_get_recommendations()


def history_attend(user_id: int, payload: dict) -> Response:
    """
    Forward an attendance request to the History service.

    Args:
        user_id: ID of the user taken from JWT.
        payload: Attendance payload.

    Returns:
        JSON response returned by the History service.
    """
    logging.info(f"[Gateway→History] User {user_id} attends {payload}")

    response = httpx.post(
        f"{RECOMMENDATIONS_URL}history/attend",
        json=payload,
        headers={"X-User-ID": str(user_id)},
    )
    return response.json()


def history_get_user(user_id: int) -> Response:
    """
    Fetch history entries for a specific user.

    Args:
        user_id: ID of the user taken from JWT.

    Returns:
        JSON response returned by the History service.
    """
    logging.info(f"[Gateway→History] Fetching history for user {user_id}")

    response = httpx.get(
        f"{RECOMMENDATIONS_URL}history/user",
        headers={"X-User-ID": str(user_id)},
    )
    return response.json()


def history_get_all() -> Response:
    """
    Fetch all history entries.
    """
    logging.info("[Gateway→History] Fetching ALL history entries")

    response = httpx.get(f"{RECOMMENDATIONS_URL}history/all")
    return response.json()


def history_get_recommendations() -> Response:
    """
    Fetch recommendations based on the current user's history.
    """
    user_id = g.user_id
    logging.info(f"[Gateway→History] Fetching recommendations for user {user_id}")

    response = httpx.get(
        f"{RECOMMENDATIONS_URL}history/recommend",
        headers={"X-User-ID": str(user_id)},
    )
    return response.json()
