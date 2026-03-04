from flask_restful import Resource, reqparse
from flask import request
import logging

from app.service.dto import EventDto
from app.service.configuration import events_service

logging.basicConfig(level=logging.INFO)


class EventsResource(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('title', type=str, required=True)
    parser.add_argument('description', type=str, required=True)
    parser.add_argument('location', type=str, required=True)
    parser.add_argument('date', type=str, required=True)

    def post(self):

        organizer_id = request.headers.get("X-User-ID")

        if not organizer_id:
            return {"error": "Missing X-User-ID header"}, 401

        raw_data = EventsResource.parser.parse_args()
        dto = EventDto(**raw_data)

        logging.info(f"[EVENTS] Creating event for organizer_id={organizer_id}")

        result = events_service.add_event(int(organizer_id), dto)
        return result, 201

    def get(self):

        logging.info("[EVENTS] Fetching all events")

        events = events_service.get_events()
        return events, 200
