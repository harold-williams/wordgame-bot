from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date
import re

from wordgame_bot.attempt import Attempt, AttemptParser
from wordgame_bot.exceptions import InvalidDay, InvalidFormatError, InvalidScore, ParsingError
from wordgame_bot.guess import GuessInfo, Guesses

INCORRECT_GUESS_SCORE = 12

@dataclass
class QuordleAttemptParser(AttemptParser):
    attempt: str
    error: str = "" # TODO

    def parse(self) -> QuordleAttempt:
        try:
            return self.parse_attempt()
        except ParsingError as e:
            self.handle_error(e)

    def parse_attempt(self):
        lines = self.get_lines()
        info = QuordleGuessInfo("\n".join(lines[0:3]))
        words = self.extract_words(lines[3:])
        for word_num, word in enumerate(words):
            if info.scores[word_num] != word.correct_guess:
                raise InvalidScore(info.score) # TODO This should be moved inside attempt as not a parsing error is an attempt error.
        return QuordleAttempt(info, words)

    def get_lines(self):
        lines = [line.strip() for line in self.attempt.split("\n")]
        if "quordle.com" in lines:
            lines.remove("quordle.com")
        if len(lines) <= 9 or len(lines) > 23:
            raise InvalidFormatError(self.attempt)
        return lines

    def extract_words(self, all_words):
        guess_list = []
        seperator = all_words.index("")
        first_words = all_words[:seperator]
        second_words = all_words[seperator+1:]
        for words in (first_words, second_words):
            for word in self.split_words(words):
                guess_list.append(Guesses(word, INCORRECT_GUESS_SCORE))

        return guess_list

    def split_words(self, combined_words):
        left_word = []
        right_word = []
        for guesses in combined_words:
            left_guess, right_guess = guesses.split(" ")
            left_word.append(left_guess)
            right_word.append(right_guess)
        return [left_word, right_word]

    def handle_error(self, error: ParsingError):
        logging.warning(f"{error!r}")
        self.errorr = str(error.message)
        raise error


@dataclass
class QuordleGuessInfo(GuessInfo):
    scores: list = field(default_factory=list)
    creation_day: date = date(2022, 1, 24)
    valid_format = re.compile("^Daily Quordle #[0-9]+\n[1-9🟥][1-9🟥]\n[1-9🟥][1-9🟥]$")

    @property
    def bonus_points(self):
        all_correct = all(score != '🟥' for score in self.scores)
        return -1 if all_correct else 0 # TODO THIS SHOULD BE MOVED TO QUORDLE ATTEMPT AS OTHERWISE INVERSION + WHY IT IS HERE IS CONFUSING

    def validate_format(self):
        self.sanitise_info()
        if self.valid_format.match(self.info) is None:
            raise InvalidFormatError(self.info)

    def sanitise_info(self):
        self.info = self.info.strip()
        for bad_char in ('\ufe0f', '\u20e3'):
            self.info = self.info.replace(bad_char, '')

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
                self.scores[score_num] = int(score)

        return sum(self.scores) + self.bonus_points

    def validate_scores(self):
        if len(self.scores) != 4:
            raise InvalidScore("Must supply 4 scores")
        prev_scores = set()
        for score in self.scores:
            try:
                assert len(score) == 1
                assert score in "123456789🟥"
                if score != "🟥":
                    print(prev_scores)
                    assert score not in prev_scores
                    prev_scores.add(score)
            except AssertionError:
                raise InvalidScore(score)


@dataclass
class QuordleAttempt(Attempt):
    @property
    def maxscore(self):
        return 50

    @property
    def score(self):
        return self.maxscore - self.info.score

    @property
    def gamemode(self):
        return "Q"
