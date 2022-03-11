from __future__ import annotations

from contextlib import contextmanager
from unittest.mock import patch

import pytest
from freezegun import freeze_time

from wordgame_bot.exceptions import (
    InvalidDay, InvalidFormatError,
    InvalidScore,
)
from wordgame_bot.quordle import (
    INCORRECT_GUESS_SCORE, QuordleAttempt,
    QuordleAttemptParser, QuordleGuessInfo,
)


@contextmanager
def remove_info_validation():
    with patch("wordgame_bot.quordle.QuordleGuessInfo.__post_init__"):
        yield


@freeze_time("2022, 2, 10")
@pytest.mark.parametrize(
    "attempt, expected_day, expected_score",
    [
        (
            (
                "Daily Quordle #17\n"
                "5️⃣6️⃣\n"
                "8️⃣7️⃣\n"
                "quordle.com\n"
                "🟩🟨⬜⬜🟨 ⬜⬜🟨⬜🟨\n"
                "⬜🟨🟩⬜⬜ ⬜🟨⬜⬜⬜\n"
                "⬜⬜⬜🟨⬜ ⬜⬜⬜⬜🟨\n"
                "🟨⬜⬜🟩⬜ ⬜🟩🟨🟩🟨\n"
                "🟩🟩🟩🟩🟩 ⬜⬜⬜🟩⬜\n"
                "⬛⬛⬛⬛⬛ 🟩🟩🟩🟩🟩\n"
                "\n"
                "⬜⬜⬜⬜🟨 ⬜⬜⬜⬜⬜\n"
                "⬜🟩⬜⬜🟩 ⬜⬜⬜🟩⬜\n"
                "⬜⬜⬜🟩⬜ ⬜⬜⬜⬜⬜\n"
                "⬜⬜⬜🟨⬜ 🟩⬜⬜⬜⬜\n"
                "⬜🟨⬜🟨⬜ ⬜⬜⬜⬜🟨\n"
                "⬜⬜⬜🟨⬜ ⬜⬜⬜⬜🟩\n"
                "⬜⬜🟨⬜⬜ 🟩🟩🟩🟩🟩\n"
                "🟩🟩🟩🟩🟩 ⬛⬛⬛⬛⬛"
            ),
            17,
            25,
        ),
        (
            (
                "Daily Quordle #17\n"
                "6️⃣9️⃣\n"
                "🟥8️⃣\n"
                "quordle.com\n"
                "⬜⬜⬜🟨⬜ ⬜⬜⬜⬜🟨\n"
                "🟨🟨⬜⬜⬜ ⬜🟨⬜🟨⬜\n"
                "⬜⬜🟨⬜⬜ ⬜🟩⬜⬜⬜\n"
                "⬜⬜🟨⬜⬜ ⬜⬜⬜⬜🟩\n"
                "🟨🟨🟩🟩🟨 ⬜⬜⬜🟨⬜\n"
                "🟩🟩🟩🟩🟩 ⬜⬜⬜🟨⬜\n"
                "⬛⬛⬛⬛⬛ ⬜⬜⬜⬜🟨\n"
                "⬛⬛⬛⬛⬛ ⬜🟨⬜🟨⬜\n"
                "⬛⬛⬛⬛⬛ 🟩🟩🟩🟩🟩\n"
                "\n"
                "⬜⬜🟨⬜⬜ ⬜⬜⬜🟨⬜\n"
                "⬜🟨⬜⬜🟨 ⬜🟨🟨🟨⬜\n"
                "⬜⬜⬜⬜⬜ ⬜⬜⬜⬜⬜\n"
                "⬜⬜⬜🟨⬜ ⬜🟩⬜⬜⬜\n"
                "⬜⬜⬜🟨⬜ ⬜🟨⬜🟩⬜\n"
                "⬜⬜⬜🟨⬜ 🟨⬜⬜🟩⬜\n"
                "⬜⬜⬜⬜⬜ 🟩🟨⬜🟨⬜\n"
                "⬜⬜⬜🟨⬜ 🟩🟩🟩🟩🟩\n"
                "⬜⬜🟩⬜⬜ ⬛⬛⬛⬛⬛"
            ),
            17,
            16,
        ),
        (
            (
                "Daily Quordle #17\n"
                "4️⃣🟥\n"
                "5️⃣8️⃣\n"
                "quordle.com\n"
                "🟨⬜⬜🟩🟩 ⬜⬜⬜⬜🟨\n"
                "⬜🟨⬜⬜🟨 🟩🟨⬜🟨🟩\n"
                "🟩🟩⬜⬜⬜ ⬜🟨⬜⬜🟨\n"
                "🟩🟩🟩🟩🟩 ⬜🟨⬜⬜🟨\n"
                "⬛⬛⬛⬛⬛ ⬜⬜⬜⬜⬜\n"
                "⬛⬛⬛⬛⬛ ⬜🟩🟨🟩⬜\n"
                "⬛⬛⬛⬛⬛ ⬜🟨🟨⬜⬜\n"
                "⬛⬛⬛⬛⬛ ⬜🟨🟨⬜⬜\n"
                "⬛⬛⬛⬛⬛ 🟩🟩⬜🟩🟩\n"
                "\n"
                "🟨⬜⬜⬜⬜ ⬜⬜⬜⬜🟨\n"
                "⬜⬜⬜⬜⬜ ⬜🟩🟨🟨⬜\n"
                "🟨⬜🟨⬜⬜ ⬜⬜⬜⬜⬜\n"
                "🟨⬜🟩⬜⬜ ⬜⬜⬜⬜🟨\n"
                "🟩🟩🟩🟩🟩 ⬜⬜⬜⬜⬜\n"
                "⬛⬛⬛⬛⬛ ⬜🟨⬜🟨🟨\n"
                "⬛⬛⬛⬛⬛ ⬜🟩⬜🟩🟩\n"
                "⬛⬛⬛⬛⬛ 🟩🟩🟩🟩🟩"
            ),
            17,
            22,
        ),
    ],
)
def test_parse_valid_attempts(attempt: str, expected_score: int, expected_day: int):
    parser = QuordleAttemptParser(attempt)
    parsed_attempt = parser.parse()
    assert isinstance(parsed_attempt, QuordleAttempt)
    assert parsed_attempt.info.day == expected_day
    assert parsed_attempt.score == expected_score


