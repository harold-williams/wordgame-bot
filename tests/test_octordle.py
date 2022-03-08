import re
import pytest
from freezegun import freeze_time
from wordgame_bot.exceptions import InvalidDay, InvalidFormatError, InvalidScore
from wordgame_bot.octordle import OctordleAttempt, OctordleAttemptParser

YESTERDAY_SUBMISSION = (
    "Daily Octordle #42\n"
    "3️⃣4️⃣\n"
    "🔟🕛\n"
    "2️⃣6️⃣\n"
    "1️⃣7️⃣\n"
    "octordle.com\n"
    "🟨⬜⬜⬜🟨 ⬜🟨⬜⬜⬜\n"
    "⬜🟨⬜⬜🟨 ⬜⬜🟨⬜⬜\n"
    "🟩🟩🟩🟩🟩 🟩⬜⬜⬜⬜\n"
    "⬛⬛⬛⬛⬛ 🟩🟩🟩🟩🟩\n"
    "\n"
    "⬜⬜⬜🟨⬜ 🟨⬜⬜⬜🟨\n"
    "⬜⬜⬜🟨⬜ ⬜⬜⬜⬜🟨\n"
    "⬜⬜⬜⬜🟨 ⬜🟨⬜🟨⬜\n"
    "⬜⬜🟨⬜⬜ ⬜⬜⬜⬜🟩\n"
    "⬜⬜⬜⬜⬜ ⬜⬜⬜⬜⬜\n"
    "⬜⬜⬜⬜⬜ ⬜⬜⬜⬜⬜\n"
    "⬜⬜⬜⬜⬜ ⬜⬜⬜🟨⬜\n"
    "🟨🟨🟨⬜⬜ ⬜⬜⬜⬜⬜\n"
    "🟩⬜🟩⬜⬜ 🟨⬜⬜⬜🟨\n"
    "🟩🟩🟩🟩🟩 🟨⬜⬜⬜⬜\n"
    "⬛⬛⬛⬛⬛ 🟨🟩🟩🟨🟩\n"
    "⬛⬛⬛⬛⬛ 🟩🟩🟩🟩🟩\n"
    "\n"
    "⬜⬜🟩🟩🟩 ⬜🟨⬜⬜⬜\n"
    "🟩🟩🟩🟩🟩 ⬜🟨🟨⬜⬜\n"
    "⬛⬛⬛⬛⬛ 🟩⬜🟨⬜⬜\n"
    "⬛⬛⬛⬛⬛ 🟩⬜⬜🟩⬜\n"
    "⬛⬛⬛⬛⬛ 🟩🟩🟨🟩⬜\n"
    "⬛⬛⬛⬛⬛ 🟩🟩🟩🟩🟩\n"
    "\n"
    "🟩🟩🟩🟩🟩 🟨🟨🟨⬜⬜\n"
    "⬛⬛⬛⬛⬛ ⬜🟩🟨⬜⬜\n"
    "⬛⬛⬛⬛⬛ ⬜⬜🟨🟩⬜\n"
    "⬛⬛⬛⬛⬛ ⬜⬜⬜🟨⬜\n"
    "⬛⬛⬛⬛⬛ ⬜⬜🟨🟨🟩\n"
    "⬛⬛⬛⬛⬛ ⬜⬜⬜🟨🟨\n"
    "⬛⬛⬛⬛⬛ 🟩🟩🟩🟩🟩"
)

