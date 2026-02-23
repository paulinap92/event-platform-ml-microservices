from dataclasses import dataclass
from typing import Optional, Self


@dataclass
class RecommendationSurveyDto:

    age: int
    gender: str
    city_size: str
    marital_status: str
    children: str
    country_of_origin: str
    occupation: str
    education: str
    income: int
    hobbies: str
    personality_type: str


    event_preference: Optional[str] = None

    def to_dict(self) -> dict[str, str | int | None]:

        return {
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

    @classmethod
    def from_dict(cls, data: dict[str, str | int]) -> Self:

        return cls(
            age=int(data["age"]),
            gender=data["gender"],
            city_size=data["city_size"],
            marital_status=data["marital_status"],
            children=data["children"],
            country_of_origin=data["country_of_origin"],
            occupation=data["occupation"],
            education=data["education"],
            income=int(data["income"]),
            hobbies=data["hobbies"],
            personality_type=data["personality_type"],
            event_preference=data.get("event_preference")
        )
