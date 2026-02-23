from dataclasses import dataclass
import cloudpickle
import pandas as pd
import logging

from app.db.repository import RecommendationsRepository
from app.service.dto import RecommendationSurveyDto

logging.basicConfig(level=logging.INFO)

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "..", "ML_model", "pipeline.pkl")
MODEL_PATH = os.path.abspath(MODEL_PATH)


# -------------------------------------------------------------------
# Load the ML model once at service startup (module import time).
# This avoids reloading the pipeline on every request.
# -------------------------------------------------------------------
with open(MODEL_PATH, "rb") as f:
    model_pipeline = cloudpickle.load(f)


@dataclass
class RecommendationsService:
    """
    Service responsible for handling recommendation surveys.

    The service:
    - Accepts a survey DTO from the user.
    - Converts survey inputs into a DataFrame compatible with the ML pipeline.
    - Predicts the user's preferred event category.
    - Persists the enriched survey (including predicted preference) via repository.
    """

    repo: RecommendationsRepository()

    def add_survey(self, user_id: int, dto: RecommendationSurveyDto) -> dict:
        """
        Processes and stores a user survey, enriched with ML prediction.

        Steps:
        1. Convert DTO to dict for persistence.
        2. Build a single-row DataFrame expected by the ML pipeline.
        3. Predict the preferred event category.
        4. Save survey + prediction in the repository.

        Args:
            user_id (int): Unique identifier of the user.
            dto (RecommendationSurveyDto): Survey payload.

        Returns:
            dict: Persisted survey record including the predicted preference.
        """
        logging.info(f"[RecommendationsService] Processing survey for user_id={user_id}")

        survey_dict = dto.to_dict()

        # Build a single-row DataFrame with the exact feature names expected by the pipeline.
        df = pd.DataFrame([{
            "Age": dto.age,
            "Gender": dto.gender,
            "City_Size": dto.city_size,
            "Marital_Status": dto.marital_status,
            "Children": dto.children,
            "Country_of_Origin": dto.country_of_origin,
            "Occupation": dto.occupation,
            "Education": dto.education,
            "Income": dto.income,
            "Hobbies": dto.hobbies,
            "Personality_Type": dto.personality_type
        }])

        predicted_category = model_pipeline.predict(df)[0]
        survey_dict["event_preference"] = predicted_category

        logging.info(f"[ML] Predicted category for user_id={user_id}: {predicted_category}")

        saved = self.repo.save_user_survey(user_id, survey_dict)
        return saved

    def get_survey(self, user_id: int) -> dict | None:
        """
        Retrieves a previously saved survey for a given user.

        Args:
            user_id (int): Unique identifier of the user.

        Returns:
            dict | None: Survey record as a dictionary if found, otherwise None.
        """
        logging.info(f"[RecommendationsService] Reading survey for user_id={user_id}")

        survey = self.repo.get_survey_by_user(user_id)
        if survey:
            return survey.to_dict()

        logging.info(f"[RecommendationsService] No survey found for user_id={user_id}")
        return None