TODAY_SUBMISSION = (
    "Daily Octordle #43\n"
    "5️⃣🕐\n"
    "🟥🟥\n"
    "9️⃣7️⃣\n"
    "🔟🕚\n"
    "octordle.com\n"
    "⬜🟨🟨⬜🟨 ⬜⬜⬜⬜🟨\n"
    "🟩⬜🟨🟨🟨 🟩⬜⬜⬜⬜\n"
    "🟩🟨🟨🟨⬜ 🟩⬜⬜⬜⬜\n"
    "🟩⬜🟩🟩🟩 🟩⬜⬜⬜⬜\n"
    "🟩🟩🟩🟩🟩 🟩⬜⬜⬜⬜\n"
    "⬛⬛⬛⬛⬛ 🟩⬜⬜🟨⬜\n"
    "⬛⬛⬛⬛⬛ 🟩⬜⬜🟩⬜\n"
    "⬛⬛⬛⬛⬛ ⬜🟨⬜⬜⬜\n"
    "⬛⬛⬛⬛⬛ ⬜⬜🟨⬜⬜\n"
    "⬛⬛⬛⬛⬛ ⬜🟨⬜⬜⬜\n"
    "⬛⬛⬛⬛⬛ 🟨⬜⬜⬜⬜\n"
    "⬛⬛⬛⬛⬛ 🟩🟩🟩🟩⬜\n"
    "⬛⬛⬛⬛⬛ 🟩🟩🟩🟩🟩\n"
    "\n"
    "⬜🟩⬜🟨⬜ ⬜⬜🟩⬜⬜\n"
    "⬜🟨⬜🟨⬜ ⬜🟨🟩⬜⬜\n"
    "⬜⬜🟨⬜⬜ ⬜🟨⬜⬜⬜\n"
    "⬜⬜⬜⬜🟨 ⬜⬜⬜🟨⬜\n"
    "⬜⬜⬜⬜🟨 ⬜🟨⬜🟨⬜\n"
    "⬜⬜🟩⬜⬜ ⬜⬜⬜🟨⬜\n"
    "⬜⬜⬜⬜⬜ ⬜⬜⬜⬜⬜\n"
    "⬜⬜⬜🟨⬜ ⬜⬜⬜⬜🟨\n"
    "⬜⬜⬜🟨⬜ ⬜⬜⬜⬜🟨\n"
    "⬜⬜⬜🟨⬜ 🟨⬜⬜⬜🟨\n"
    "⬜⬜⬜⬜⬜ ⬜⬜⬜🟨⬜\n"
    "⬜⬜🟨⬜⬜ ⬜🟨⬜⬜⬜\n"
    "⬜⬜🟨⬜⬜ ⬜⬜⬜⬜🟩\n"
    "\n"
    "⬜⬜⬜⬜⬜ ⬜⬜⬜⬜🟨\n"
    "⬜⬜⬜⬜🟨 🟩⬜⬜⬜🟩\n"
    "⬜⬜⬜🟨⬜ 🟩⬜⬜🟨⬜\n"
    "⬜⬜🟨⬜⬜ 🟩🟩🟨⬜⬜\n"
    "⬜🟨🟨⬜⬜ 🟩⬜🟨⬜⬜\n"
    "⬜⬜🟨⬜🟨 🟩🟩⬜⬜🟩\n"
    "⬜⬜⬜🟨🟨 🟩🟩🟩🟩🟩\n"
    "🟨🟨🟨🟩🟩 ⬛⬛⬛⬛⬛\n"
    "🟩🟩🟩🟩🟩 ⬛⬛⬛⬛⬛\n"
    "\n"
    "⬜⬜🟨⬜⬜ ⬜⬜🟨⬜⬜\n"
    "⬜⬜🟨⬜⬜ ⬜⬜🟨⬜🟨\n"
    "⬜🟨⬜⬜⬜ ⬜🟨⬜🟨⬜\n"
    "⬜⬜⬜🟨⬜ ⬜⬜🟨🟩⬜\n"
    "⬜🟨⬜🟨⬜ ⬜⬜🟨🟩⬜\n"
    "⬜⬜🟨⬜⬜ ⬜⬜⬜⬜🟨\n"
    "⬜⬜⬜🟨⬜ ⬜⬜⬜🟨🟨\n"
    "⬜🟩⬜🟩🟩 🟨🟨⬜⬜⬜\n"
    "⬜⬜🟩🟩🟩 ⬜🟩🟨⬜⬜\n"
    "🟩🟩🟩🟩🟩 🟨🟨🟨⬜⬜\n"
    "⬛⬛⬛⬛⬛ 🟩🟩🟩🟩🟩"
)

@freeze_time("2022, 3, 8")
@pytest.mark.parametrize(
    "attempt, expected_day, expected_score",
    [
        (
            TODAY_SUBMISSION,
            43,
            35,
        ),
        (
            YESTERDAY_SUBMISSION,
            42,
            76,
        ),
    ]
)
def test_parse_valid_attempts(attempt: str, expected_score: int, expected_day: int):
    parser = OctordleAttemptParser(attempt)
    parsed_attempt = parser.parse()
    assert isinstance(parsed_attempt, OctordleAttempt)
    assert parsed_attempt.info.day == expected_day
    assert parsed_attempt.score == expected_score

def replace_day(submission: str, new_day: str):
    return re.sub("#[0-9]+\n", f"#{new_day}\n", submission)

def replace_score(submission: str, new_scores: str):
    submission_lines = submission.split("\n")
    valid_tiles = ("🟩🟨⬜⬛")
    new_submission = submission_lines[0:1] + new_scores
    for line_num, line in enumerate(submission_lines[1:]):
        if any(tile in line for tile in valid_tiles):
            break
    new_submission += submission_lines[line_num:]
    print(new_submission)
    return "\n".join(new_submission)

@freeze_time("2022, 3, 8")
@pytest.mark.parametrize(
    "attempt, expected_error",
    [
        (
            replace_day(TODAY_SUBMISSION, 5),
            InvalidDay
        ),
        (
            replace_score(TODAY_SUBMISSION, ["5️⃣6️⃣", "8️⃣7️⃣", "🟥🟥", "🟥🟥"]),
            InvalidScore,
        ),
        (
            replace_score(TODAY_SUBMISSION, ["6️⃣6️⃣", "6️⃣6️⃣", "6️⃣6️⃣", "6️⃣6️⃣"]),
            InvalidScore,
        ),
        (
            replace_score(TODAY_SUBMISSION, ["6️⃣6️⃣6️⃣6️⃣6️⃣6️⃣6️⃣6️⃣"]),
            InvalidFormatError
        ),
        (
            TODAY_SUBMISSION[:40],
            InvalidFormatError
        ),
    ]
)
def test_parse_invalid_attempts(attempt: str, expected_error: Exception):
    parser = OctordleAttemptParser(attempt)
    with pytest.raises(expected_error):
        parser.parse()
