from __future__ import annotations

import logging
from typing import Any

import httpx
from flask import Blueprint, g, request

from app.config import EVENTS_URL
from app.security.configuration import authorize

from flask.typing import ResponseReturnValue

logging.basicConfig(level=logging.INFO)

events_blueprint = Blueprint("events", __name__, url_prefix="/api/events")


@events_blueprint.route("/", methods=["GET"])
@authorize()
def get_events_route() -> Any:
    """
    GET /api/events/

    Proxy endpoint to fetch events from the Events microservice.

    Auth:
        Requires JWT (@authorize()).

    Returns:
        JSON-like Python object (usually list[dict]) returned by Events service.
        Flask will serialize it to a JSON HTTP response automatically.
    """
    return events_get()


@events_blueprint.route("/", methods=["POST"])
@authorize()
def add_event_route() -> Any:
    """
    POST /api/events/

    Proxy endpoint to create a new event in the Events microservice.

    Organizer:
        organizer_id is taken from JWT context (g.user_id) and forwarded
        via X-User-ID header.

    Body:
        JSON with fields required by Events service (title, description, location, date).

    Returns:
        JSON-like Python object (dict) returned by Events service.
    """
    organizer_id = g.user_id
    data = request.json
    return events_add(organizer_id, data)


def events_add(organizer_id: int, event_data: dict) -> Any:
    """
    Calls Events microservice to create a new event.

    Args:
        organizer_id: Organizer/admin id (from JWT).
        event_data: Event payload (title, description, location, date).

    Returns:
        JSON-like Python object returned by Events service (dict).

    Notes:
        This function returns parsed JSON, not a Flask Response.
    """
    response = httpx.post(
        f"{EVENTS_URL}events",
        json=event_data,
        headers={"X-User-ID": str(organizer_id)},
    )
    return response.json()


def events_get() -> Any:
    """
    Calls Events microservice to fetch all events.

    Returns:
        JSON-like Python object returned by Events service (usually list[dict]).
    """
    response = httpx.get(f"{EVENTS_URL}events")
    return response.json()


def events_health_test() -> Any:
    """
    Calls Events microservice health/test endpoint.

    Returns:
        JSON-like Python object returned by Events service.
    """
    response = httpx.get(f"{EVENTS_URL}test")
    return response.json()
