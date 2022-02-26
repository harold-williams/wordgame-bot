
from collections import namedtuple
from datetime import date

from wordgame_bot.attempt import AttemptParser

INCORRECT_GUESS_SCORE = 12
MAX_TILES_PER_WORD = 9
UNICODE_STRING_1 = '\ufe0f'
UNICODE_STRING_2 = '\u20e3'
COMPLETED_TILES = ('🟩🟩🟩🟩🟩', '⬛⬛⬛⬛⬛')

AttemptStrings = namedtuple("AttemptStrings", "day_string score_string guess_list")
QuordleAttempt = namedtuple("Attempt", "day score guesses num_correct")

class InvalidDay(Exception):
    pass

class Guess():
    def __init__(self, tiles, score) -> None:
        self.tiles = tiles
        if score != '🟥':
            self.score = int(score)
        else:
            self.score = INCORRECT_GUESS_SCORE

    def is_valid(self):
        try:
            guessed_row = self.tiles.index('🟩🟩🟩🟩🟩') + 1
            return self.score == guessed_row
        except ValueError:
            return self.score == INCORRECT_GUESS_SCORE

class QuordleAttemptParser(AttemptParser):
    def __init__(self, attempt: str):
        self.errors = []
        self.attempt = attempt
        self.attempt_details: QuordleAttempt | None = None

    # def parse(self) -> WordleAttempt:
    #     try:
    #         return self.parse_attempt()
    #     except ParsingError as e:
    #         self.handle_error(e)

    def parse(self) -> QuordleAttempt:
        try:
            attempt = self.attempt
            attempt_strings = self.split_attempt(attempt)
            day = self.get_day(attempt_strings.day_string)
            num_correct = self.get_correct(attempt_strings.score_string)
            score = self.get_score(attempt_strings.score_string)
            if num_correct == 4:
                score -= 1
            score = 50 - score
            guesses = self.get_guesses(attempt_strings)
            self.attempt_details = QuordleAttempt(day, score, guesses, num_correct)
        except AssertionError as e:
            raise

    def validate_guesses(self):
        if not self.errors or self.attempt_details:
            scores = set()
            try:
                assert isinstance(self.attempt_details, QuordleAttempt)
                assert len(self.attempt_details.guesses) == 4
                for i, guess in enumerate(self.attempt_details.guesses):
                    assert guess.is_valid()
                    if guess.score != INCORRECT_GUESS_SCORE:
                        scores.add(guess.score)
                    else:
                        scores.add(guess.score + i)
                self.assert_unique_scores(scores)
            except AssertionError:
                if not self.errors:
                    self.errors.append("Tiles do not match scores")
                return

    def validate_parsing(self, attempt_values: AttemptStrings):
        try:
            assert "Daily Quordle" in attempt_values.day_string
            assert len(attempt_values.score_string) == 4
            for score_string in attempt_values.score_string:
                for character in score_string:
                    assert character in '🟥123456789'
            assert len(attempt_values.guess_list) == 4
            for guess in attempt_values.guess_list:
                assert len(guess) > 0 and len(guess) <= MAX_TILES_PER_WORD
                for tiles in guess:
                    assert all(tile in '🟨🟩⬜⬛' for tile in tiles)
        except AssertionError as e:
            self.errors.append("Message format not supported")
            raise

    def assert_unique_scores(self, scores):
        try:
            assert len(scores) == 4
        except AssertionError as e:
            self.errors.append("You can't guess two words with one guess you fucking moron.")
            raise

    def split_attempt(self, attempt: str):
        lines = [line.strip() for line in attempt.split("\n") if line.strip()]
        scores = self.parse_scores(lines[1:3])
        attempt_values = AttemptStrings(
            lines[0],
            scores,
            self.parse_tiles(lines[4:]),
        )
        self.validate_parsing(attempt_values)
        return attempt_values

    def parse_scores(self, lines: list):
        stripped_lines = [line.replace('\ufe0f', '').replace('\u20e3', '') for line in lines]
        scores = ''.join(stripped_lines)
        return scores

    def parse_tiles(self, tiles):
        words = []
        first_tile_list = []
        second_tile_list = []
        word_len = 0

        for tile_string in tiles:
            assert len(words) < 4
            word_len += 1
            first_tiles, second_tiles = tile_string.split(' ')
            first_tile_list.append(first_tiles)
            second_tile_list.append(second_tiles)

            if first_tiles in COMPLETED_TILES and second_tiles in COMPLETED_TILES:
                words.append(first_tile_list)
                words.append(second_tile_list)
                first_tile_list = []
                second_tile_list = []
                word_len = 0

            elif (word_len) % MAX_TILES_PER_WORD == 0:
                words.append(first_tile_list)
                words.append(second_tile_list)
                first_tile_list = []
                second_tile_list = []
                word_len = 0

        return words

    
    def get_guesses(self, attempt_values: AttemptStrings):
        guesses = []
        guess_details = zip(attempt_values.guess_list, attempt_values.score_string)
        for details in guess_details:
            guesses.append(Guess(*details))
        return guesses

    def extract_day(self, line: str):
        try:
            _, day = line.split("#")
            return int(day)
        except TypeError as e:
            raise InvalidDay
    
    def validate_day(self, puzzle_day: int):
        creation_day = date(2022, 1, 24)
        todays_puzzle = (date.today() - creation_day).days
        yesterdays_puzzle = todays_puzzle - 1
        if puzzle_day not in (todays_puzzle, yesterdays_puzzle):
            return False
        return True

    def get_day(self, day_string: str):
        attempt_day = self.extract_day(day_string)
        if self.validate_day(attempt_day):
            return attempt_day
        raise InvalidDay

    def extract_score(self, score: str):
        if score == '🟥':
            return INCORRECT_GUESS_SCORE
        else:
            return int(score)

    def get_score(self, score_string: str):
        score_tally = 0
        for score in score_string:
            score_tally += self.extract_score(score)
        return score_tally
    
    def get_correct(self, score_string: str):
        return 4 - score_string.count('🟥')


