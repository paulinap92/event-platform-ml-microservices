from abc import ABC, abstractmethod
from flask_sqlalchemy import SQLAlchemy
from app.db.configuration import sa
from app.db.entity import RecommendationProfileEntity, HistoryEntity
import logging

logging.basicConfig(level=logging.INFO)


class CrudRepository(ABC):

    @abstractmethod
    def save_or_update(self, entity):
        pass

    @abstractmethod
    def find_by_id(self, entity_id: int):
        pass

    @abstractmethod
    def find_all(self):
        pass

    @abstractmethod
    def delete_by_id(self, entity_id: int):
        pass

    @abstractmethod
    def delete_all(self):
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



class RecommendationsRepository(CrudRepositoryORM):
    """
    Repozytorium odpowiedzialne za zapis/odczyt ankiety
    wraz z predykcją ML w ramach mikroserwisu rekomendacji.
    """

    def __init__(self, db: SQLAlchemy = sa):
        super().__init__(db, RecommendationProfileEntity)

    def save_user_survey(self, user_id: int, survey_data: dict) -> dict:
        logging.info(f"[RecommendationsRepository] Saving survey for user_id={user_id}")

        entity = RecommendationProfileEntity(
            user_id=user_id,
            **survey_data
        )

        self.db.session.add(entity)
        self.db.session.commit()
        return entity.to_dict()


    def get_survey_by_user(self, user_id: int):
        logging.info(f"[RecommendationsRepository] Fetching survey for user_id={user_id}")

        return (
            self.db.session.query(RecommendationProfileEntity)
            .filter(RecommendationProfileEntity.user_id == user_id)
            .first()
        )

class HistoryRepository(CrudRepositoryORM):

    def __init__(self, db: SQLAlchemy = sa):
        super().__init__(db, HistoryEntity)


    def add_history(self, user_id: int, event_id: int):
        logging.info(f"[HistoryRepository] Adding event history: user={user_id}, event={event_id}")

        entity = HistoryEntity(
            user_id=user_id,
            event_id=event_id
        )
        self.db.session.add(entity)
        self.db.session.commit()

        return entity.to_dict()


    def get_user_history(self, user_id: int):
        logging.info(f"[HistoryRepository] Fetching history for user_id={user_id}")

        return (
            self.db.session.query(HistoryEntity)
            .filter(HistoryEntity.user_id == user_id)
            .all()
        )

    # ----------------------------------------------------------
    # Pobranie CAŁEJ historii wszystkich użytkowników
    #    - potrzebne do Collaborative Filtering
    # ----------------------------------------------------------
    def get_all_history(self):
        logging.info("[HistoryRepository] Fetching ALL history records for CF engine")
        return self.find_all()


recommendations_repository = RecommendationsRepository(sa)
history_repository = HistoryRepository(sa)
