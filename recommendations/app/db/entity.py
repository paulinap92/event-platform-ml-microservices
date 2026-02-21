from app.db.configuration import sa
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String

from app.db.configuration import sa
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, DateTime, func


class RecommendationProfileEntity(sa.Model):
    """
    Represents a user recommendation profile stored within the
    recommendations microservice. It contains both raw survey inputs
    and the ML-generated event preference produced by the recommendation model.
    """

    __tablename__ = "recommendation_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)

    # Survey attributes (raw user profile data)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    gender: Mapped[str] = mapped_column(String(50), nullable=False)
    city_size: Mapped[str] = mapped_column(String(50), nullable=False)
    marital_status: Mapped[str] = mapped_column(String(50), nullable=False)
    children: Mapped[str] = mapped_column(String(10), nullable=False)
    country_of_origin: Mapped[str] = mapped_column(String(50), nullable=False)
    occupation: Mapped[str] = mapped_column(String(50), nullable=False)
    education: Mapped[str] = mapped_column(String(50), nullable=False)
    income: Mapped[int] = mapped_column(Integer, nullable=False)
    hobbies: Mapped[str] = mapped_column(String(200), nullable=False)
    personality_type: Mapped[str] = mapped_column(String(50), nullable=False)

    # ML prediction output
    event_preference: Mapped[str] = mapped_column(String(100), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "age": self.age,
            "gender": self.gender,
            "city_size": self.city_size,
            "marital_status": self.marital_status,
            "children": self.children,
            "country_of_origin": self.country_of_origin,
            "occupation": self.occupation,
            "education": self.education,
            "income": self.income,
            "hobbies": self.hobbies,
            "personality_type": self.personality_type,
            "event_preference": self.event_preference
        }

    def __str__(self):
        return (
            f"RecommendationProfile("
            f"id={self.id}, user_id={self.user_id}, age={self.age}, gender={self.gender}, "
            f"city_size={self.city_size}, marital_status={self.marital_status}, children={self.children}, "
            f"country_of_origin={self.country_of_origin}, occupation={self.occupation}, education={self.education}, "
            f"income={self.income}, hobbies={self.hobbies}, personality_type={self.personality_type}, "
            f"event_preference={self.event_preference})"
        )

    def __repr__(self):
        return str(self)
#todo tu sa dwa przypadki rekomendacji (klasyfikacji), jeden na podstawie survey, ale nigdzie nie jest zaimplementowany
#todo uznalam, ze to najlepsze miejce na zapisanie historii w celu rekomendacji na podstawie historii, czy tak ma zostac?

class HistoryEntity(sa.Model):
    """
    Stores user event participation history inside the recommendations microservice.

    Used by Collaborative Filtering (item-based CF) to generate recommendations
    based on event co-occurrence.
    """

    __tablename__ = "event_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    event_id: Mapped[int] = mapped_column(Integer, nullable=False)

    # Timestamp when the user attended the event
    attended_at: Mapped[str] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    def to_dict(self):
          return {
            "id": self.id,
            "user_id": self.user_id,
            "event_id": self.event_id,
            "attended_at": self.attended_at.isoformat() if self.attended_at else None
        }

    def __str__(self):
        return (
            f"HistoryEntity(id={self.id}, user_id={self.user_id}, "
            f"event_id={self.event_id}, attended_at={self.attended_at})"
        )

    def __repr__(self):
        return str(self)
