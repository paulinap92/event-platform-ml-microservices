from dataclasses import dataclass
from typing import Self


@dataclass
class EventDto:
    """
    DTO representing event input data used for creating or updating events.
    It also supports the ML-predicted category for the event.
    """

    title: str
    description: str
    location: str
    date: str

    def to_dict(self) -> dict[str, str | None]: # pragma: no cover
        """
        Converts the DTO into a dictionary representation,
        used by repositories and ML pipelines.
        """
        return {
            "title": self.title,
            "description": self.description,
            "location": self.location,
            "date": self.date
        }

    @classmethod
    def from_dict(cls, data: dict[str, str | None]) -> Self: # pragma: no cover
        """
        Creates a DTO instance from a dictionary,
        typically used when retrieving data from the database.
        """
        return cls(
            title=data["title"],
            description=data["description"],
            location=data["location"],
            date=data["date"]
        )
