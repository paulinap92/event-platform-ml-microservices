from app.db.configuration import sa
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Text


class EventEntity(sa.Model):

    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # organizer (admin) ID – always derived from authentication (X-User-ID)
    organizer_id: Mapped[int] = mapped_column(Integer, nullable=False)

    # core event fields
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str] = mapped_column(String(200), nullable=False)
    date: Mapped[str] = mapped_column(String(50), nullable=False)

    # ML prediction output (optional)
    predicted_category: Mapped[str] = mapped_column(String(100), nullable=True)

    def to_dict(self): # pragma: no cover

        return {
            "id": self.id,
            "organizer_id": self.organizer_id,
            "title": self.title,
            "description": self.description,
            "location": self.location,
            "date": self.date,
            "predicted_category": self.predicted_category
        }

    def __str__(self): # pragma: no cover

        return (
            f"EventEntity("
            f"id={self.id}, organizer_id={self.organizer_id}, "
            f"title={self.title}, description={self.description}, "
            f"location={self.location}, date={self.date}, "
            f"predicted_category={self.predicted_category})"
        )

    def __repr__(self): # pragma: no cover
         return str(self)
