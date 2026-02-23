from dataclasses import dataclass
import logging
from app.db.repository import HistoryRepository
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO)


@dataclass
class HistoryService:
    """
    Service layer responsible for handling user-event interaction history.

    This service acts as an abstraction over the HistoryRepository and
    provides additional business logic such as collaborative filtering
    recommendations based on historical participation data.
    """

    repo: HistoryRepository

    def attend_event(self, user_id: int, event_id: int) -> dict:
        """
        Registers a user as attending a specific event.

        Args:
            user_id (int): Unique identifier of the user.
            event_id (int): Unique identifier of the event.

        Returns:
            dict: Persisted history record.
        """
        logging.info(f"[HistoryService] User {user_id} attends event {event_id}")
        return self.repo.add_history(user_id=user_id, event_id=event_id)

    def get_user_history(self, user_id: int) -> list[dict]:
        """
        Retrieves participation history for a specific user.

        Args:
            user_id (int): Unique identifier of the user.

        Returns:
            list[dict]: List of user-event interaction records.
        """
        logging.info(f"[HistoryService] Fetching history for user {user_id}")
        records = self.repo.get_user_history(user_id)
        return [rec.to_dict() for rec in records]

    def get_all_history(self) -> list[dict]:
        """
        Retrieves full participation history.

        This method can be used for analytics, collaborative filtering,
        or administrative purposes.

        Returns:
            list[dict]: List of all history records.
        """
        logging.info("[HistoryService] Fetching ALL history records")
        records = self.repo.get_all_history()
        return [rec.to_dict() for rec in records]

    def get_event_participants(self, event_id: int) -> list[int]:
        """
        Retrieves all user IDs participating in a specific event.

        Args:
            event_id (int): Unique identifier of the event.

        Returns:
            list[int]: List of user IDs.
        """
        logging.info(f"[HistoryService] Fetching participants for event {event_id}")
        records = self.repo.find_all()
        return [rec.user_id for rec in records if rec.event_id == event_id]

    def delete_all_history(self):
        """
        Deletes all participation history records.

        Warning:
            This operation removes all historical data permanently.
        """
        logging.warning("[HistoryService] Deleting ALL history records")
        self.repo.delete_all()

    def recommend_events(self, user_id: int) -> list[int]:
        """
        Recommends events using a simple collaborative filtering approach
        based on event co-occurrence.

        The algorithm:
        1. Builds a user–event interaction matrix (binary).
        2. Computes event co-occurrence matrix.
        3. Scores candidate events based on co-attendance frequency.
        4. Removes events already attended by the user.
        5. Returns top 5 recommended event IDs.

        Args:
            user_id (int): Unique identifier of the user.

        Returns:
            list[int]: List of recommended event IDs.
        """
        logging.info(
            f"\n================== [CF] START recommendation for user_id={user_id} ==================\n"
        )

        # 1) Fetch full interaction history
        history_records = self.repo.get_all_history()
        logging.info(f"[CF] All history records: {history_records}")

        if not history_records:
            logging.info("[CF] No history available — no recommendations")
            return []

        # 2) Convert history into Pandas DataFrame
        df = pd.DataFrame([
            {"user_id": h.user_id, "event_id": h.event_id}
            for h in history_records
        ])
        logging.info(f"\n[CF] History DataFrame:\n{df.to_string(index=False)}\n")

        # 3) Build user–event interaction matrix (binary)
        interaction_matrix = pd.crosstab(df["user_id"], df["event_id"])
        logging.info(f"[CF] User–event matrix before binarization:\n{interaction_matrix}\n")

        interaction_matrix = interaction_matrix.applymap(lambda x: 1 if x > 0 else 0)
        logging.info(f"[CF] User–event matrix (binary):\n{interaction_matrix}\n")

        # Ensure user exists in the matrix
        if user_id not in interaction_matrix.index:
            logging.info(f"[CF] User {user_id} not found in history → no recommendations")
            return []

        # 4) Identify events attended by the target user
        user_events = interaction_matrix.loc[user_id]
        user_events = user_events[user_events > 0].index.tolist()
        logging.info(f"[CF] User {user_id} attended events: {user_events}")

        if not user_events:
            logging.info(f"[CF] User {user_id} has no attended events → no recommendations")
            return []

        # 5) Compute event co-occurrence matrix
        co_matrix = interaction_matrix.T.dot(interaction_matrix)
        logging.info(
            f"[CF] Event co-occurrence matrix (before diagonal reset):\n{co_matrix}\n"
        )

        np.fill_diagonal(co_matrix.values, 0)
        logging.info(
            f"[CF] Event co-occurrence matrix (after diagonal reset):\n{co_matrix}\n"
        )

        # 6) Score events related to user's attended events
        scores = co_matrix[user_events].sum(axis=1)
        logging.info(
            f"[CF] Event scores related to {user_events}:\n{scores}\n"
        )

        # 7) Remove events already attended by the user
        scores = scores.drop(labels=user_events)
        logging.info(
            f"[CF] Event scores after removing attended events {user_events}:\n{scores}\n"
        )

        # 8) Sort and return top recommended events
        recommended = list(scores.sort_values(ascending=False).head(5).index)
        logging.info(f"[CF] Final recommendations for user {user_id}: {recommended}")
        logging.info(
            f"\n================== [CF] END recommendation for user_id={user_id} ==================\n"
        )

        return recommended