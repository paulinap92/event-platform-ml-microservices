import logging

import httpx
from flask import Blueprint, Response, g, request

from app.config import SENTIMENT_URL
from app.security.configuration import authorize


logging.basicConfig(level=logging.INFO)


# All endpoints under /api/sentiment
sentiment_blueprint = Blueprint(
    "sentiment",
    __name__,
    url_prefix="/api/sentiment",
)

# ---------------------------------------------------------------------
# Endpoints (Gateway → Sentiment)
# ---------------------------------------------------------------------


@sentiment_blueprint.route("/", methods=["GET"])
@authorize()
def get_sentiment_route():
    """
    Proxy endpoint for fetching sentiment data.
    """
    return sentiment_get()


@sentiment_blueprint.route("/", methods=["POST"])
@authorize()
def add_sentiment_route():
    """
    Proxy endpoint for sending sentiment data.

    The user ID is taken from the JWT token (g.user_id) and forwarded
    to the Sentiment service via the X-User-ID header.
    """
    user_id = g.user_id   # user ID from JWT
    data = request.json

    return sentiment_add(user_id, data)


# ---------------------------------------------------------------------
# Forwarding logic
# ---------------------------------------------------------------------


def sentiment_add(user_id: int, payload: dict) -> Response:
    """
    Forward sentiment payload to the Sentiment service.

    Args:
        user_id: ID of the user taken from JWT.
        payload: Sentiment payload.

    Returns:
        JSON response returned by the Sentiment service.
    """
    response = httpx.post(
        f"{SENTIMENT_URL}sentiment",
        json=payload,
        headers={"X-User-ID": str(user_id)},
    )
    return response.json()


def sentiment_get() -> Response:
    """
    Fetch sentiment data from the Sentiment service.

    Returns:
        JSON response returned by the Sentiment service.
    """
    response = httpx.get(f"{SENTIMENT_URL}sentiment")
    return response.json()


def sentiment_health_test() -> Response:
    """
    Forward a health-check request to the Sentiment service.

    Returns:
        JSON response returned by the Sentiment service.
    """
    response = httpx.get(f"{SENTIMENT_URL}test")
    return response.json()
