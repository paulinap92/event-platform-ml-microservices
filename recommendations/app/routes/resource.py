from flask_restful import Resource, reqparse
from flask import request
from app.service.dto import RecommendationSurveyDto
from app.service.configuration import recommendations_service, history_service

import logging

logging.basicConfig(level=logging.INFO)


class RecommendationsResource(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('age', type=int, required=True)
    parser.add_argument('gender', type=str, required=True)
    parser.add_argument('city_size', type=str, required=True)
    parser.add_argument('marital_status', type=str, required=True)
    parser.add_argument('children', type=str, required=True)
    parser.add_argument('country_of_origin', type=str, required=True)
    parser.add_argument('occupation', type=str, required=True)
    parser.add_argument('education', type=str, required=True)
    parser.add_argument('income', type=int, required=True)
    parser.add_argument('hobbies', type=str, required=True)
    parser.add_argument('personality_type', type=str, required=True)

    def post(self):

        user_id = request.headers.get("X-User-ID")

        if not user_id:
            return {"error": "Missing X-User-ID header"}, 401

        raw_data = RecommendationsResource.parser.parse_args()
        dto = RecommendationSurveyDto(**raw_data)

        logging.info(f"[RECOMMENDATIONS] Received survey for user_id={user_id}")

        result = recommendations_service.add_survey(int(user_id), dto)
        return result, 201

    def get(self):

        # Zwraca profil ankiety użytkownika + wynik klasyfikacji

        user_id = request.headers.get("X-User-ID")

        if not user_id:
            return {"error": "Missing X-User-ID header"}, 401

        result = recommendations_service.get_survey(int(user_id))

        if result:
            return result, 200

        return {"message": "Survey not found"}, 404


class HistoryAttendResource(Resource):

    def post(self):

        # Otrzymuje zgłoszenie uczestnictwa użytkownika w wydarzeniu.
        # Gateway przesyła user_id w nagłówku:
        # X-User-ID: <id_użytkownika>
        #
        # Body JSON:
        # {
        #     "event_id": <int>
        # }

        user_id = request.headers.get("X-User-ID")
        if not user_id:
            return {"error": "Missing X-User-ID header"}, 401

        data = request.get_json()
        if not data or "event_id" not in data:
            return {"error": "Missing 'event_id' in body"}, 400

        event_id = int(data["event_id"])

        logging.info(f"[HISTORY] User {user_id} attends event {event_id}")

        result = history_service.attend_event(int(user_id), event_id)
        return result, 201

class HistoryUserResource(Resource):

    def get(self):

        # Zwraca wszystkie wydarzenia, w których użytkownik brał udział.
        # Pobiera user_id z nagłówka:
        # X-User-ID: <id>

        user_id = request.headers.get("X-User-ID")
        if not user_id:
            return {"error": "Missing X-User-ID header"}, 401

        history = history_service.get_user_history(int(user_id))
        return {"user_id": int(user_id), "history": history}, 200

class HistoryAllResource(Resource):

    def get(self):

        # Zwraca całą historię wszystkich użytkowników.
        # Używane do Collaborative Filtering

        history = history_service.get_all_history()
        return {"history": history}, 200

class CollaborativeFilteringRecommendations(Resource):

    def get(self):
        user_id = request.headers.get("X-User-ID")
        if not user_id:
            return {"error": "Missing X-User-ID header"}, 401
        history = history_service.recommend_events(int(user_id))
        return {"user_id": int(user_id), "recommended_events": history}, 200