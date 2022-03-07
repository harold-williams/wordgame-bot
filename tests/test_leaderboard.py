from unittest.mock import MagicMock
from wordgame_bot.leaderboard import Leaderboard


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

def test_get_ranks_table(leaderboard: Leaderboard):
    leaderboard.scores = [
        ("User1", 4),
        ("User2", 7),
        ("User3", 12),
        ("User4", 0),
    ]
    ranks_table = (
        "🥇. User3 -- 12\n"
        "🥈. User2 -- 7\n"
        "🥉. User1 -- 4\n"
        "4. User4 -- 0"
    )
    assert leaderboard.get_ranks_table() == ranks_table