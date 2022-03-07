from __future__ import annotations
from contextlib import contextmanager

from unittest.mock import MagicMock, patch

from freezegun import freeze_time
import pytest

from wordgame_bot.wordle import INCORRECT_GUESS_SCORE, WordleAttempt, WordleAttemptParser, WordleGuessInfo
from wordgame_bot.exceptions import InvalidDay, InvalidFormatError, InvalidScore, ParsingError


@contextmanager
def remove_info_validation():
    with patch('wordgame_bot.wordle.WordleGuessInfo.__post_init__'):
        yield

@pytest.mark.parametrize(
    "info",
    [
        ("Wordle 2162 1/6"),
        ("Wordle 248 4/6"),
        ("Wordle 20 X/6"),
    ]
)
def test_valid_info_format_raises_no_error(info: str):
    with remove_info_validation():
        info = WordleGuessInfo(info)
        info.validate_format()

@pytest.mark.parametrize(
    "info",
    [
        (""),
        ("255 3/6"),
        ("XXXXXXXXX 20 X/6"),
        ("XXXXXXXXX 20 12/6"),
        ("Wordle 248 4"),
        ("Wordle 248 -2/6"),
        ("Wordle bad_day_format 5/6"),
    ]
)
def test_invalid_info_format(info: str):
    with remove_info_validation():
        with pytest.raises(InvalidFormatError):
            info = WordleGuessInfo(info)
            info.validate_format()

@pytest.mark.parametrize(
    "info, expected_day, expected_score",
    [
        ("Wordle 2162 1/6", "2162", "1"),
        ("Wordle 248 4/6", "248", "4"),
        ("Wordle 20 X/6", "20", "X"),
    ]
)
def test_extract_day_and_score(info: str, expected_day: int, expected_score: int):
    with remove_info_validation():
        guess_info = WordleGuessInfo(info)
        guess_info.extract_day_and_score()
        assert guess_info.day == expected_day
        assert guess_info.score == expected_score


@pytest.mark.parametrize(
    "guess_num, expected_score",
    [
        (5, 5),
        (0, 10),
        (10, 0),
    ]
)
def test_wordle_attempt(guess_num: int, expected_score: int):
    info_mock = MagicMock(score=guess_num)
    guesses = MagicMock()
    attempt = WordleAttempt(info_mock, guesses)
    assert attempt.score == expected_score

@freeze_time("2021, 6, 25")
@pytest.mark.parametrize(
    "day, expecting_error",
    [
        ("6", False),
        ("5", False),
        (6, False),
        (5, False),
        ("0", True),
        ("140", True),
        (0, True),
        (140, True),
        ("1st Feb", True),
    ]
)
def test_validate_day(day: str | int, expecting_error: bool):
    with remove_info_validation():
        guess_info = WordleGuessInfo("", day=day)
        try:
            guess_info.validate_day()
        except InvalidDay:
            if not expecting_error:
                pytest.fail()

@freeze_time("2021, 6, 25")
@pytest.mark.parametrize(
    "day, expected_day",
    [
        ("6", 6),
        ("5", 5),
        ("0", None),
        ("140", None),
        ("1st Feb", None),
    ]
)
def test_parse_day(day: str, expected_day: int | None):
    with remove_info_validation():
        guess_info = WordleGuessInfo("", day=day)
        try:
            assert guess_info.parse_day() == expected_day
        except InvalidDay:
            if expected_day is not None:
                pytest.fail()

@pytest.mark.parametrize(
    "score, expecting_error",
    [
        ("6", False),
        ("5", False),
        ("4", False),
        ("3", False),
        ("2", False),
        ("1", False),
        ("X", False),
        ("0", True),
        ("7", True),
        ("12", True),
    ]
)
def test_validate_score(score: str, expecting_error: bool):
    with remove_info_validation():
        guess_info = WordleGuessInfo("", score=score)
        try:
            guess_info.validate_score()
        except InvalidScore:
            if not expecting_error:
                pytest.fail()

@pytest.mark.parametrize(
"score, expected_score",
    [
        ("6", 6),
        ("5", 5),
        ("4", 4),
        ("3", 3),
        ("2", 2),
        ("1", 1),
        ("X", INCORRECT_GUESS_SCORE),
        ("0", None),
        ("7", None),
        ("12", None),
    ]
)
def test_parse_score(score: str, expected_score: int | None):
    with remove_info_validation():
        guess_info = WordleGuessInfo("", score=score)
        try:
            assert guess_info.parse_score() == expected_score
        except InvalidScore:
            if expected_score is not None:
                pytest.fail()