@freeze_time("2022, 2, 10")
@pytest.mark.parametrize(
    "attempt, expected_error",
    [
        (
            (
                "Daily Quordle #24\n"
                "5️⃣6️⃣\n"
                "8️⃣7️⃣\n"
                "quordle.com\n"
                "🟩🟨⬜⬜🟨 ⬜⬜🟨⬜🟨\n"
                "⬜🟨🟩⬜⬜ ⬜🟨⬜⬜⬜\n"
                "⬜⬜⬜🟨⬜ ⬜⬜⬜⬜🟨\n"
                "🟨⬜⬜🟩⬜ ⬜🟩🟨🟩🟨\n"
                "🟩🟩🟩🟩🟩 ⬜⬜⬜🟩⬜\n"
                "⬛⬛⬛⬛⬛ 🟩🟩🟩🟩🟩\n"
                "\n"
                "⬜⬜⬜⬜🟨 ⬜⬜⬜⬜⬜\n"
                "⬜🟩⬜⬜🟩 ⬜⬜⬜🟩⬜\n"
                "⬜⬜⬜🟩⬜ ⬜⬜⬜⬜⬜\n"
                "⬜⬜⬜🟨⬜ 🟩⬜⬜⬜⬜\n"
                "⬜🟨⬜🟨⬜ ⬜⬜⬜⬜🟨\n"
                "⬜⬜⬜🟨⬜ ⬜⬜⬜⬜🟩\n"
                "⬜⬜🟨⬜⬜ 🟩🟩🟩🟩🟩\n"
                "🟩🟩🟩🟩🟩 ⬛⬛⬛⬛⬛"
            ),
            InvalidDay,
        ),
        (
            (
                "Daily Quordle #17\n"
                "8️⃣8️⃣\n"
                "8️⃣8️⃣\n"
                "quordle.com\n"
                "⬜⬜⬜🟨⬜ ⬜⬜⬜⬜🟨\n"
                "🟨🟨⬜⬜⬜ ⬜🟨⬜🟨⬜\n"
                "⬜⬜🟨⬜⬜ ⬜🟩⬜⬜⬜\n"
                "⬜⬜🟨⬜⬜ ⬜⬜⬜⬜🟩\n"
                "🟨🟨🟩🟩🟨 ⬜⬜⬜🟨⬜\n"
                "🟩🟩🟩🟩🟩 ⬜⬜⬜🟨⬜\n"
                "⬛⬛⬛⬛⬛ ⬜⬜⬜⬜🟨\n"
                "⬛⬛⬛⬛⬛ ⬜🟨⬜🟨⬜\n"
                "⬛⬛⬛⬛⬛ 🟩🟩🟩🟩🟩\n"
                "\n"
                "⬜⬜🟨⬜⬜ ⬜⬜⬜🟨⬜\n"
                "⬜🟨⬜⬜🟨 ⬜🟨🟨🟨⬜\n"
                "⬜⬜⬜⬜⬜ ⬜⬜⬜⬜⬜\n"
                "⬜⬜⬜🟨⬜ ⬜🟩⬜⬜⬜\n"
                "⬜⬜⬜🟨⬜ ⬜🟨⬜🟩⬜\n"
                "⬜⬜⬜🟨⬜ 🟨⬜⬜🟩⬜\n"
                "⬜⬜⬜⬜⬜ 🟩🟨⬜🟨⬜\n"
                "⬜⬜⬜🟨⬜ 🟩🟩🟩🟩🟩\n"
                "⬜⬜🟩⬜⬜ ⬛⬛⬛⬛⬛"
            ),
            InvalidScore,
        ),
        (
            (
                "Daily Quordle #17\n"
                "5️⃣6️⃣\n"
                "8️⃣7️⃣\n"
                "quordle.com\n"
                "⬜⬜🟨⬜⬜ ⬜⬜⬜🟨⬜\n"
                "⬜🟨⬜⬜🟨 ⬜🟨🟨🟨⬜\n"
                "⬜⬜⬜⬜⬜ ⬜⬜⬜⬜⬜\n"
                "⬜⬜⬜🟨⬜ ⬜🟩⬜⬜⬜\n"
                "⬜⬜⬜🟨⬜ ⬜🟨⬜🟩⬜\n"
                "⬜⬜⬜🟨⬜ 🟨⬜⬜🟩⬜\n"
                "⬜⬜⬜⬜⬜ 🟩🟨⬜🟨⬜\n"
                "⬜⬜⬜🟨⬜ 🟩🟩🟩🟩🟩\n"
                "⬜⬜🟩⬜⬜ ⬛⬛⬛⬛⬛\n"
                "\n"
                "⬜⬜🟨⬜⬜ ⬜⬜⬜🟨⬜\n"
                "⬜🟨⬜⬜🟨 ⬜🟨🟨🟨⬜\n"
                "⬜⬜⬜⬜⬜ ⬜⬜⬜⬜⬜\n"
                "⬜⬜⬜🟨⬜ ⬜🟩⬜⬜⬜\n"
                "⬜⬜⬜🟨⬜ ⬜🟨⬜🟩⬜\n"
                "⬜⬜⬜🟨⬜ 🟨⬜⬜🟩⬜\n"
                "⬜⬜⬜⬜⬜ 🟩🟨⬜🟨⬜\n"
                "⬜⬜⬜🟨⬜ 🟩🟩🟩🟩🟩\n"
                "⬜⬜🟩⬜⬜ ⬛⬛⬛⬛⬛"
            ),
            InvalidScore,
        ),
        (
            (
                "Daily Quordle #17\n"
                "4️⃣4️⃣4️⃣4️⃣\n"
                "🟨⬜⬜🟩🟩 ⬜⬜⬜⬜🟨\n"
                "⬜🟨⬜⬜🟨 🟩🟨⬜🟨🟩\n"
                "🟩🟩⬜⬜⬜ ⬜🟨⬜⬜🟨\n"
                "🟩🟩🟩🟩🟩 ⬜🟨⬜⬜🟨\n"
                "⬛⬛⬛⬛⬛ ⬜⬜⬜⬜⬜\n"
                "⬛⬛⬛⬛⬛ ⬜🟩🟨🟩⬜\n"
                "⬛⬛⬛⬛⬛ ⬜🟨🟨⬜⬜\n"
                "⬛⬛⬛⬛⬛ ⬜🟨🟨⬜⬜\n"
                "⬛⬛⬛⬛⬛ 🟩🟩⬜🟩🟩\n"
                "\n"
                "🟨⬜⬜⬜⬜ ⬜⬜⬜⬜🟨\n"
                "⬜⬜⬜⬜⬜ ⬜🟩🟨🟨⬜\n"
                "🟨⬜🟨⬜⬜ ⬜⬜⬜⬜⬜\n"
                "🟨⬜🟩⬜⬜ ⬜⬜⬜⬜🟨\n"
                "🟩🟩🟩🟩🟩 ⬜⬜⬜⬜⬜\n"
                "⬛⬛⬛⬛⬛ ⬜🟨⬜🟨🟨\n"
                "⬛⬛⬛⬛⬛ ⬜🟩⬜🟩🟩\n"
                "⬛⬛⬛⬛⬛ 🟩🟩🟩🟩🟩"
            ),
            InvalidFormatError,
        ),
        (("Daily Quordle #17\n" "5️⃣6️⃣\n" "8️⃣7️⃣\n"), InvalidFormatError),
    ],
)
def test_parse_invalid_attempts(attempt: str, expected_error: Exception):
    parser = QuordleAttemptParser(attempt)
    with pytest.raises(expected_error):
        parser.parse()


@freeze_time("2022, 2, 10")
@pytest.mark.parametrize(
    "day, expected_day",
    [
        ("17", 17),
        ("16", 16),
        ("0", None),
        ("140", None),
        ("1st Feb", None),
    ],
)
def test_parse_day(day: str, expected_day: int | None):
    with remove_info_validation():
        guess_info = QuordleGuessInfo("", day=day)
        try:
            assert guess_info.parse_day() == expected_day
        except InvalidDay:
            assert expected_day is None


@pytest.mark.parametrize(
    "scores, expected_score",
    [
        (["8", "2", "4", "7"], 20),
        (["6", "3", "5", "7"], 20),
        (["🟥", "2", "4", "7"], 24),
        (["3", "2"], None),
        (["1", "1", "1", "1"], None),
        (["X", "X", "X", "X"], None),
    ],
)
def test_parse_score(scores: list[str], expected_score: int | None):
    with remove_info_validation():
        guess_info = QuordleGuessInfo("", scores=scores)
        try:
            assert guess_info.parse_score() == expected_score
        except InvalidScore:
            assert expected_score is None
