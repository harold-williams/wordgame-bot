from __future__ import annotations

from dataclasses import dataclass


class ParsingError(Exception):

    def __init__(self, message: str, *args: object) -> None:
        self.message = message
        super().__init__(*args)

    def __str__(self) -> str:
        return self.message

    def __repr__(self) -> str:
        return f"{self}"


@dataclass
class InvalidTiles(ParsingError):
    tiles: list[str]

    def __post_init__(self) -> None:
        message = f"Incorrect tile format: {self.tiles}"
        super().__init__(message)


class InvalidDay(ParsingError):
    day: int | str
    valid_days: tuple[int, int] | None

    def __post_init__(self) -> None:
        if self.valid_days is not None: 
            self.message = f"Day - {self.day} - is not in valid puzzle days: {self.valid_days}"
        else:
            self.message = f"Invalid day provided: {self.day}"
        super().__init__(self.message)


class InvalidScore(ParsingError):

    def __init__(
        self,
        score: str,
        *args: object
    ) -> None:
        message = f"Invalid score provided: {score}"
        super().__init__(message, *args)


class InvalidFormatError(ParsingError):

    def __init__(
        self,
        user_input: str,
        *args: object
    ) -> None:
        message = f"User input incorrectly formatted: {user_input}"
        super().__init__(message, *args)
