from __future__ import annotations

from abc import ABC, abstractclassmethod
from dataclasses import dataclass
from datetime import date

from wordgame_bot.exceptions import InvalidDay, InvalidTiles

COMPLETED_TILES = ("🟩🟩🟩🟩🟩", "⬜⬜⬜⬜⬜", "⬛⬛⬛⬛⬛")


@dataclass
class GuessInfo(ABC):
    info: str
    creation_day: date
    day: int | None = None
    score: int | None = None

    def __post_init__(self):
        self.validate_format()
        self.parse()

    @property
    def valid_puzzle_days(self):
        todays_puzzle = (date.today() - self.creation_day).days
        yesterdays_puzzle = todays_puzzle - 1
        return (todays_puzzle, yesterdays_puzzle)

    @abstractclassmethod
    def validate_format(self):
        pass

    def parse(self):
        self.extract_day_and_score()
        self.day = self.parse_day()
        self.score = self.parse_score()

    def validate_day(self) -> None:
        try:
            day = int(self.day)
            if day not in self.valid_puzzle_days:
                raise InvalidDay(day, self.valid_puzzle_days)
        except ValueError:
            raise InvalidDay(self.day)

    @abstractclassmethod
    def extract_day_and_score(self):
        pass

    @abstractclassmethod
    def parse_day(self):
        pass

    @abstractclassmethod
    def parse_score(self):
        pass


@dataclass
class Guesses:
    guesses: list[str]
    incorrect_guess_score: int
    correct_answer: str = "🟩🟩🟩🟩🟩"
    valid_tiles: str = "🟨🟩⬜⬛"
    tiles_per_guess: int = 5

    def __post_init__(self):
        self.guesses = [guess.strip() for guess in self.guesses]
        self.validate_guesses()

    @property
    def correct_guess(self):
        try:
            return self.guesses.index(self.correct_answer) + 1
        except ValueError:
            return self.incorrect_guess_score

    def validate_guesses(self):
        for guess in self.guesses:
            self.validate_guess(guess)

    def validate_guess(self, guess):
        valid_amount_of_tiles = len(guess) == self.tiles_per_guess
        valid_tiles = all(tile in self.valid_tiles for tile in guess)
        if not (valid_amount_of_tiles and valid_tiles):
            raise InvalidTiles(guess)
