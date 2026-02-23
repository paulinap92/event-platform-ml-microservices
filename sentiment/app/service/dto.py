from dataclasses import dataclass
from typing import Self


@dataclass
class SentimentDto:

    text: str

    def to_dict(self) -> dict[str, str]:

        return {
            "text": self.text
        }

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> Self:

        return cls(
            text=data["text"]
        )
