from abc import ABC, abstractmethod
from flask_sqlalchemy import SQLAlchemy
from app.db.configuration import sa
from app.db.entity import SentimentEntity
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


# ======================================================================
# ORM CRUD IMPLEMENTATION
# ======================================================================

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




class SentimentRepository(CrudRepositoryORM):
    """
    Repository for sentiment analysis records.
    Stores original text + ML-predicted sentiment + confidence level.
    """

    def __init__(self, db: SQLAlchemy = sa):
        super().__init__(db, SentimentEntity)


    # ----------------------------------------------------------
    def save_sentiment(self, user_id: int | None, text: str,
                       predicted_sentiment: str, confidence: float) -> dict:
        logging.info(f"[SentimentRepository] Saving sentiment for user_id={user_id}")

        entity = SentimentEntity(
            user_id=user_id,
            text=text,
            predicted_sentiment=predicted_sentiment,
            confidence=confidence
        )

        self.db.session.add(entity)
        self.db.session.commit()
        return entity.to_dict()

    def get_sentiment_by_id(self, sentiment_id: int):
        logging.info(f"[SentimentRepository] Fetching sentiment_id={sentiment_id}")
        return self.find_by_id(sentiment_id)


    def get_all_sentiments(self):
        logging.info("[SentimentRepository] Fetching all sentiment records")
        return self.find_all()


    def delete_sentiment(self, sentiment_id: int):
        logging.info(f"[SentimentRepository] Deleting sentiment_id={sentiment_id}")
        self.delete_by_id(sentiment_id)


# Global instance
sentiment_repository = SentimentRepository(sa)
