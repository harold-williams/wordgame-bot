from __future__ import annotations

from abc import ABC, abstractclassmethod
from dataclasses import dataclass

from wordgame_bot.exceptions import InvalidTiles

COMPLETED_TILES = ('🟩🟩🟩🟩🟩', '⬜⬜⬜⬜⬜', '⬛⬛⬛⬛⬛')


@dataclass
class GuessInfo(ABC):
    info: str
    day: int | None = None 
    score: int | None = None 

    def __post_init__(self):
        self.validate_format()
        self.parse()

    @abstractclassmethod
    def validate_format(self):
        pass

    def parse(self):
        self.extract_day_and_score()
        self.day = self.parse_day()
        self.score = self.parse_score()

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

    def __post_init__(self):
        self.guesses = [guess.strip() for guess in self.guesses]
        self.validate_guesses()

    @property
    def correct_guess(self):
        try:
            return self.guesses.index('🟩🟩🟩🟩🟩') + 1
        except ValueError:
            return self.incorrect_guess_score

    def validate_guesses(self):
        for guess in self.guesses:
            self.validate_guess(guess)

    @staticmethod
    def validate_guess(guess):
        valid_amount_of_tiles = len(guess) == 5
        valid_tiles = all(tile in '🟨🟩⬜⬛' for tile in guess)
        if not (valid_amount_of_tiles and valid_tiles):
            raise InvalidTiles(guess)