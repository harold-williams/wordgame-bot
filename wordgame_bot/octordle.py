from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date
import re

from wordgame_bot.attempt import Attempt, AttemptParser
from wordgame_bot.exceptions import InvalidFormatError, InvalidScore, ParsingError
from wordgame_bot.guess import GuessInfo, Guesses

INCORRECT_GUESS_SCORE = 15
SCORE_MAP = {
    "🔟": 10,
    "🕚": 11,
    "🕛": 12,
    "🕐": 13,
}

@dataclass
class OctordleAttemptParser(AttemptParser):
    attempt: str
    error: str = "" # TODO

    def parse(self) -> OctordleAttempt:
        try:
            return self.parse_attempt()
        except ParsingError as e:
            self.handle_error(e)

    def parse_attempt(self):
        lines = self.get_lines()
        info = OctordleGuessInfo("\n".join(lines[0:5]))
        words = self.extract_words(lines[5:])
        for word_num, word in enumerate(words):
            if info.scores[word_num] != word.correct_guess:
                raise InvalidScore(info.score) # TODO This should be moved inside attempt as not a parsing error is an attempt error.
        return OctordleAttempt(info, words)

    def get_lines(self):
        lines = [line.strip() for line in self.attempt.split("\n")]
        if "octordle.com" in lines:
            lines.remove("octordle.com")
        if len(lines) <= 28 or len(lines) > 60:
            raise InvalidFormatError(self.attempt)
        return lines

    def extract_words(self, all_words):
        guess_list = []
        word_pairs = "\n".join(all_words).split("\n\n")
        for pair in word_pairs:
            for word in self.split_words(pair):
                guess_list.append(Guesses(word, INCORRECT_GUESS_SCORE))

        return guess_list

    def split_words(self, word_pair):
        left_word = []
        right_word = []
        for guesses in word_pair.split("\n"):
            left_guess, right_guess = guesses.split(" ")
            left_word.append(left_guess)
            right_word.append(right_guess)
        return [left_word, right_word]

    def handle_error(self, error: ParsingError):
        logging.warning(f"{error!r}")
        self.errorr = str(error.message)
        raise error


@dataclass
class OctordleGuessInfo(GuessInfo):
    scores: list = field(default_factory=list)
    creation_day: date = date(2022, 1, 24)
    valid_format = re.compile("^Daily Octordle #[0-9]+\n[1-9🔟🕚🕛🕐🟥][1-9🔟🕚🕛🕐🟥]\n[1-9🔟🕚🕛🕐🟥][1-9🔟🕚🕛🕐🟥]\n[1-9🔟🕚🕛🕐🟥][1-9🔟🕚🕛🕐🟥]\n[1-9🔟🕚🕛🕐🟥][1-9🔟🕚🕛🕐🟥]$")

    @property
    def bonus_points(self):
        all_correct = all(score != INCORRECT_GUESS_SCORE for score in self.scores)
        return -1 if all_correct else 0 # TODO THIS SHOULD BE MOVED TO QUORDLE ATTEMPT AS OTHERWISE INVERSION + WHY IT IS HERE IS CONFUSING

    def validate_format(self):
        self.sanitise_info()
        if self.valid_format.match(self.info) is None:
            raise InvalidFormatError(self.info)

    def sanitise_info(self):
        self.info = self.info.strip()
        for bad_char in ('\ufe0f', '\u20e3'):
            self.info = self.info.replace(bad_char, '')
        print(self.info)

    def extract_day_and_score(self):
        info_parts = self.info.split('\n')
        self.day = info_parts[0].split('#')[1]
        self.scores = list("".join(info_parts[1:]))

    def parse_day(self):
        self.validate_day()
        return int(self.day)

    def parse_score(self):
        self.validate_scores()
        for score_num, score in enumerate(self.scores):
            if score == "🟥":
                self.scores[score_num] = INCORRECT_GUESS_SCORE
            else:
                score_value = SCORE_MAP.get(score)
                if score_value is None:
                    score_value = int(score)
                self.scores[score_num] = score_value
        print(self.bonus_points)
        return sum(self.scores) + self.bonus_points

    def validate_scores(self):
        if len(self.scores) != 8:
            raise InvalidScore("Must supply 8 scores")
        prev_scores = set()
        for score in self.scores:
            try:
                assert len(score) == 1
                assert score in "123456789🔟🕚🕛🕐🟥"
                if score != "🟥":

                    assert score not in prev_scores
                    prev_scores.add(score)
            except AssertionError:
                raise InvalidScore(score)


@dataclass
class OctordleAttempt(Attempt):
    @property
    def maxscore(self):
        return 120

    @property
    def score(self):
        return self.maxscore - self.info.score

    @property
    def gamemode(self):
        return "O"
