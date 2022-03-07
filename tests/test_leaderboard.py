from unittest.mock import MagicMock
from wordgame_bot.leaderboard import Leaderboard


def test_verify_valid_user(leaderboard: Leaderboard, user):
    cursor: MagicMock = leaderboard.conn.cursor.__enter__
    print(cursor)
    leaderboard.verify_valid_user(user)
    assert cursor.fetchone.called