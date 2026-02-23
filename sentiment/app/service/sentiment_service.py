from dataclasses import dataclass
import logging
import os
import pickle
import re
import nltk

from nltk.stem import WordNetLemmatizer

from app.db.repository import SentimentRepository
from app.service.dto import SentimentDto

logging.basicConfig(level=logging.INFO)

# -------------------------------------------------------------------
# Load NLTK
# -------------------------------------------------------------------
nltk.download("wordnet")

lemmatizer = WordNetLemmatizer()

# -------------------------------------------------------------------
# Text cleaning — must match training EXACTLY
# -------------------------------------------------------------------
custom_stopwords = {
    'the','and','a','to','in','is','for','on','it','you','that','with','as',
    'was','at','be','by','this','which','or','from','but','are','have','an',
    'were','all','they','their','we','our','has','will'
}

def clean_text(text: str) -> str:
    text = re.sub(r"[^a-zA-Z\']", " ", text)
    text = text.lower()
    words = text.split()
    filtered = [lemmatizer.lemmatize(w) for w in words if w not in custom_stopwords]
    return " ".join(filtered)


# -------------------------------------------------------------------
# Load your trained sentiment model
# -------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "model", "ML_model", "sentiment_model"))

logging.info(f"[SentimentService] Loading sentiment_model from {MODEL_PATH}")

with open(MODEL_PATH, "rb") as f:
    sentiment_model = pickle.load(f)

logging.info("[SentimentService] Model loaded successfully.")


@dataclass
class SentimentService:
    """
    Sentiment microservice:
    - clean input text
    - run Naive Bayes classifier
    - compute confidence
    - save prediction in DB
    """

    repo: SentimentRepository

    # --------------------------------------------------------------
    # Analyze text
    # --------------------------------------------------------------
    def analyze_text(self, user_id: int, dto: SentimentDto) -> dict:
        logging.info(f"[SentimentService] Analyzing text for user_id={user_id}")

        # 1) Clean text exactly as during training
        cleaned = clean_text(dto.text)

        # 2) Predict class (0 or 1)
        predicted_label = sentiment_model.predict([cleaned])[0]

        # Map numerical label to string
        label_map = {
            0: "negative",
            1: "positive"
        }
        sentiment_text = label_map.get(predicted_label, "unknown")

        # 3) Predict confidence (probability score)
        if hasattr(sentiment_model, "predict_proba"):
            proba = sentiment_model.predict_proba([cleaned])[0]
            confidence = float(max(proba))
        else:
            logging.warning("[SentimentService] Model has no predict_proba; using confidence = 1.0")
            confidence = 1.0

        logging.info(f"[ML] Predicted sentiment = {sentiment_text}")
        logging.info(f"[ML] Confidence = {confidence}")

        # 4) Store result in DB
        saved = self.repo.save_sentiment(
            user_id=user_id,
            text=dto.text,
            predicted_sentiment=sentiment_text,  # <-- zapisujemy STRING
            confidence=confidence
        )

        return saved

    # --------------------------------------------------------------
    # Read one record
    # --------------------------------------------------------------
    def get_sentiment(self, sentiment_id: int) -> dict | None:
        entry = self.repo.get_sentiment_by_id(sentiment_id)
        return entry.to_dict() if entry else None

    # --------------------------------------------------------------
    # Read all
    # --------------------------------------------------------------
    def get_all(self) -> list[dict]:
        return [s.to_dict() for s in self.repo.get_all_sentiments()]

    # --------------------------------------------------------------
    # Delete
    # --------------------------------------------------------------
    def delete_sentiment(self, sentiment_id: int) -> bool:
        entry = self.repo.get_sentiment_by_id(sentiment_id)
        if not entry:
            return False
        self.repo.delete_sentiment(sentiment_id)
        return True
