from app.service.events_service import EventsService
from app.db.repository import events_repository

# Inject repository into the events service layer
events_service = EventsService(events_repository)
