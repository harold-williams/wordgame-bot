from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
import psycopg2
from discord import User
from wordgame_bot.leaderboard import CREATE_TABLE_SCHEMA, LEADERBOARD_SCHEMA, AttemptDuplication, Leaderboard, Score, connect_to_leaderboard
from wordgame_bot.octordle import OctordleAttempt
from wordgame_bot.quordle import QuordleAttempt
from wordgame_bot.wordle import WordleAttempt

def test_create_table_on_instantiation():
    leaderboard = Leaderboard(MagicMock())
    mocked_cursor: MagicMock = leaderboard.conn.cursor.return_value.__enter__.return_value
    execute: MagicMock = mocked_cursor.execute
    execute.assert_called_once_with(CREATE_TABLE_SCHEMA)

def test_verify_new_user(leaderboard: Leaderboard, user: User):
    mocked_cursor: MagicMock = leaderboard.conn.cursor.return_value.__enter__.return_value
    execute: MagicMock = mocked_cursor.execute
    fetchone: MagicMock = mocked_cursor.fetchone
    fetchone.return_value = None
    leaderboard.verify_valid_user(user)
    fetchone.assert_called_once()
    execute.assert_any_call(
        f"SELECT * FROM users WHERE user_id = {user.id}"
    )
    execute.assert_any_call(
        f"INSERT INTO users(user_id, username) VALUES ({user.id}, {user.name})"
    )

def test_verify_preexisting_user(leaderboard: Leaderboard, user: User):
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

@pytest.mark.parametrize(
    "attempt",
    [
        QuordleAttempt(
            info = MagicMock(day = 5, score = 10),
            guesses = MagicMock()
        ),
        WordleAttempt(
            info = MagicMock(day = 5, score = 2),
            guesses = MagicMock()
        ),
        OctordleAttempt(
            info = MagicMock(day = 5, score = 2),
            guesses = MagicMock()
        ),
    ]
)
def test_insert_valid_submission(leaderboard: Leaderboard, user: User, attempt):
    mocked_cursor: MagicMock = leaderboard.conn.cursor.return_value.__enter__.return_value
    execute: MagicMock = mocked_cursor.execute
    leaderboard.verify_valid_user = MagicMock()
    leaderboard.insert_submission(attempt, user)
    execute.assert_called_once_with(
        "INSERT INTO attempts(user_id, mode, day, score) "
        "VALUES ("
            f"{user.id},"
            f"{attempt.gamemode},"
            f"{attempt.info.day},"
            f"{attempt.score}"
        ")"
    )

@pytest.mark.parametrize(
    "attempt",
    [
        QuordleAttempt(
            info = MagicMock(day = 5, score = 10),
            guesses = MagicMock()
        ),
        WordleAttempt(
            info = MagicMock(day = 5, score = 2),
            guesses = MagicMock()
        ),
        OctordleAttempt(
            info = MagicMock(day = 5, score = 2),
            guesses = MagicMock()
        ),
    ]
)
def test_insert_invalid_submission(leaderboard: Leaderboard, user: User, attempt):
    mocked_cursor: MagicMock = leaderboard.conn.cursor.return_value.__enter__.return_value
    execute: MagicMock = mocked_cursor.execute
    execute.side_effect = psycopg2.errors.UniqueViolation
    leaderboard.verify_valid_user = MagicMock()
    with pytest.raises(AttemptDuplication) as duplication_error:
        leaderboard.insert_submission(attempt, user)
    execute.assert_called_once_with(
        "INSERT INTO attempts(user_id, mode, day, score) "
        "VALUES ("
            f"{user.id},"
            f"{attempt.gamemode},"
            f"{attempt.info.day},"
            f"{attempt.score}"
        ")"
    )
    assert duplication_error.value.username == user.name
    assert duplication_error.value.day == attempt.info.day

@patch("wordgame_bot.leaderboard.psycopg2.connect")
def test_successful_connect_to_leaderboard(connect: MagicMock):
    mock_conn = MagicMock()
    connect.return_value = mock_conn

    with connect_to_leaderboard() as leaderboard:
        connect.assert_called_once()
        assert leaderboard.conn == mock_conn
        mock_conn.close.assert_not_called()

    mock_conn.close.assert_called_once()

@patch("wordgame_bot.leaderboard.psycopg2.connect")
def test_error_connecting_to_leaderboard(connect: MagicMock):
    mock_conn = MagicMock()
    connect.return_value = mock_conn
    Leaderboard.__init__ = MagicMock(side_effect = Exception)
    with pytest.raises(Exception):
        with connect_to_leaderboard() as leaderboard:
            pass
    connect.assert_called_once()
    mock_conn.close.assert_called_once()
