import pytest
from discord import User
from unittest.mock import MagicMock

from wordgame_bot.leaderboard import Leaderboard
from wordgame_bot.wordle import WordleAttemptParser

@pytest.fixture
def parser():
    return WordleAttemptParser("")

@pytest.fixture
def user():
    data = {
        "username": "test",
        "id": 1,
        "discriminator": "test",
        "avatar": None,
    }
    return User(state=None, data=data)

@pytest.fixture
def leaderboard():
    conn = MagicMock()
    curs = MagicMock()
    curs.fetchone  = MagicMock(return_value = None)
    # curs.execute.return_value = None)
    conn.cursor.return_value.__enter__.return_value = curs
    Leaderboard.create_table = MagicMock()
    return Leaderboard(conn)