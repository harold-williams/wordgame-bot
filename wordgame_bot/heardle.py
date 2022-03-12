from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from datetime import date

from wordgame_bot.attempt import Attempt, AttemptParser
from wordgame_bot.exceptions import InvalidFormatError, ParsingError
from wordgame_bot.guess import Guesses, GuessInfo

INCORRECT_GUESS_SCORE = 8


@dataclass
class HeardleAttemptParser(AttemptParser):
    attempt: str
    error: str = ""  # TODO

    def parse(self) -> HeardleAttempt:
        try:
            return self.parse_attempt()
        except ParsingError as e:
            self.handle_error(e)

    def parse_attempt(self) -> HeardleAttempt:
        lines = self.get_lines()
        info = HeardleGuessInfo(lines[0])
        guesses = Guesses(lines[1][1:], INCORRECT_GUESS_SCORE, "🟩", "🟩🟥⬜️", 1)
        info.score = guesses.correct_guess
        return HeardleAttempt(info, guesses)

    def get_lines(self) -> list[str]:
        lines = [
            line.strip()
            for line in self.attempt.strip().split("\n")
            if line.strip()
        ]
        if len(lines) <= 1 or len(lines) > 3:
            raise InvalidFormatError(self.attempt)
        return lines

    def handle_error(self, error: ParsingError):
        logging.warning(f"{error!r}")
        self.error = str(error.message)
        raise error


@dataclass
class HeardleGuessInfo(GuessInfo):
    creation_day: date = date(2022, 2, 25)
    valid_format = re.compile("^#Heardle #[0-9]+$")

    def validate_format(self):
        self.info = self.info.strip()
        if self.valid_format.match(self.info) is None:
            raise InvalidFormatError(self.info)

    def extract_day_and_score(self):
        info_parts = self.info.split(" ")
        self.day = info_parts[1][1:]
        self.score = None

    def parse_day(self) -> int:
        self.validate_day()
        return int(self.day)

    def parse_score(self) -> int:
        return None


@dataclass
class HeardleAttempt(Attempt):
    @property
    def maxscore(self):
        return 10

    @property
    def gamemode(self):
        return "H"
