from __future__ import annotations

from dataclasses import dataclass


class ParsingError(Exception):
    def __init__(self, message: str, *args: object) -> None:
        self.message = message
        super().__init__(message, *args)

    def __str__(self) -> str:
        return str(self.message)

    def __repr__(self) -> str:
        return str(self.message)  # TODO - Improve repr format


@dataclass
class InvalidTiles(ParsingError):
    tiles: list[str]

    def __post_init__(self) -> None:
        self.message = f"Incorrect tile format: {self.tiles}"
        super().__init__(self.message)


@dataclass
class InvalidDay(ParsingError):
    day: int | str
    valid_days: tuple[int, int] | None = None

    def __post_init__(self) -> None:
        if self.valid_days is not None:
            self.message = (
                f"Day - {self.day} - is not in valid puzzle days: {self.valid_days}"
            )
        else:
            self.message = f"Invalid day provided: {self.day}"
        super().__init__(self.message)


@dataclass
class InvalidScore(ParsingError):
    score: int | None

    def __post_init__(self) -> None:
        self.message = f"Invalid score provided: {self.score}"
        super().__init__(self.message)


@dataclass
class InvalidFormatError(ParsingError):
    user_input: str

    def __post_init__(self) -> None:
        self.message = f"User input incorrectly formatted: {self.user_input}"
        super().__init__(self.message)
