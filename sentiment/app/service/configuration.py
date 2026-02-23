from app.service.sentiment_service import SentimentService
from app.db.repository import sentiment_repository


sentiment_service = SentimentService(sentiment_repository)
