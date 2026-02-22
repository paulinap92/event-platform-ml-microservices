from dataclasses import dataclass
import joblib
import pandas as pd
import logging
import os

from app.db.repository import EventsRepository
from app.service.dto import EventDto

logging.basicConfig(level=logging.INFO)

# -------------------------------------------------------------------
# Load ML artifacts once (Pipeline + LabelEncoder)
# -------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PIPELINE_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "model", "ML_model", "pipeline.pkl"))
ENCODER_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "model","ML_model", "label_encoder.pkl"))

with open(PIPELINE_PATH, "rb") as f:
    model_pipeline = joblib.load(f)

with open(ENCODER_PATH, "rb") as f:
    label_encoder = joblib.load(f)


@dataclass
class EventsService:
    """
    Core business logic for the Event Management microservice.

    Responsibilities:
    - Accept event data DTO
    - Run ML prediction (TF-IDF + MLP classifier)
    - Decode predicted category using LabelEncoder
    - Save event to the database
    - Retrieve existing events
    """

    repo: EventsRepository

    # --------------------------------------------------------------
    # Create event + ML prediction
    # --------------------------------------------------------------
    def add_event(self, organizer_id: int, dto: EventDto) -> dict:
        """
        Creates a new event, runs ML prediction based on title + description,
        decodes predicted class label, and stores everything in the database.
        """
        logging.info(f"[EventsService] Creating event for organizer_id={organizer_id}")

        # 1) DTO → dict
        event_dict = dto.to_dict()

        # 2) Prepare data (title + description)
        text = dto.title + " " + dto.description

        # 3) Predict numeric class
        predicted_encoded = model_pipeline.predict([text])[0]

        # 4) Decode numeric class → category label
        predicted_category = label_encoder.inverse_transform([predicted_encoded])[0]

        # event_dict["predicted_category"] = predicted_category

        logging.info(f"[ML] Encoded prediction = {predicted_encoded}")
        logging.info(f"[ML] Decoded category  = {predicted_category}")

        # 5) Save event
        saved = self.repo.save_event(
            organizer_id=organizer_id,
            event_data=event_dict,
            predicted_category=predicted_category
        )

        return saved

    # --------------------------------------------------------------
    # Read single event
    # --------------------------------------------------------------
    def get_event(self, event_id: int) -> dict | None:
        logging.info(f"[EventsService] Fetching event_id={event_id}")

        event = self.repo.get_event_by_id(event_id)
        return event.to_dict() if event else None

    # --------------------------------------------------------------
    # Read all events
    # --------------------------------------------------------------
    def get_events(self) -> list[dict]:
        logging.info("[EventsService] Fetching all events")
        return [e.to_dict() for e in self.repo.get_events()]

    # --------------------------------------------------------------
    # Delete event
    # --------------------------------------------------------------
    def delete_event(self, event_id: int) -> bool:
        logging.info(f"[EventsService] Deleting event_id={event_id}")

        event = self.repo.get_event_by_id(event_id)
        if not event:
            logging.info("[EventsService] Cannot delete; event not found.")
            return False

        self.repo.delete_event(event_id)
        return True
