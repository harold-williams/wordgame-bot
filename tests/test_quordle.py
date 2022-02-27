from freezegun import freeze_time
import pytest
from wordgame_bot.quordle import QourdleAttempt, QuordleAttemptParser

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
    ]
)
def test_parse_valid_attempts(attempt: str, expected_score: int, expected_day: int):
    parser = QuordleAttemptParser(attempt)
    parsed_attempt = parser.parse()
    assert isinstance(parsed_attempt, QourdleAttempt)
    assert parsed_attempt.info.day == expected_day
    assert parsed_attempt.score == expected_score
