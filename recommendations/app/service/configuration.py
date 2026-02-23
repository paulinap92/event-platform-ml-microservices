from app.service.recommendations_service import RecommendationsService
from app.service.history_service import HistoryService

from app.db.repository import (
    recommendations_repository,
    history_repository
)


recommendations_service = RecommendationsService(recommendations_repository)
history_service = HistoryService(history_repository)