if __name__ == "__main__":
    attempt1 = """
Daily Quordle #29
6️⃣9️⃣
🟥8️⃣
quordle.com
⬜⬜⬜🟨⬜ ⬜⬜⬜⬜🟨
🟨🟨⬜⬜⬜ ⬜🟨⬜🟨⬜
⬜⬜🟨⬜⬜ ⬜🟩⬜⬜⬜
⬜⬜🟨⬜⬜ ⬜⬜⬜⬜🟩
🟨🟨🟩🟩🟨 ⬜⬜⬜🟨⬜
🟩🟩🟩🟩🟩 ⬜⬜⬜🟨⬜
⬛⬛⬛⬛⬛ ⬜⬜⬜⬜🟨
⬛⬛⬛⬛⬛ ⬜🟨⬜🟨⬜
⬛⬛⬛⬛⬛ 🟩🟩🟩🟩🟩

⬜⬜🟨⬜⬜ ⬜⬜⬜🟨⬜
⬜🟨⬜⬜🟨 ⬜🟨🟨🟨⬜
⬜⬜⬜⬜⬜ ⬜⬜⬜⬜⬜
⬜⬜⬜🟨⬜ ⬜🟩⬜⬜⬜
⬜⬜⬜🟨⬜ ⬜🟨⬜🟩⬜
⬜⬜⬜🟨⬜ 🟨⬜⬜🟩⬜
⬜⬜⬜⬜⬜ 🟩🟨⬜🟨⬜
⬜⬜⬜🟨⬜ 🟩🟩🟩🟩🟩
⬜⬜🟩⬜⬜ ⬛⬛⬛⬛⬛
"""
    
    attempt2 = """
    Daily Quordle #28
5️⃣6️⃣
8️⃣7️⃣
quordle.com
🟩🟨⬜⬜🟨 ⬜⬜🟨⬜🟨
⬜🟨🟩⬜⬜ ⬜🟨⬜⬜⬜
⬜⬜⬜🟨⬜ ⬜⬜⬜⬜🟨
🟨⬜⬜🟩⬜ ⬜🟩🟨🟩🟨
🟩🟩🟩🟩🟩 ⬜⬜⬜🟩⬜
⬛⬛⬛⬛⬛ 🟩🟩🟩🟩🟩

⬜⬜⬜⬜🟨 ⬜⬜⬜⬜⬜
⬜🟩⬜⬜🟩 ⬜⬜⬜🟩⬜
⬜⬜⬜🟩⬜ ⬜⬜⬜⬜⬜
⬜⬜⬜🟨⬜ 🟩⬜⬜⬜⬜
⬜🟨⬜🟨⬜ ⬜⬜⬜⬜🟨
⬜⬜⬜🟨⬜ ⬜⬜⬜⬜🟩
⬜⬜🟨⬜⬜ 🟩🟩🟩🟩🟩
🟩🟩🟩🟩🟩 ⬛⬛⬛⬛⬛
"""

    attempt3 = """
Daily Quordle #30
4️⃣🟥
5️⃣8️⃣
quordle.com
🟨⬜⬜🟩🟩 ⬜⬜⬜⬜🟨
⬜🟨⬜⬜🟨 🟩🟨⬜🟨🟩
🟩🟩⬜⬜⬜ ⬜🟨⬜⬜🟨
🟩🟩🟩🟩🟩 ⬜🟨⬜⬜🟨
⬛⬛⬛⬛⬛ ⬜⬜⬜⬜⬜
⬛⬛⬛⬛⬛ ⬜🟩🟨🟩⬜
⬛⬛⬛⬛⬛ ⬜🟨🟨⬜⬜
⬛⬛⬛⬛⬛ ⬜🟨🟨⬜⬜
⬛⬛⬛⬛⬛ 🟩🟩⬜🟩🟩

🟨⬜⬜⬜⬜ ⬜⬜⬜⬜🟨
⬜⬜⬜⬜⬜ ⬜🟩🟨🟨⬜
🟨⬜🟨⬜⬜ ⬜⬜⬜⬜⬜
🟨⬜🟩⬜⬜ ⬜⬜⬜⬜🟨
🟩🟩🟩🟩🟩 ⬜⬜⬜⬜⬜
⬛⬛⬛⬛⬛ ⬜🟨⬜🟨🟨
⬛⬛⬛⬛⬛ ⬜🟩⬜🟩🟩
⬛⬛⬛⬛⬛ 🟩🟩🟩🟩🟩
    """
    attempt = QuordleAttemptParser(attempt1)
    attempt_details = attempt.parse()
    attempt.validate_guesses()
    print(attempt.attempt_details)
    print(attempt.errors)