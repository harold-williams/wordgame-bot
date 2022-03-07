from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date
import re

from wordgame_bot.attempt import Attempt, AttemptParser
from wordgame_bot.exceptions import InvalidDay, InvalidFormatError, InvalidScore, ParsingError
from wordgame_bot.guess import GuessInfo, Guesses

INCORRECT_GUESS_SCORE = 8

@dataclass
class WordleAttemptParser(AttemptParser):
    attempt: str
    error: str = "" # TODO

    def parse(self) -> WordleAttempt:
        try:
            return self.parse_attempt()
        except ParsingError as e:
            self.handle_error(e)

    def parse_attempt(self):
        lines = self.get_lines()
        info = WordleGuessInfo(lines[0])
        guesses = Guesses(lines[1:], INCORRECT_GUESS_SCORE)
        if info.score != guesses.correct_guess:
            raise InvalidScore(info.score) # TODO This should be moved inside attempt as not a parsing error is an attempt error.
        return WordleAttempt(info, guesses)

    def get_lines(self):
        lines = [line.strip() for line in self.attempt.split("\n") if line.strip()]
        if len(lines) <= 1 or len(lines) > 7:
            raise InvalidFormatError(self.attempt)
        return lines

    def handle_error(self, error: ParsingError):
        logging.warning(f"{error!r}")
        self.errorr = str(error.message)
        raise error


@dataclass
class WordleGuessInfo(GuessInfo):
    creation_day: date = date(2021, 6, 19)
    valid_format = re.compile("^Wordle [0-9]+ [1-6X]\/6$")

    def validate_format(self):
        self.info = self.info.strip()
        if self.valid_format.match(self.info) is None:
            raise InvalidFormatError(self.info)

    def extract_day_and_score(self):
        info_parts = self.info.split(' ')
        self.day = info_parts[1]
        self.score = info_parts[2].split('/')[0]

    def parse_day(self):
        self.validate_day()
        return int(self.day)

    def parse_score(self):
        self.validate_score()
        if self.score == "X":
            return INCORRECT_GUESS_SCORE

        return int(self.score)

    def validate_score(self):
        try:
            assert len(self.score) == 1
            assert self.score in '123456X'
        except AssertionError:
            raise InvalidScore(self.score)


@dataclass
class WordleAttempt(Attempt):
    @property
    def score(self):
        return 10 - self.info.score

    @property
    def gamemode(self):
        return "W"
