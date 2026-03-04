from flask_restful import Resource, reqparse
from flask import request
import logging

from app.service.dto import SentimentDto
from app.service.configuration import sentiment_service

logging.basicConfig(level=logging.INFO)


class SentimentResource(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('text', type=str, required=True)

    def post(self):

        user_id = request.headers.get("X-User-ID")

        if not user_id:
            return {"error": "Missing X-User-ID header"}, 401

        raw_data = SentimentResource.parser.parse_args()
        dto = SentimentDto(**raw_data)

        logging.info(f"[SENTIMENT] Running sentiment analysis for user_id={user_id}")

        result = sentiment_service.analyze_text(int(user_id), dto)
        return result, 201

    def get(self):

        logging.info("[SENTIMENT] Fetching all sentiment records")

        all_sentiments = sentiment_service.get_all()
        return all_sentiments, 200
