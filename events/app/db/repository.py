from abc import ABC, abstractmethod
from flask_sqlalchemy import SQLAlchemy
from app.db.configuration import sa
from app.db.entity import EventEntity
import logging

logging.basicConfig(level=logging.INFO)



class CrudRepository(ABC):

    @abstractmethod
    def save_or_update(self, entity): # pragma: no cover
        """Persist or update an entity."""
        pass

    @abstractmethod
    def find_by_id(self, entity_id: int): # pragma: no cover
        """Retrieve a single entity by its ID."""
        pass

    @abstractmethod
    def find_all(self): # pragma: no cover
        """Retrieve all entities of this type."""
        pass

    @abstractmethod
    def delete_by_id(self, entity_id: int): # pragma: no cover
        """Delete a single entity by its ID."""
        pass

    @abstractmethod
    def delete_all(self): # pragma: no cover
        """Delete all entities of this type."""
        pass


class CrudRepositoryORM(CrudRepository):

    def __init__(self, db: SQLAlchemy, entity_type):

        self.db = db
        self.entity_type = entity_type

    def save_or_update(self, entity):
        self.db.session.add(entity)
        self.db.session.commit()
        return entity

    def find_by_id(self, entity_id: int):
        return self.db.session.query(self.entity_type).get(entity_id)

    def find_all(self):
        return self.db.session.query(self.entity_type).all()

    def delete_by_id(self, entity_id: int):
        entity = self.find_by_id(entity_id)
        if entity:
            self.db.session.delete(entity)
            self.db.session.commit()

    def delete_all(self):
        self.db.session.query(self.entity_type).delete()
        self.db.session.commit()


# ======================================================================
# EVENTS REPOSITORY
# ======================================================================

class EventsRepository(CrudRepositoryORM):
    """
    Repository responsible for persisting and retrieving events within the
    Event Management microservice.

    This repository also integrates ML category predictions (produced by an
    MLPClassifier) and stores them alongside the event data.
    """

    def __init__(self, db: SQLAlchemy = sa):
        super().__init__(db, EventEntity)

    # ----------------------------------------------------------
    # Save event
    # ----------------------------------------------------------
    def save_event(self, organizer_id: int, event_data: dict, predicted_category: str | None) -> dict:
        """
        Create and persist a new event.

        Args:
            organizer_id: ID of the admin/user who created the event.
            event_data: Dict containing event fields (title, description, etc.).
            predicted_category: Category predicted by the ML model (optional).

        Returns:
            A dictionary representation of the saved EventEntity.
        """
        logging.info(f"[EventsRepository] Saving event for organizer_id={organizer_id}")

        entity = EventEntity(
            organizer_id=organizer_id,
            predicted_category=predicted_category,
            **event_data
        )

        self.db.session.add(entity)
        self.db.session.commit()
        return entity.to_dict()

    # ----------------------------------------------------------
    # Get single event
    # ----------------------------------------------------------
    def get_event_by_id(self, event_id: int):
        """
        Retrieve a single event by ID.

        Args:
            event_id: Event ID.

        Returns:
            EventEntity or None.
        """
        logging.info(f"[EventsRepository] Fetching event_id={event_id}")
        return self.find_by_id(event_id)

    # ----------------------------------------------------------
    # Get all events
    # ----------------------------------------------------------
    def get_events(self):
        """
        Retrieve a list of all events.

        Returns:
            List of EventEntity objects.
        """
        logging.info("[EventsRepository] Fetching all events")
        return self.find_all()

    # ----------------------------------------------------------
    # Delete event
    # ----------------------------------------------------------
    def delete_event(self, event_id: int):
        """
        Delete an event by ID.

        Args:
            event_id: Event ID to delete.
        """
        logging.info(f"[EventsRepository] Deleting event_id={event_id}")
        self.delete_by_id(event_id)


# Global repository instance
events_repository = EventsRepository(sa)
