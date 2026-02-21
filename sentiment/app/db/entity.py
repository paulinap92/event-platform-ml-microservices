from app.db.configuration import sa
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Text, Float


class SentimentEntity(sa.Model):


    __tablename__ = "sentiment"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # optional: user ID (from X-User-ID), allows personal sentiment tracking
    user_id: Mapped[int] = mapped_column(Integer, nullable=True)

    # input text to analyze
    text: Mapped[str] = mapped_column(Text, nullable=False)

    # ML outputs
    predicted_sentiment: Mapped[str] = mapped_column(String(50), nullable=False)  # "positive", "neutral", "negative"
    confidence: Mapped[float] = mapped_column(Float, nullable=False)              # 0.0 – 1.0

    def to_dict(self) -> dict:
               return {
            "id": self.id,
            "user_id": self.user_id,
            "text": self.text,
            "predicted_sentiment": self.predicted_sentiment,
            "confidence": self.confidence,
        }

    def __str__(self):
        return (
            f"SentimentEntity("
            f"id={self.id}, user_id={self.user_id}, "
            f"text={self.text[:30]}..., "
            f"predicted_sentiment={self.predicted_sentiment}, "
            f"confidence={self.confidence})"
        )

    __repr__ = __str__
