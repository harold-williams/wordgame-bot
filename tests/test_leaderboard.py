from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from wordgame_bot.leaderboard import LEADERBOARD_SCHEMA, Leaderboard, Score


def test_verify_new_user(leaderboard: Leaderboard, user):
    mocked_cursor: MagicMock = leaderboard.conn.cursor.return_value.__enter__.return_value
    execute: MagicMock = mocked_cursor.execute
    fetchone: MagicMock = mocked_cursor.fetchone
    leaderboard.verify_valid_user(user)
    fetchone.assert_called_once()
    execute.assert_any_call(
        f"SELECT * FROM users WHERE user_id = {user.id}"
    )
    execute.assert_any_call(
        f"INSERT INTO users(user_id, username) VALUES ({user.id}, {user.name})"
    )

def test_verify_preexisting_user(leaderboard: Leaderboard, user):
    mocked_cursor: MagicMock = leaderboard.conn.cursor.return_value.__enter__.return_value
    execute: MagicMock = mocked_cursor.execute
    fetchone: MagicMock = mocked_cursor.fetchone
    fetchone.return_value = (user.id, user.name)
    leaderboard.verify_valid_user(user)
    execute.assert_called_once_with(
        f"SELECT * FROM users WHERE user_id = {user.id}"
    )
    fetchone.assert_called_once()

@pytest.mark.parametrize(
    "retrieved",
    [
        [
            ("User1", 2),
            ("User2", 4),
        ],
        [],
    ]
)
def test_retrieve_scores(leaderboard: Leaderboard, retrieved: list[Score]):
    mocked_cursor: MagicMock = leaderboard.conn.cursor.return_value.__enter__.return_value
    execute: MagicMock = mocked_cursor.execute
    execute.return_value = retrieved
    leaderboard.retrieve_scores()
    execute.assert_called_once_with(LEADERBOARD_SCHEMA)
    assert leaderboard.scores == retrieved

@pytest.mark.parametrize(
    "scores, expected_ranks",
    [
        (
            [
                ("User1", 4),
                ("User2", 7),
                ("User3", 12),
                ("User4", 0),
            ],
            (
                "🥇. User3 -- 12\n"
                "🥈. User2 -- 7\n"
                "🥉. User1 -- 4\n"
                "4. User4 -- 0"
            ),
        ),
        (
            [
                ("User1", 4),
                ("User2", 7),
                ("User3", 7),
            ],
            (
                "🥇. User2 -- 7\n"
                "🥈. User3 -- 7\n"
                "🥉. User1 -- 4"
            ),
        ),
        (
            [],
            "",
        ),
    ]
)
def test_get_ranks_table(leaderboard: Leaderboard, scores: list[Score], expected_ranks: str):
    leaderboard.scores = scores
    assert leaderboard.get_ranks_table() == expected_ranks

# @pytest.mark.parametrize(
#     "scores",
#     [

#     ]
# )
def test_get_leaderboard(leaderboard: Leaderboard):
    leaderboard.retrieve_scores = MagicMock()
    leaderboard.get_ranks_table = MagicMock(return_value = "ranks_mock")
    leaderboard_embed = leaderboard.get_leaderboard()
    leaderboard_contents = leaderboard_embed.to_dict()
    fields = leaderboard_contents.get("fields", [])
    assert len(fields) == 1
    assert fields[0] == {
        'inline': False,
        'name': 'Ranks',
        'value': 'ranks_mock'
    }
    assert leaderboard_contents.get("title", "") == "🏆 Leaderboard 🏆"