from __future__ import annotations
from unittest.mock import MagicMock

import pytest
from wordgame_bot.wordle import INCORRECT_GUESS_SCORE, WordleAttemptParser
from wordgame_bot.exceptions import InvalidDay, InvalidFormatError, InvalidScore, InvalidTiles

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
    parser = WordleAttemptParser(
        "\n".join(f"line{x}" for x in range(number_lines))
    )
    try:
        info, tiles = parser.get_lines()
        assert info == "line0"
        assert tiles == [f"line{x}" for x in range(1,number_lines)]
        assert tiles != []
        assert expect_error == False

    except InvalidFormatError:
        assert expect_error == True

@pytest.mark.parametrize(
    "info, expected",
    [
        ("Wordle 2162 1/6", (2162, 1)),
        ("Wordle 248 4/6", (248, 4)),
        ("Wordle 20 X/6", (20, INCORRECT_GUESS_SCORE)),
    ]
)
def test_parse_valid_info(parser: WordleAttemptParser, info: str, expected: tuple[int, int]):
    parser.validate_day = MagicMock()
    result = parser.parse_info(info)
    assert result == expected

@pytest.mark.parametrize(
    "info, error, error_details",
    [
        ("XXXXXXXXX 20 X/6", InvalidFormatError, "XXXXXXXXX 20 X/6"),
        ("", InvalidFormatError, ""),
        ("Wordle 248 4", InvalidScore, "4"),
        ("Wordle 248 -2/6", InvalidScore, "-2"),
        ("Wordle bad_day_format 5/6", InvalidDay, "bad_day_format"),
    ]
)
def test_parse_info_raises(
    parser: WordleAttemptParser,
    info: str,
    error: type[Exception],
    error_details: str
):
    parser.validate_day = MagicMock()
    with pytest.raises(error) as e:
        parser.parse_info(info)
    
    assert error_details in e.value.message




# TODO: validate_day



@pytest.mark.parametrize(
    "score, expected_score",
    [
        (4, 6),
        (0, 10),
        (10, 0),
    ]
)
def test_convert_valid_score(parser: WordleAttemptParser, score: int, expected_score: int):
    converted_score = parser.convert_score(score)
    assert converted_score == expected_score

@pytest.mark.parametrize(
    "score",
    [
        12,
        -5,
    ]
)
def test_convert_valid_score(parser: WordleAttemptParser, score: int):
    with pytest.raises(InvalidScore) as error:
        parser.convert_score(score)
    
    assert str(score) in error.value.message

@pytest.mark.parametrize(
    "tiles",
    [
        "🟨🟩⬜⬜🟩",
        "🟩🟩🟩🟩🟩", 
        "🟨🟨🟨🟨🟨",
    ]
)
def test_recognise_valid_tiles(parser: WordleAttemptParser, tiles: str):
    try:
        parser.validate_tiles(tiles)
    except InvalidTiles:
        pytest.fail()

@pytest.mark.parametrize(
    "tiles",
    [
        "🟨🟨",
        "🟩🟩🟩🟩🟩🟩",
        "tiles",
    ]
)
def test_recognise_invalid_tiles(parser: WordleAttemptParser, tiles: str):
    with pytest.raises(InvalidTiles):
        parser.validate_tiles(tiles)

@pytest.mark.parametrize(
"attempt, expected_day, expected_score",
[
    (
        (
            "Wordle 248 4/6\n"
            "⬛⬛⬛🟨⬛\n"
            "🟨🟨⬛🟩⬛\n"
            "⬛🟩🟩🟩🟨\n"
            "🟩🟩🟩🟩🟩\n"
        ),
        248,
        4,
    ),
    (
        (
            "Wordle 242 X/6\n"
            "\n"
            "🟩⬜⬜🟩⬜\n"
            "🟩⬜⬜🟩⬜\n"
            "🟩⬜⬜🟩⬜\n"
            "⬜⬜⬜🟨⬜\n"
            "⬜⬜⬜⬜⬜\n"
            "⬜⬜⬜⬜⬜\n"
        ),
        242,
        INCORRECT_GUESS_SCORE,
    ),
    (
        (
            "Wordle 221 3/6\n"
            "🟩⬛⬛🟨⬛\n"
            "🟩🟩⬛🟩🟩\n"
            "🟩🟩🟩🟩🟩\n"
        ),
        221,
        3,
    )
]
)
def test_parse_valid_attempts(parser: WordleAttemptParser, attempt: str, expected_score: int, expected_day: int):
    parser.validate_day = MagicMock()

    parser.attempt = attempt
    parsed_attempt = parser.parse_attempt()
    assert isinstance(parsed_attempt.guess, WordleGuess)
    assert parsed_attempt.day == expected_day
    assert parsed_attempt.guess.score == expected_score
