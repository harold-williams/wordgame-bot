from __future__ import annotations

import logging
from collections import namedtuple
from dataclasses import dataclass
from datetime import date

from wordgame_bot.attempt import AttemptParser
from wordgame_bot.exceptions import InvalidDay, InvalidFormatError, InvalidScore, ParsingError
from wordgame_bot.guess import GuessInfo, Guesses

INCORRECT_GUESS_SCORE = 8
MAX_TILES_PER_WORD = 6
COMPLETED_TILES = ('🟩🟩🟩🟩🟩', '⬜⬜⬜⬜⬜')


class WordleGuessInfo(GuessInfo):

    @property
    def valid_puzzle_days(self):
        creation_day = date(2021, 6, 19)
        todays_puzzle = (date.today() - creation_day).days
        yesterdays_puzzle = todays_puzzle - 1
        return (todays_puzzle, yesterdays_puzzle)

    def validate_format(self):
        self.info = self.info.strip()
        try:
            assert self.info.startswith("Wordle")
            info_parts = self.info.split(' ')
            assert len(info_parts) == 3
            assert self.info.endswith("/6")
        except AssertionError:
            raise InvalidFormatError(self.info)

    def extract_day_and_score(self):
        info_parts = self.info.split(' ')
        self.day = info_parts[1]
        self.score = info_parts[2].split('/')[0]

    def parse_day(self):
        self.validate_day()
        return int(self.day)

    def validate_day(self):
        try:
            day = int(self.day)
            if day not in self.valid_puzzle_days:
                raise InvalidDay(day, self.valid_puzzle_days)
        except TypeError:
            raise InvalidDay(self.day)

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
class WordleAttempt:
    info: WordleGuessInfo
    guesses: Guesses

    @property
    def score(self):
        return 10 - self.info.score


class WordleAttemptParser(AttemptParser):
    def __init__(self, attempt: str):
        self.errors: list[str] = []
        self.attempt: str = attempt

    def error_message(self):
        return (
            f"Invalid Attempt: {self.errors}",
        )

    def handle_error(self, error: ParsingError):
        logging.warning(f"{error!r}")
        self.errors.append(str(error.message))
        raise error

    def parse(self) -> WordleAttempt:
        try:
            return self.parse_attempt()
        except ParsingError as e:
            self.handle_error(e)

    def parse_attempt(self):
        lines = self.get_lines()
        info = WordleGuessInfo(lines[0])
        guesses = Guesses(lines[1:], INCORRECT_GUESS_SCORE)
        print(guesses.correct_guess)
        print(info.score)
        print(type(guesses.correct_guess))
        print(type(info.score))
        if info.score != guesses.correct_guess:
            raise InvalidScore(info.score)
        return WordleAttempt(info, guesses)

    def get_lines(self):
        lines = [line.strip() for line in self.attempt.split("\n") if line.strip()]
        if len(lines) <= 1 or len(lines) > 7:
            raise InvalidFormatError(self.attempt)

        return lines

if __name__ == "__main__":
#     attempt1 = """
# Wordle 248 4/6

# ⬛⬛⬛🟨⬛
# 🟨🟨⬛🟩⬛
# ⬛🟩🟩🟩🟨
# 🟩🟩🟩🟩🟩
# """

#     attempt2 = """
# Wordle 248 X/6

# 🟩⬜⬜🟩⬜
# 🟩⬜⬜🟩⬜
# 🟩⬜⬜🟩⬜
# ⬜⬜⬜🟨⬜
# ⬜⬜⬜⬜⬜
# ⬜⬜⬜⬜⬜
# """

#     attempt3 = """
# Wordle 247 2/6

# ⬛⬛⬛⬛⬛
# ⬛⬛⬛⬛🟨
# ⬛🟨🟩🟨⬛
# 🟩🟩🟩🟩🟩
# """

    attempt4 = """
Wordle 251 4/6

⬛⬛⬛🟨⬛
⬛🟨⬛⬛⬛
🟩🟩🟨⬛⬛
🟩🟩🟩🟩🟩
"""

    attempt = WordleAttemptParser(attempt4)
    details = attempt.parse()
    print(details)