@pytest.mark.parametrize(
    "number_lines, expect_error",
    [
        (2, False),
        (4, False),
        (6, False),
        (0, True),
        (1, True),
        (8, True),
        (10, True),
    ]
)
def test_wordle_get_lines(number_lines: int, expect_error: bool):
    info = "\n".join(
        f"line{x}"
        for x in range(number_lines)
    )
    parser = WordleAttemptParser(info)
    try:
        parser.get_lines()
        assert expect_error == False
    except InvalidFormatError:
        assert expect_error == True

@freeze_time("2021, 6, 25")
@pytest.mark.parametrize(
    "attempt, expected_day, expected_score",
    [
        (
            (
                "Wordle 5 4/6\n"
                "⬛⬛⬛🟨⬛\n"
                "🟨🟨⬛🟩⬛\n"
                "⬛🟩🟩🟩🟨\n"
                "🟩🟩🟩🟩🟩\n"
            ),
            5,
            6,
        ),
        (
            (
                "Wordle 5 X/6\n"
                "\n"
                "🟩⬜⬜🟩⬜\n"
                "🟩⬜⬜🟩⬜\n"
                "🟩⬜⬜🟩⬜\n"
                "⬜⬜⬜🟨⬜\n"
                "⬜⬜⬜⬜⬜\n"
                "⬜⬜⬜⬜⬜\n"
            ),
            5,
            2,
        ),
        (
            (
                "Wordle 6 3/6\n"
                "🟩⬛⬛🟨⬛\n"
                "🟩🟩⬛🟩🟩\n"
                "🟩🟩🟩🟩🟩\n"
            ),
            6,
            7,
        ),
        (
            (
                "Wordle 6 6/6\n"
                "⬜⬜⬜⬜⬜\n"
                "⬜⬜⬜🟨⬜\n"
                "🟨⬜⬜⬜🟨\n"
                "⬜🟨🟨🟨🟨\n"
                "🟩🟩🟩⬜🟩\n"
                "🟩🟩🟩🟩🟩\n"
            ),
            6,
            4,
        ),
    ]
)
def test_parse_valid_attempts(attempt: str, expected_score: int, expected_day: int):
    parser = WordleAttemptParser(attempt)
    parsed_attempt = parser.parse()
    assert isinstance(parsed_attempt, WordleAttempt)
    assert parsed_attempt.info.day == expected_day
    assert parsed_attempt.score == expected_score

@freeze_time("2021, 6, 25")
@pytest.mark.parametrize(
    "attempt, expected_error",
    [
        (
            (
                ""
            ),
            InvalidFormatError
        ),
        (
            (
                "Wordle 5 8/6\n"
                "\n"
                "🟩⬜⬜🟩⬜\n"
                "🟩⬜⬜🟩⬜\n"
                "🟩⬜⬜🟩⬜\n"
                "⬜⬜⬜🟨⬜\n"
                "⬜⬜⬜⬜⬜\n"
                "⬜⬜⬜⬜⬜\n"
            ),
            InvalidFormatError
        ),
        (
            (
                "Score: 1000\n"
                "🟩⬛⬛🟨⬛\n"
                "🟩🟩⬛🟩🟩\n"
                "🟩🟩🟩🟩🟩\n"
            ),
            InvalidFormatError
        ),
        (
            (
                "Wordle 8 4/6\n"
                "⬛⬛⬛🟨⬛\n"
                "🟨🟨⬛🟩⬛\n"
                "⬛🟩🟩🟩🟨\n"
                "🟩🟩🟩🟩🟩\n"
            ),
            InvalidDay
        ),
        (
            (
                "Wordle 6 2/6\n"
                "⬜⬜⬜⬜⬜\n"
                "⬜⬜⬜🟨⬜\n"
                "🟨⬜⬜⬜🟨\n"
                "🟩🟩🟩⬜🟩\n"
                "🟩🟩🟩🟩🟩\n"
            ),
            InvalidScore
        ),
    ]
)
def test_parse_invalid_attempts(attempt: str, expected_error: ParsingError):
    parser = WordleAttemptParser(attempt)
    try:
        with pytest.raises(expected_error):
            parser.parse()
    except Exception as e:
        pytest.fail()











# @pytest.mark.parametrize(
#     "tiles",
#     [
#         "🟨🟩⬜⬜🟩",
#         "🟩🟩🟩🟩🟩", 
#         "🟨🟨🟨🟨🟨",
#     ]
# )
# def test_recognise_valid_tiles(parser: WordleAttemptParser, tiles: str):
#     try:
#         parser.validate_tiles(tiles)
#     except InvalidTiles:
#         pytest.fail()

# @pytest.mark.parametrize(
#     "tiles",
#     [
#         "🟨🟨",
#         "🟩🟩🟩🟩🟩🟩",
#         "tiles",
#     ]
# )
# def test_recognise_invalid_tiles(parser: WordleAttemptParser, tiles: str):
#     with pytest.raises(InvalidTiles):
#         parser.validate_tiles(tiles)

