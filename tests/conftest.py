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
    curs.fetchone = MagicMock()
    curs.execute = MagicMock()
    conn.cursor.__enter__ = MagicMock(return_value=curs)
    return Leaderboard(conn)